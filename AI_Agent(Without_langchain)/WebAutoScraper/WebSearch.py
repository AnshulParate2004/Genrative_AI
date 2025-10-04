from dotenv import load_dotenv
import os
import requests
import json

# Load API keys from .env file
load_dotenv()
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

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
    try:
        res = requests.post(url, headers=headers, json=json_data)
        res.raise_for_status()  # Raise an exception for bad status codes
        return res.json()
    except Exception as e:
        print(f"Error in search_tavily: {e}")
        return {}

def search_serper(query):
    url = "https://google.serper.dev/search"
    headers = {
        "X-API-KEY": SERPER_API_KEY,
        "Content-Type": "application/json"
    }
    try:
        res = requests.post(url, headers=headers, json={"q": query})
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error in search_serper: {e}")
        return {}

def combined_search(query):
    try:
        tavily_results = search_tavily(query)
        results = {
            "answer": tavily_results.get("answer", "No relevant results found.")
        }
        # Save results to JSON files in the current working directory
        output_files = [ "combined_search.json"]
        for output_file in output_files:
            try:
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4)
                print(f"\n✅ All results saved to {os.path.abspath(output_file)}")
            except Exception as e:
                print(f"Error saving to {output_file}: {e}")
        return results
    except Exception as e:
        print(f"Error in combined_search: {e}")
        return {"answer": "No relevant results found."}

# === Run and collect results (for testing) ===
if __name__ == "__main__":
    query = "Who is maker of ChaiaurCode Channel on youtube"
    results = combined_search(query)