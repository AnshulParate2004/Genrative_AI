from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import os
from bs4 import BeautifulSoup

load_dotenv()

mcp = FastMCP("docs")

USER_AGENT = "docs-app/1.0"
SERPER_URL = "https://google.serper.dev/search"

docs_urls = {
    "langchain": "python.langchain.com/docs",
    "llama-index": "docs.llamaindex.ai/en/stable",
    "openai": "platform.openai.com/docs",
}

async def search_web(query: str) -> dict | None:
    payload = json.dumps({"q": query, "num": 2})

    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                SERPER_URL, headers=headers, data=payload, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            return {"organic": []}
        except Exception as e:
            print(f"Error in search_web: {e}")
            return {"organic": []}

async def fetch_url(url: str):
    async with httpx.AsyncClient(follow_redirects=True) as client:
        try:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            
            # Set encoding explicitly
            response.encoding = 'utf-8'
            
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            
            # Clean the text to remove problematic characters
            text = text.encode('utf-8', 'ignore').decode('utf-8', 'ignore')
            
            return text
        except httpx.TimeoutException:
            return "Timeout error"
        except Exception as e:
            return f"Error fetching URL: {e}"

@mcp.tool()
async def get_docs(query: str, library: str):
    """
    Search the latest docs for a given query and library.
    Supports langchain, openai, and llama-index.

    Args:
        query: The query to search for (e.g. "Chroma DB")
        library: The library to search in (e.g. "langchain")

    Returns:
        Text from the docs
    """
    if library not in docs_urls:
        raise ValueError(f"Library {library} not supported by this tool")

    search_query = f"site:{docs_urls[library]} {query}"
    
    results = await search_web(search_query)

    if not results or len(results.get("organic", [])) == 0:
        return "No results found"

    text = ""
    for result in results["organic"]:
        fetched_text = await fetch_url(result["link"])
        text += f"\n\n--- Source: {result['link']} ---\n{fetched_text}\n"
    
    return text


if __name__ == "__main__":
    mcp.run(transport="stdio") 