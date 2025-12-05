from typing import Optional, List, Dict, Any
from contextlib import AsyncExitStack
import traceback
import json
import os
from datetime import datetime

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from utils.logger import logger

import google.generativeai as genai


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        # Configure Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.llm = genai.GenerativeModel("gemini-2.5-pro")

        self.tools = []
        self.conversation_history = []
        self.logger = logger
        self.chat_session = None

    # CONNECT TO SERVER
    async def connect_to_server(self, server_script_path: str) -> bool:
        try:
            is_python = server_script_path.endswith(".py")
            is_js = server_script_path.endswith(".js")

            if not (is_python or is_js):
                raise ValueError("Server script must be a .py or .js file")

            command = "python" if is_python else "node"

            server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],
                env=None
            )

            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            self.stdio, self.write = stdio_transport

            self.session = await self.exit_stack.enter_async_context(
                ClientSession(self.stdio, self.write)
            )

            await self.session.initialize()
            self.logger.info("✅ Connected to MCP server")

            # Load MCP tools and convert to Gemini format
            await self._load_tools()
            
            return True

        except Exception as e:
            self.logger.error(f"❌ Error connecting to MCP server: {e}")
            traceback.print_exc()
            raise

    # LOAD AND CONVERT MCP TOOLS TO GEMINI FORMAT
    async def _load_tools(self):
        try:
            response = await self.session.list_tools()
            mcp_tools = response.tools
            
            # Convert MCP tools to Gemini function declarations
            self.tools = []
            for tool in mcp_tools:
                gemini_tool = genai.protos.FunctionDeclaration(
                    name=tool.name,
                    description=tool.description or f"Execute {tool.name}",
                    parameters=genai.protos.Schema(
                        type=genai.protos.Type.OBJECT,
                        properties={
                            key: genai.protos.Schema(
                                type=self._convert_type(val.get("type", "string")),
                                description=val.get("description", "")
                            )
                            for key, val in tool.inputSchema.get("properties", {}).items()
                        },
                        required=tool.inputSchema.get("required", [])
                    )
                )
                self.tools.append(gemini_tool)
            
            self.logger.info(f"✅ Loaded {len(self.tools)} tools: {[t.name for t in self.tools]}")
            
        except Exception as e:
            self.logger.error(f"❌ Error loading tools: {e}")
            raise

    # CONVERT JSON SCHEMA TYPES TO GEMINI TYPES
    def _convert_type(self, json_type: str) -> genai.protos.Type:
        type_mapping = {
            "string": genai.protos.Type.STRING,
            "number": genai.protos.Type.NUMBER,
            "integer": genai.protos.Type.INTEGER,
            "boolean": genai.protos.Type.BOOLEAN,
            "array": genai.protos.Type.ARRAY,
            "object": genai.protos.Type.OBJECT,
        }
        return type_mapping.get(json_type.lower(), genai.protos.Type.STRING)

    # GET MCP TOOLS (for API endpoint)
    async def get_mcp_tools(self):
        try:
            response = await self.session.list_tools()
            return response.tools
        except Exception as e:
            self.logger.error(f"❌ Error getting MCP tools: {e}")
            raise

    # PROCESS QUERY WITH TOOL CALLING
    async def process_query(self, query: str) -> List[Dict[str, Any]]:
        try:
            self.logger.info(f"📝 Processing query: {query}")

            # Initialize chat session with tools
            if not self.chat_session:
                self.chat_session = self.llm.start_chat(
                    history=self.conversation_history,
                    enable_automatic_function_calling=False  # Manual control
                )

            messages = [{"role": "user", "content": query}]
            max_iterations = 10  # Prevent infinite loops
            iteration = 0

            while iteration < max_iterations:
                iteration += 1
                self.logger.info(f"🔄 Iteration {iteration}")

                # Send message to Gemini
                response = await self._call_gemini(query if iteration == 1 else None)

                # Check if response has function calls
                if self._has_function_calls(response):
                    self.logger.info("🔧 Function calls detected")
                    
                    # Execute all function calls
                    for part in response.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            fc = part.function_call
                            tool_name = fc.name
                            tool_args = dict(fc.args)
                            
                            self.logger.info(f"⚙️ Calling tool: {tool_name} with args: {tool_args}")
                            
                            # Execute MCP tool
                            try:
                                result = await self.session.call_tool(tool_name, tool_args)
                                tool_result = self._format_tool_result(result)
                                
                                self.logger.info(f"✅ Tool result: {tool_result[:200]}...")
                                
                                # Add tool call and result to messages
                                messages.append({
                                    "role": "assistant",
                                    "tool_calls": [{
                                        "name": tool_name,
                                        "args": tool_args
                                    }]
                                })
                                messages.append({
                                    "role": "tool",
                                    "tool_name": tool_name,
                                    "content": tool_result
                                })
                                
                                # Send tool result back to Gemini
                                response = self.chat_session.send_message(
                                    genai.protos.Content(
                                        parts=[genai.protos.Part(
                                            function_response=genai.protos.FunctionResponse(
                                                name=tool_name,
                                                response={"result": tool_result}
                                            )
                                        )]
                                    )
                                )
                                
                            except Exception as e:
                                error_msg = f"Error executing tool {tool_name}: {str(e)}"
                                self.logger.error(f"❌ {error_msg}")
                                messages.append({
                                    "role": "tool",
                                    "tool_name": tool_name,
                                    "content": error_msg
                                })
                                
                else:
                    # No function calls - we have final response
                    final_text = response.text if hasattr(response, 'text') else str(response)
                    self.logger.info(f"✅ Final response: {final_text[:200]}...")
                    
                    messages.append({
                        "role": "assistant",
                        "content": final_text
                    })
                    
                    # Save conversation
                    await self.log_conversation(messages)
                    
                    return messages

            # Max iterations reached
            self.logger.warning("⚠️ Max iterations reached")
            messages.append({
                "role": "assistant",
                "content": "I apologize, but I've reached the maximum number of tool calls. Please try breaking down your request."
            })
            
            return messages

        except Exception as e:
            self.logger.error(f"❌ Error processing query: {e}")
            traceback.print_exc()
            raise

    # CALL GEMINI WITH TOOLS
    async def _call_gemini(self, user_message: Optional[str] = None):
        try:
            if user_message:
                # First call with user message
                return self.chat_session.send_message(
                    user_message,
                    tools=[genai.protos.Tool(function_declarations=self.tools)] if self.tools else None
                )
            else:
                # Continuation call (after tool results)
                # Already sent via send_message with function_response
                pass
                
        except Exception as e:
            self.logger.error(f"❌ Error calling Gemini: {e}")
            raise

    # CHECK IF RESPONSE HAS FUNCTION CALLS
    def _has_function_calls(self, response) -> bool:
        if not hasattr(response, 'parts'):
            return False
        
        for part in response.parts:
            if hasattr(part, 'function_call') and part.function_call:
                return True
        
        return False

    # FORMAT TOOL RESULT
    def _format_tool_result(self, result) -> str:
        try:
            if hasattr(result, 'content'):
                content = result.content
                if isinstance(content, list):
                    # Extract text from content blocks
                    text_parts = []
                    for item in content:
                        if hasattr(item, 'text'):
                            text_parts.append(item.text)
                        elif isinstance(item, dict) and 'text' in item:
                            text_parts.append(item['text'])
                        else:
                            text_parts.append(str(item))
                    return "\n".join(text_parts)
                else:
                    return str(content)
            else:
                return str(result)
        except Exception as e:
            self.logger.error(f"❌ Error formatting tool result: {e}")
            return f"Error formatting result: {str(e)}"

    # CLEANUP
    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
            self.logger.info("🔌 Disconnected from MCP server")
        except Exception as e:
            self.logger.error(f"❌ Error during cleanup: {e}")
            traceback.print_exc()

    # SAVE CONVERSATION
    async def log_conversation(self, messages: List[Dict[str, Any]]):
        try:
            os.makedirs("conversations", exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filepath = os.path.join("conversations", f"conversation_{timestamp}.json")
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(messages, f, indent=2, default=str, ensure_ascii=False)
            
        
            self.logger.info(f"💾 Conversation saved: {filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error saving conversation: {e}")