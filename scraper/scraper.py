import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from db.database import SessionLocal
from db.models import Software



# Configure headless Chrome
options = Options()
options.add_argument("--headless=new") 
options.add_argument("--window-size=1920,1080")
driver = webdriver.Chrome(options=options)

#BASE_URL = "https://filecr.com/windows/security-privacy/"

BASE_URL = "https://filecr.com/windows/audio-music/"


def scrape_page():
    """Scrape data from current page"""
    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_cards = soup.select("div.product-list > div")

    data = []
    for card in product_cards:
        try:
            title_tag = card.select_one("a.card_title__az7G7")
            title = title_tag.text.strip() if title_tag else ""
            relative_url = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
            full_url = "https://filecr.com" + relative_url if relative_url else ""

            description_tag = card.select_one("p.card_desc__b66Ca")
            description = description_tag.text.strip() if description_tag else ""

            subcategory_tag = card.select_one("a.card_category__4DBde")
            subcategory = subcategory_tag.text.strip() if subcategory_tag else ""

            category_tag = card.select_one("span.card_primary-text__fEKA_")
            category = category_tag.text.strip() if category_tag else ""

            downloads_tag = card.select_one("span.card_meta-text__KdSKY")
            downloads = downloads_tag.text.strip() if downloads_tag else ""

            download_link, password, size = fetch_download_link(full_url)


            data.append({
                "title": title,
                "url": full_url,
                "description": description,
                "category": category,
                "subcategory": subcategory,
                "downloads": downloads,
                "size": size,
                "download_link": download_link,
                "password": password
            })

            driver.back()
            time.sleep(2)

        except Exception as e:
            print(f"Error parsing a card: {e}")

    return data


def fetch_download_link(software_url):
    """Navigate to software page, scrape size, click download, and fetch final download URL and password (if any)"""
    
    try:
        driver.get(software_url)
        time.sleep(2)  

        # --- Scrape size info before clicking download ---
        size = {"value": "", "unit": ""}

        try:
            soup_before_click = BeautifulSoup(driver.page_source, "html.parser")
            size_div = soup_before_click.select_one("div.download-size")

            if size_div:
                raw_texts = list(size_div.stripped_strings)

                for t in raw_texts:
                    cleaned = t.replace('"', '').strip()
                    try:
                        float(cleaned)
                        size["value"] = cleaned
                        break
                    except ValueError:
                        continue

                unit_span = size_div.select_one("span")
                size["unit"] = unit_span.text.strip() if unit_span else ""

        except Exception as e:
            print(f"Size scrape failed at {software_url}: {e}")


        # --- Click the "Direct Download" button ---
        try:
            direct_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Direct Download')]"))
            )

            direct_button.click()
            print("✅ Clicked 'Direct Download' button")

        except TimeoutException:
            print(f"'Direct Download' button not found at {software_url}")
            return None, "", size

        # --- Extract download link and password ---
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a#download-btn.sh_download-btn.done"))
        )
        soup_after_click = BeautifulSoup(driver.page_source, "html.parser")

        # Download link
        download_button = soup_after_click.select_one("a#download-btn.sh_download-btn.done")
        download_link = download_button["href"] if download_button and download_button.get("href") else None

        # Password
        password_tag = soup_after_click.find("span", class_="password")
        password = password_tag.text.strip() if password_tag else "" 

        return download_link, password, size

    except Exception as e:
        print(f"Download link error at {software_url}: {e}")
        return None, "", {"value": "", "unit": ""}


# def click_next_page():
#     """Click the next page button if available"""
#     try:
#         next_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Next Page")]')
#         driver.execute_script("arguments[0].click();", next_btn)
#         time.sleep(3)
#         return True
#     except NoSuchElementException:
#         return False

def click_next_page():
    """Dummy next page function for testing."""
    return None


def run_scraper():
    driver.get(BASE_URL)
    all_data = []

    while True:
        print("🔄 Scraping current page...")
        page_data = scrape_page()
        all_data.extend(page_data)

        print("👉 Checking for next page...")
        if not click_next_page():
            print("No more pages.")
            break

    # Save to JSON
    with open("2_data.json", "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=4)
        print("Data saved to 2_data.json")

    driver.quit()
    return all_data 


def save_to_db(all_data):
    db = SessionLocal()
    for item in all_data:
        software = Software(
            title=item["title"],
            url=item["url"],
            description=item["description"],
            subcategory=item["subcategory"],
            category=item["category"],
            downloads=item["downloads"],
            size=item["size"],
            download_link=item["download_link"],
            password=item["password"]
        )
        db.add(software)
    db.commit()
    db.close()


if __name__ == "__main__":
    scraped_data = run_scraper()  
    save_to_db(scraped_data) 



