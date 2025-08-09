from dotenv import load_dotenv
import os
import requests
import json

# Load API keys from .env file
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
METAPHOR_API_KEY = os.getenv("METAPHOR_API_KEY")

def search_tavily(query):
    url = "https://api.tavily.com/search"
    headers = {
        "Authorization": f"Bearer {TAVILY_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
    }
    res = requests.post(url, headers=headers, json=json_data)
    return res.json()

def search_serper(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    res = requests.post(url, headers=headers, json={"q": query})
    return res.json()
# Duckgo is trash can use hit and try but not worthy 
# def search_duckduckgo(query):
#     url = "https://api.duckduckgo.com/"
#     params = {"q": query, "format": "json"}
#     res = requests.get(url, params=params)
#     return res.json()

# Good for DataSources BUTNOT GOOD for websearch
# def search_metaphor(query):
#     url = "https://api.metaphor.systems/search"
#     headers = {"X-Api-Key": METAPHOR_API_KEY, "Content-Type": "application/json"}
#     data = {"query": query, "numResults": 5}
#     res = requests.post(url, headers=headers, json=data)
#     return res.json()

# === Run and collect results ===
query = "What is payment of genrative ai devloper in INdia ?"

results = {
    "query": query,
    "Tavily": search_tavily(query),
    "Serper": search_serper(query),
    #"DuckDuckGo": search_duckduckgo(query),
    #"Metaphor": search_metaphor(query)
}

# === Save results to JSON file ===
output_file = "search_results.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=4)

print(f"\n✅ All results saved to {output_file}")
