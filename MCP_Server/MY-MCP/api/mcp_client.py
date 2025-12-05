from typing import Optional
from contextlib import AsyncExitStack
import traceback
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from utils.logger import logger
from utils.weather_tool import WeatherTool, WEATHER_TOOL_SCHEMA, FORECAST_TOOL_SCHEMA
from utils.serper_tool import SerperSearchTool, SERPER_SEARCH_TOOL_SCHEMA
import os
import google.generativeai as genai


class MCPClient:
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()

        # Gemini init
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.llm = genai.GenerativeModel("gemini-2.5-pro")

        # Initialize custom tools
        self.weather_tool = WeatherTool(api_key=os.getenv("OPENWEATHER_API_KEY"))
        self.serper_tool = SerperSearchTool(api_key=os.getenv("SERPER_API_KEY"))

        self.tools = []
        self.custom_tools = [
            WEATHER_TOOL_SCHEMA,
            FORECAST_TOOL_SCHEMA,
            SERPER_SEARCH_TOOL_SCHEMA
        ]
        self.messages = []
        self.logger = logger

    # CONNECT TO MCP SERVER
    async def connect_to_server(self, server_script_path: str):
        try:
            is_python = server_script_path.endswith(".py")
            is_js = server_script_path.endswith(".js")

            if not (is_python or is_js):
                raise ValueError("Server script must be a .py or .js file")

            command = "python" if is_python else "node"

            server_params = StdioServerParameters(
                command=command,
                args=[server_script_path],  # MUST be list
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
            self.logger.info("Connected to MCP server")

            # fetch MCP tools
            mcp_tools = await self.session.get_mcp_tools()
            mcp_tool_list = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in mcp_tools
            ]

            # Combine MCP tools with custom tools
            self.tools = mcp_tool_list + self.custom_tools

            self.logger.info(f"Available tools: {len(self.tools)} total")
            self.logger.info(f"  - MCP tools: {len(mcp_tool_list)}")
            self.logger.info(f"  - Custom tools: {len(self.custom_tools)}")

        except Exception as e:
            self.logger.error(f"Error connecting to MCP server: {e}")
            traceback.print_exc()
            raise

    # GET ALL TOOLS (MCP + CUSTOM)
    async def get_mcp_tools(self):
        try:
            # Get MCP server tools
            response = await self.session.list_tools()
            mcp_tools = response.tools
            
            # Create custom tool objects that match MCP tool format
            class CustomTool:
                def __init__(self, name, description, input_schema):
                    self.name = name
                    self.description = description
                    self.inputSchema = input_schema
            
            custom_tool_objects = [
                CustomTool(
                    tool["name"],
                    tool["description"],
                    tool["input_schema"]
                )
                for tool in self.custom_tools
            ]
            
            # Combine both
            all_tools = list(mcp_tools) + custom_tool_objects
            return all_tools
            
        except Exception as e:
            self.logger.error(f"Error getting tools: {e}")
            raise

    # HANDLE CUSTOM TOOL CALLS
    async def call_custom_tool(self, tool_name: str, tool_args: dict):
        """Handle calls to custom tools (weather, serper)"""
        try:
            if tool_name == "get_weather":
                result = await self.weather_tool.get_weather(
                    location=tool_args.get("location"),
                    units=tool_args.get("units", "metric")
                )
                formatted_result = self.weather_tool.format_weather_response(result)
                return {"content": [{"type": "text", "text": formatted_result}]}
            
            elif tool_name == "get_weather_forecast":
                result = await self.weather_tool.get_forecast(
                    location=tool_args.get("location"),
                    units=tool_args.get("units", "metric"),
                    cnt=tool_args.get("cnt", 5)
                )
                # Format forecast results
                if "error" in result:
                    formatted_result = f"Error: {result['error']}"
                else:
                    formatted_result = f"Forecast for {result['location']}:\n\n"
                    for forecast in result['forecasts']:
                        formatted_result += f"📅 {forecast['datetime']}\n"
                        formatted_result += f"   🌡️ {forecast['temperature']}° - {forecast['weather']}\n"
                        formatted_result += f"   {forecast['description']}\n\n"
                
                return {"content": [{"type": "text", "text": formatted_result}]}
            
            elif tool_name == "web_search":
                result = await self.serper_tool.search(
                    query=tool_args.get("query"),
                    num_results=tool_args.get("num_results", 10),
                    search_type=tool_args.get("search_type", "search"),
                    location=tool_args.get("location"),
                    time_range=tool_args.get("time_range")
                )
                formatted_result = self.serper_tool.format_search_response(
                    result, 
                    tool_args.get("search_type", "search")
                )
                return {"content": [{"type": "text", "text": formatted_result}]}
            
            else:
                error_msg = f"Unknown custom tool: {tool_name}"
                self.logger.error(error_msg)
                return {"content": [{"type": "text", "text": error_msg}]}
                
        except Exception as e:
            error_msg = f"Error calling custom tool {tool_name}: {str(e)}"
            self.logger.error(error_msg)
            return {"content": [{"type": "text", "text": error_msg}]}

    # PROCESS QUERY
    async def process_query(self, query: str):
        try:
            self.logger.info(f"Processing query: {query}")
            self.messages = [{"role": "user", "content": query}]

            while True:
                response = await self.call_llm()

                # NO TOOL, only text
                if (
                    response.content[0].type == "text"
                    and len(response.content) == 1
                ):
                    self.messages.append(
                        {"role": "assistant", "content": response.content[0].text}
                    )
                    break

                # Else, handle tool calls
                for content in response.content:
                    if content.type == "tool_call":
                        tool_name = content.name
                        tool_args = content.input
                        tool_use_id = content.id

                        self.logger.info(
                            f"Calling tool {tool_name} with args {tool_args}"
                        )

                        # Check if it's a custom tool or MCP tool
                        custom_tool_names = [t["name"] for t in self.custom_tools]
                        
                        if tool_name in custom_tool_names:
                            # Call custom tool
                            result = await self.call_custom_tool(tool_name, tool_args)
                        else:
                            # Call MCP tool
                            result = await self.session.call_tool(tool_name, tool_args)

                        # Send tool_result back to LLM
                        self.messages.append(
                            {
                                "role": "user",
                                "content": [
                                    {
                                        "type": "tool_result",
                                        "tool_use_id": tool_use_id,
                                        "content": result.content,
                                    }
                                ],
                            }
                        )

            return self.messages

        except Exception as e:
            self.logger.error(f"Error processing query: {e}")
            raise

    # CALL GEMINI LLM
    async def call_llm(self):
        try:
            return await self.llm.messages.create(
                messages=self.messages,
                tools=self.tools,
                max_tokens=100000
            )
        except Exception as e:
            self.logger.error(f"Error calling LLM: {e}")
            raise

    # CLEANUP
    async def cleanup(self):
        try:
            await self.exit_stack.aclose()
            self.logger.info("Disconnected from MCP server")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
            traceback.print_exc()
            raise
