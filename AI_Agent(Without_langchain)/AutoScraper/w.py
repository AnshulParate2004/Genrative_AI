import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

lock = threading.Lock()  # Ensure thread-safe file writes

def get_driver():
    """Setup Selenium Chrome driver (headless)."""
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
    """Scrape a page and return {title, content}."""
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

def scrape_result(result, output_file="scraped_output.jsonl"):
    """Scrape a main result + its sitelinks (if any) and write directly to file."""
    scraped = scrape_page(result["link"])
    scraped["position"] = result.get("position")

    # Handle sitelinks
    sitelinks_data = []
    if "sitelinks" in result and result["sitelinks"]:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(scrape_page, sl["link"]) for sl in result["sitelinks"]]
            for i, future in enumerate(as_completed(futures)):
                sl_data = future.result()
                sl_data["title"] = result["sitelinks"][i]["title"]
                sitelinks_data.append(sl_data)

    if sitelinks_data:
        scraped["sitelinks"] = sitelinks_data

    # Thread-safe write to file
    with lock:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(scraped, ensure_ascii=False) + "\n")

def run_threadpool(input_file="serper_output.json", output_file="scraped_output.jsonl"):
    with open(input_file, "r", encoding="utf-8") as f:
        serper_data = json.load(f)

    results = serper_data.get("results", [])

    # Scrape all results in parallel
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(scrape_result, r, output_file) for r in results]
        for _ in as_completed(futures):
            pass  # Results are written directly

    print(f"✅ All data written directly to {output_file}")

if __name__ == "__main__":
    run_threadpool()
