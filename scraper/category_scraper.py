
# import json
# import time
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from selenium.common.exceptions import NoSuchElementException, TimeoutException
# from selenium.webdriver.common.action_chains import ActionChains
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from bs4 import BeautifulSoup
# from sqlalchemy.orm import Session
# from etl.models import Categories
# from etl.db import SessionLocal

# # Headless browser setup
# options = Options()
# options.add_argument("--headless=new")
# driver = webdriver.Chrome(options=options)
# wait = WebDriverWait(driver, 10)

# #driver.get("https://filecr.com/android/")
# driver.get("https://filecr.com/ms-windows/")
# time.sleep(5)

# json_results = []

# # Save to DB
# def save_to_db(session: Session, title, url, primary, sub, child):
#     categories = Categories(
#         title=title,
#         url=url,
#         primary_category=primary,
#         sub_category=sub,
#         child_category=child
#     )
#     session.add(categories)
#     session.commit()

# # Save to JSON
# def save_to_json(title, url, primary, sub, child, results_list):
#     results_list.append({
#         "title": title,
#         "url": url,
#         "primary_category": primary,
#         "sub_category": sub,
#         "child_category": child
#     })

# # Safe click with wait
# def safe_click(elem):
#     try:
#         ActionChains(driver).move_to_element(elem).click().perform()
#         time.sleep(2)  # slight delay for JS to load
#     except Exception as e:
#         print(f"[!] Click failed: {e}")

# # Pagination handler
# def click_next_page():
#     try:
#         next_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Next Page")]')
#         driver.execute_script("arguments[0].click();", next_btn)
#         time.sleep(3)
#         return True
#     except NoSuchElementException:
#         return False

# # Scrape products on page
# def scrape_products(session, primary, sub, child):
#     print(f"🔍 Scraping products for: {primary} > {sub} > {child}")
#     while True:
#         try:
#             wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card_wrap__S35wt")))
#         except TimeoutException:
#             print("⚠️ Timed out waiting for products to load.")
#             break

#         soup = BeautifulSoup(driver.page_source, "html.parser")
#         found = False

#         for card in soup.select(".card_wrap__S35wt"):
#             title_tag = card.select_one("a.card_title__az7G7")
#             title = title_tag.text.strip() if title_tag else ""
#             relative_url = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
#             full_url = "https://filecr.com" + relative_url if relative_url else ""

#             if title and full_url:
#                 print(f"📦 Found: {title} ({full_url})")
#                 save_to_db(session, title, full_url, primary, sub, child)
#                 save_to_json(title, full_url, primary, sub, child, json_results)
#                 found = True

#         if not click_next_page():
#             break
#         if not found:
#             print("⚠️ No products found on this page.")
#             break

# # Start scraping categories
# session = SessionLocal()

# try:
#     wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")))
#     primary_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")

#     for i, primary_el in enumerate(primary_cats):
#         primary_label = primary_el.find_element(By.TAG_NAME, "label")
#         primary_name = primary_label.text.strip()
#         print(f"\n🔷 PRIMARY: {primary_name}")
#         safe_click(primary_label)

#         time.sleep(2)
#         sub_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")

#         for j, sub_el in enumerate(sub_cats):
#             sub_label = sub_el.find_element(By.TAG_NAME, "label")
#             sub_name = sub_label.text.strip()
#             print(f"  🔹 SUB: {sub_name}")
#             safe_click(sub_label)

#             time.sleep(2)
#             child_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")

#             if child_cats:
#                 for child_el in child_cats:
#                     child_label = child_el.find_element(By.TAG_NAME, "label")
#                     child_name = child_label.text.strip()
#                     print(f"    🔸 CHILD: {child_name}")
#                     safe_click(child_label)
#                     scrape_products(session, primary_name, sub_name, child_name)
#             else:
#                 print("    ❌ No child categories.")
#                 scrape_products(session, primary_name, sub_name, None)

# except Exception as e:
#     print(f"💥 Error occurred: {e}")

# finally:
#     print("\n💾 Saving scraped data to JSON...")
#     with open("scraped_data.json", "w", encoding="utf-8") as f:
#         json.dump(json_results, f, ensure_ascii=False, indent=4)
#     session.close()
#     driver.quit()
#     print("✅ Done.")

#---------------------------




import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from db.models import Categories
from db.database import SessionLocal

json_results = []

def setup_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    return webdriver.Chrome(options=options)

def save_to_db(session: Session, title, url, primary, sub, child):
    categories = Categories(
        title=title,
        url=url,
        primary_category=primary,
        sub_category=sub,
        child_category=child
    )
    session.add(categories)
    session.commit()

def save_to_json(title, url, primary, sub, child, results_list):
    results_list.append({
        "title": title,
        "url": url,
        "primary_category": primary,
        "sub_category": sub,
        "child_category": child
    })

def safe_click(driver, elem):
    try:
        ActionChains(driver).move_to_element(elem).click().perform()
        time.sleep(2)
    except Exception as e:
        print(f"[!] Click failed: {e}")

def click_next_page(driver):
    try:
        next_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Next Page")]')
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(3)
        return True
    except NoSuchElementException:
        return False

def click_categories_button(driver, wait):
    try:
        categories_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//a[span[text()='Categories']]"))
        )
        categories_button.click()
        print("✅ Clicked 'Categories' button.")
        time.sleep(3)
    except TimeoutException:
        print("❌ Timeout: 'Categories' button not found.")
        driver.quit()
        raise

def click_first_primary_category(driver, wait):
    try:
        first_primary_cat = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "div.nav_links__iogCZ a"))
        )
        print(f"✅ Clicking first primary category: {first_primary_cat.text.strip()}")
        first_primary_cat.click()
        time.sleep(3)
    except TimeoutException:
        print("❌ Timeout: Primary category not found.")
        driver.quit()
        raise

def scrape_current_products(driver, wait, session, primary, sub, child):
    print(f"🔍 Scraping products for: {primary} > {sub} > {child}")
    while True:
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".card_wrap__S35wt")))
        except TimeoutException:
            print("⚠️ Timed out waiting for products to load.")
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        found = False

        for card in soup.select(".card_wrap__S35wt"):
            title_tag = card.select_one("a.card_title__az7G7")
            title = title_tag.text.strip() if title_tag else ""
            relative_url = title_tag["href"] if title_tag and title_tag.has_attr("href") else ""
            full_url = "https://filecr.com" + relative_url if relative_url else ""

            if title and full_url:
                print(f"📦 Found: {title} ({full_url})")
                save_to_db(session, title, full_url, primary, sub, child)
                save_to_json(title, full_url, primary, sub, child, json_results)
                found = True

        if not click_next_page(driver):
            break
        if not found:
            print("⚠️ No products found on this page.")
            break


def scrape_all(driver, wait, session):
    wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")))

    primary_cat_labels = [
        el.find_element(By.TAG_NAME, "label")
        for el in driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")
    ]

    for primary_label in primary_cat_labels:
        primary_name = primary_label.text.strip()
        print(f"\n🔷 PRIMARY: {primary_name}")
        safe_click(driver, primary_label)
        wait.until(EC.staleness_of(primary_label))
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")))

        sub_cat_elements = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")
        sub_cat_labels = [el.find_element(By.TAG_NAME, "label") for el in sub_cat_elements]

        for sub_label in sub_cat_labels:
            sub_name = sub_label.text.strip()
            print(f"  🔹 SUB: {sub_name}")
            safe_click(driver, sub_label)
            wait.until(EC.staleness_of(sub_label))
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")))

            all_filters = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")
            if len(all_filters) > len(sub_cat_labels):
                child_cat_elements = all_filters[len(sub_cat_labels):]
                child_cat_labels = [el.find_element(By.TAG_NAME, "label") for el in child_cat_elements]

                for child_label in child_cat_labels:
                    child_name = child_label.text.strip()
                    print(f"    🔸 CHILD: {child_name}")
                    safe_click(driver, child_label)
                    wait.until(EC.staleness_of(child_label))
                    scrape_current_products(driver, wait, session, primary_name, sub_name, child_name)
            else:
                print("    ❌ No child categories.")
                scrape_current_products(driver, wait, session, primary_name, sub_name, None)



# def scrape_all(driver, wait, session):
#     wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")))
#     primary_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")

#     for i in range(len(primary_cats)):
#         primary_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")
#         primary_label = primary_cats[i].find_element(By.TAG_NAME, "label")
#         primary_name = primary_label.text.strip()
#         print(f"\n🔷 PRIMARY: {primary_name}")
#         safe_click(driver, primary_label)
#         time.sleep(2)

#         sub_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")

#         for j in range(len(sub_cats)):
#             sub_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")
#             sub_label = sub_cats[j].find_element(By.TAG_NAME, "label")
#             sub_name = sub_label.text.strip()
#             print(f"  🔹 SUB: {sub_name}")
#             safe_click(driver, sub_label)
#             time.sleep(2)
            
#             all_filters = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")

#             if len(all_filters) > len(sub_cats):
#                 for k in range(len(all_filters)):
#                     child_cats = driver.find_elements(By.CSS_SELECTOR, ".filter-options .form-group.sub-category-filter")
#                     if k < len(child_cats):
#                         child_label = child_cats[k].find_element(By.TAG_NAME, "label")
#                         child_name = child_label.text.strip()
#                         print(f"    🔸 CHILD: {child_name}")
#                         safe_click(driver, child_label)
#                         time.sleep(2)
#                         scrape_current_products(driver, wait, session, primary_name, sub_name, child_name)
#             else:
#                 print("    ❌ No child categories.")
#                 scrape_current_products(driver, wait, session, primary_name, sub_name, None)

def main():
    driver = setup_driver()
    wait = WebDriverWait(driver, 10)
    session = SessionLocal()

    try:
        driver.get("https://filecr.com/")
        print("🌐 Opened filecr.com")

        click_categories_button(driver, wait)
        print("✅ Clicked 'Categories' button.")

        click_first_primary_category(driver, wait)
        print("✅ Clicked first primary category.")

        scrape_all(driver, wait, session)
        print("✅ Scraped all categories.")


    except Exception as e:
        print(f"💥 Error occurred: {e}")

    finally:
        print("\n💾 Saving scraped data to JSON...")
        with open("category_scraper.json", "w", encoding="utf-8") as f:
            json.dump(json_results, f, ensure_ascii=False, indent=4)
        session.close()
        driver.quit()
        print("✅ Done.")

if __name__ == "__main__":
    main()



# watch dog for   detection 
# rclone for  uploading and managing softwares




