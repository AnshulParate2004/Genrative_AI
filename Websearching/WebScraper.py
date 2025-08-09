from duckduckgo_search import DDGS

query = "What is the carbon footprint of Mumbai?"

with DDGS() as ddgs:
    results = ddgs.text(query, region="wt-wt", safesearch="moderate", max_results=5)
    for r in results:
        print("Title:", r["title"])
        print("URL:", r["href"])
        print("Snippet:", r["body"])
        print("------")
