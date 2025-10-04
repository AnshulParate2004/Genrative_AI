import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import os
from dotenv import load_dotenv

load_dotenv()

SERPER_API_KEY = os.getenv("SERPER_API_KEY")
lock = threading.Lock() 

# serper fetch 
def fetch_serper(query):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    res = requests.post(url, headers=headers, json={"q": query})
    res.raise_for_status()
    data = res.json()

    results = []
    for item in data.get("organic", []):
        sitelinks = [{"title": sl.get("title"), "link": sl.get("link")} for sl in item.get("sitelinks", [])]
        results.append({
            "position": item.get("position"),
            "title": item.get("title"),
            "link": item.get("link"),
            "sitelinks": sitelinks
        })
    return results

# selenium 
def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def scrape_page(url):
    driver = get_driver()
    driver.get(url)
    time.sleep(1)

    title = ""
    if driver.find_elements(By.ID, "firstHeading"):
        title = driver.find_element(By.ID, "firstHeading").text
    else:
        title = driver.title

    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    content = "\n".join([p.text for p in paragraphs if p.text.strip()])

    driver.quit()
    return {"title": title, "content": content}

def scrape_result(result, output_file):

    scraped = scrape_page(result["link"])
    scraped["position"] = result.get("position")

    # Scrape 
    sitelinks_data = []
    if result.get("sitelinks"):
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(scrape_page, sl["link"]) for sl in result["sitelinks"]]
            for i, future in enumerate(as_completed(futures)):
                sl_data = future.result()
                sl_data["title"] = result["sitelinks"][i]["title"]
                sitelinks_data.append(sl_data)

    if sitelinks_data:
        scraped["sitelinks"] = sitelinks_data

    # write to JSONL
    with lock:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(scraped, ensure_ascii=False) + "\n")
            f.flush()


def main(query, output_file="scraped_output.jsonl"):
    results = fetch_serper(query)
    if not results:
        print("No results from Serper.")
        return

    # Remove old 
    open(output_file, "w").close()

    # Scrape parallel
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(scrape_result, r, output_file) for r in results]
        for _ in as_completed(futures):
            pass

    print(f"data saved directly to {output_file}")

if __name__ == "__main__":
    main("What is world?")
