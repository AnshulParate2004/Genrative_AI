import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_serper():
    payload = json.dumps({"q": "site:python.langchain.com/docs Chroma", "num": 2})
    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://google.serper.dev/search",
            headers=headers,
            data=payload,
            timeout=30.0
        )
        print(response.json())

import asyncio
asyncio.run(test_serper())