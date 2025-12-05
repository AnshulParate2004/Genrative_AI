from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
from contextlib import asynccontextmanager

from mcp_client import MCPClient   # <-- This is now the GEMINI version
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()


class Settings(BaseSettings):
    # CHANGE THIS TO YOUR SERVER SCRIPT PATH
    server_script_path: str = r"D:\Learning\Genrative_AI\MCP_Server\MY-MCP\api\tools_server.py"


settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = MCPClient()
    try:
        connected = await client.connect_to_server(settings.server_script_path)
        if not connected:
            raise HTTPException(
                status_code=500,
                detail="❌ Failed to connect to MCP server"
            )

        app.state.client = client
        yield

    except Exception as e:
        print(f"Error during lifespan: {e}")
        raise HTTPException(status_code=500, detail=f"Startup error: {str(e)}") from e

    finally:
        await client.cleanup()


app = FastAPI(title="MCP Client API (Gemini-Powered)", lifespan=lifespan)


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- MODELS ----------
class QueryRequest(BaseModel):
    query: str


class Message(BaseModel):
    role: str
    content: Any


class ToolCall(BaseModel):
    name: str
    args: Dict[str, Any]


# ---------- ROUTES ----------
@app.post("/query")
async def process_query(request: QueryRequest):
    """Send a query to Gemini + MCP Tools"""
    try:
        messages = await app.state.client.process_query(request.query)
        return {"messages": messages}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Query processing error: {str(e)}"
        )


@app.get("/tools")
async def get_tools():
    """Get list of MCP tools from server"""
    try:
        tools = await app.state.client.get_mcp_tools()
        return {
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": tool.inputSchema,
                }
                for tool in tools
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"❌ Could not fetch MCP tools: {str(e)}"
        )


# ---------- RUN SERVER ----------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
