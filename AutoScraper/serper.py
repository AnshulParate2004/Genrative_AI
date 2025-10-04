import requests
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed



# -------------------- Serper fetch --------------------
def fetch_serper(query):
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    try:
        res = requests.post(url, headers=headers, json={"q": query})
        res.raise_for_status()
        data = res.json()
    except Exception as e:
        print(f"Error in Serper request: {e}")
        return []

    results = []
    for item in data.get("organic", []):
        sitelinks = [{"title": sl.get("title"), "link": sl.get("link")}
                     for sl in item.get("sitelinks", [])]
        results.append({
            "position": item.get("position"),
            "title": item.get("title"),
            "link": item.get("link"),
            "sitelinks": sitelinks
        })
    return results

# -------------------- Selenium scraper --------------------
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
    try:
        driver.get(url)
        time.sleep(1)

        try:
            title = driver.find_element(By.ID, "firstHeading").text
        except:
            title = driver.title if driver.title else ""

        try:
            paragraphs = driver.find_elements(By.TAG_NAME, "p")
            content = "\n".join([p.text for p in paragraphs if p.text.strip()])
        except:
            content = ""

        return {"title": title, "content": content}
    except Exception as e:
        return {"title": "", "content": f"Error: {e}"}
    finally:
        driver.quit()

def scrape_result(result, file_handle):
    """Scrape main result + sitelinks and write immediately to file."""
    scraped = scrape_page(result["link"])
    scraped["position"] = result.get("position")

    # Scrape sitelinks in parallel
    sitelinks_data = []
    if result.get("sitelinks"):
        with ThreadPoolExecutor(max_workers=MAX_SITELINK_THREADS) as executor:
            futures = [executor.submit(scrape_page, sl["link"]) for sl in result["sitelinks"]]
            for i, future in enumerate(as_completed(futures)):
                sl_data = future.result()
                # Keep original sitelink title
                sl_data["title"] = result["sitelinks"][i]["title"]
                sitelinks_data.append(sl_data)

    if sitelinks_data:
        scraped["sitelinks"] = sitelinks_data

    # Write this result directly to JSONL
    file_handle.write(json.dumps(scraped, ensure_ascii=False) + "\n")
    file_handle.flush()  # ensure written immediately

# -------------------- Main execution --------------------
def main(query, output_file="scraped_output.jsonl"):
    results = fetch_serper(query)
    if not results:
        print("No results from Serper.")
        return

    with open(output_file, "w", encoding="utf-8") as f:
        with ThreadPoolExecutor(max_workers=MAX_RESULT_THREADS) as executor:
            futures = [executor.submit(scrape_result, r, f) for r in results]
            # Wait for all to finish
            for _ in as_completed(futures):
                pass

    print(f"✅ All data saved directly to {output_file}")

# -------------------- Run --------------------
if __name__ == "__main__":
    main("What is world?")
