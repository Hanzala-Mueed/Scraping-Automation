import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
from datetime import datetime

class FileCRScraper:
    def __init__(self, base_url="https://filecr.com", headless=False):
        self.base_url = base_url
        self.scraped_data = []
        self.progress_file = "scraping_progress.json"
        self.output_file = "new_scraper_data.json"
        self.progress = self.load_progress()
        
        # Setup Chrome driver
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def load_progress(self):
        """Load scraping progress from file"""
        if os.path.exists(self.progress_file):
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                progress = json.load(f)
                print(f"✅ Resuming from saved progress: {progress}")
                return progress
        return {
            "current_primary_index": 0,
            "current_sub_index": 0,
            "completed_categories": [],
            "last_scraped_url": None
        }
    
    def save_progress(self):
        """Save current progress to file"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2)
    
    def save_data(self):
        """Save scraped data to JSON file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        print(f"💾 Data saved to {self.output_file} ({len(self.scraped_data)} items)")
    
    def get_primary_categories(self):
        """Extract primary categories from header navigation"""
        try:
            nav_container = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.container nav.menu"))
            )
            
            categories = []
            category_links = nav_container.find_elements(By.CSS_SELECTOR, "a.menu_link__lDtKC")
            
            for link in category_links:
                name = link.find_element(By.TAG_NAME, "span").text.strip()
                url = link.get_attribute("href")
                categories.append({"name": name, "url": url})
            
            print(f"🎯 Found {len(categories)} primary categories: {[cat['name'] for cat in categories]}")
            return categories
            
        except Exception as e:
            print(f"❌ Error getting primary categories: {e}")
            return []
    
    def get_subcategories(self):
        """Extract subcategories from sidebar"""
        try:
            time.sleep(2)  # Wait for sidebar to load
            
            subcategories = []
            sidebar = self.driver.find_element(By.CSS_SELECTOR, "aside.sidebar")
            
            # Find the "Sub Category" section
            sub_category_sections = sidebar.find_elements(By.CSS_SELECTOR, "div.widget_wrap__lfits")
            
            for section in sub_category_sections:
                header = section.find_element(By.CSS_SELECTOR, "div.widget_header__vge_D h3")
                if "Sub Category" in header.text:
                    filter_options = section.find_elements(By.CSS_SELECTOR, "div.form-group.sub-category-filter")
                    
                    for option in filter_options:
                        label = option.find_element(By.TAG_NAME, "label")
                        checkbox = option.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
                        
                        name = label.text.strip()
                        # Remove private tag text if present
                        if "Private Category" in name:
                            name = name.replace("Private Category", "").strip()
                        
                        subcategories.append({
                            "name": name,
                            "checkbox_id": checkbox.get_attribute("id"),
                            "element": checkbox
                        })
                    break
            
            print(f"🎯 Found {len(subcategories)} subcategories")
            return subcategories
            
        except Exception as e:
            print(f"❌ Error getting subcategories: {e}")
            return []
    
    def click_subcategory(self, subcategory):
        """Click on a subcategory checkbox"""
        try:
            self.driver.execute_script("arguments[0].click();", subcategory["element"])
            time.sleep(3)  # Wait for page to load
            print(f"🔄 Selected subcategory: {subcategory['name']}")
            return True
        except Exception as e:
            print(f"❌ Error clicking subcategory {subcategory['name']}: {e}")
            return False
    
    def scrape_current_page(self, primary_cat, sub_cat, child_cat=None):
        """Scrape all products from current page"""
        try:
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find product containers (adjust selector based on actual HTML structure)
            products = soup.find_all('div', class_='card_wrap__S35wt')


            if not products:
                print("🔍 DEBUG: No products found with card_wrap__S35wt selector")
                print("📋 Looking for alternative card selectors...")
                
                # Try alternative card selectors in case class names change
                alt_selectors = [
                    'div[class*="card_wrap"]',
                    'div[class*="card"]',
                    '.card',
                    'div[class*="wrap"]'
                ]
                
                for selector in alt_selectors:
                    products = soup.select(selector)
                    if products:
                        print(f"🎯 Found {len(products)} products using alternative selector: {selector}")
                        break
                
                if not products:
                    print("❌ No product containers found with any selector")
                    return 0
            else:
                print(f"🎯 Found {len(products)} products using card_wrap__S35wt selector")
            # if not products:
            #     # Try alternative selectors
            #     products = soup.find_all('article') or soup.find_all('div', class_=lambda x: x and 'item' in x.lower())
            
            page_count = 0
            for product in products:
                try:
                    # # Extract product data (adjust selectors based on actual HTML)
                    # title_elem = product.find(['h1', 'h2', 'h3', 'h4', 'a'])
                    # title = title_elem.get_text().strip() if title_elem else "No title"
                    
                    # # Get URL
                    # url = None
                    # if title_elem and title_elem.name == 'a':
                    #     url = title_elem.get('href')
                    # else:
                    #     link_elem = product.find('a')
                    #     if link_elem:
                    #         url = link_elem.get('href')
                    
                    # # Make URL absolute
                    # if url and not url.startswith('http'):
                    #     url = self.base_url + url if url.startswith('/') else self.base_url + '/' + url


                
                    # Extract URL from the card_icon__mmJ8V link (as per your HTML structure)
                    link_elem = product.find('a', class_='card_icon__mmJ8V')
                    
                    if not link_elem:
                        # Fallback: try any link in the card
                        link_elem = product.find('a', href=True)
                    
                    if not link_elem or not link_elem.get('href'):
                        continue
                    
                    url = link_elem.get('href')
                    
                    # Extract title from the img alt attribute (as per your HTML structure)
                    title = None
                    img_elem = link_elem.find('img')
                    if img_elem and img_elem.get('alt'):
                        title = img_elem.get('alt').strip()
                    
                    # Fallback title extraction methods
                    if not title:
                        # Try to find title in other elements within the card
                        title_selectors = ['h1', 'h2', 'h3', 'h4', '.title', '.name', '.card-title']
                        for title_sel in title_selectors:
                            title_elem = product.select_one(title_sel)
                            if title_elem:
                                title = title_elem.get_text().strip()
                                break
                    
                    # If still no title, use link text or filename from URL
                    if not title:
                        title = link_elem.get_text().strip()
                        if not title and url:
                            # Extract title from URL as last resort
                            title = url.split('/')[-2].replace('-', ' ').title() if '/' in url else "Unknown"
                    
                    # Skip if still no proper title
                    if not title or len(title.strip()) < 3:
                        continue
                    
                    # Clean up title
                    title = ' '.join(title.split())  # Remove extra whitespace
                    
                    # Make URL absolute
                    if not url.startswith('http'):
                        if url.startswith('/'):
                            url = self.base_url + url
                        else:
                            url = self.base_url + '/' + url
                    
                    # Skip invalid URLs
                    if '#' in url or 'javascript:' in url.lower():
                        continue
                    
                    product_data = {
                        "title": title,
                        "url": url,
                        "primary_category": primary_cat,
                        "sub_category": sub_cat,
                        "child_category": child_cat,
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    self.scraped_data.append(product_data)
                    page_count += 1
                    
                except Exception as e:
                    print(f"⚠️ Error scraping individual product: {e}")
                    continue
            
            print(f"📦 Scraped {page_count} products from current page")
            return page_count
            
        except Exception as e:
            print(f"❌ Error scraping current page: {e}")
            return 0
    
    def has_next_page(self):
        """Check if there's a next page button"""
        try:
            next_button = self.driver.find_element(
                By.CSS_SELECTOR, 
                "div.pagination button[aria-label='pagination next']"
            )
            return next_button.is_enabled()
        except NoSuchElementException:
            return False
    
    def click_next_page(self):
        """Click the next page button"""
        try:
            next_button = self.wait.until(
                EC.element_to_be_clickable((
                    By.CSS_SELECTOR, 
                    "div.pagination button[aria-label='pagination next']"
                ))
            )
            self.driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            return True
        except Exception as e:
            print(f"❌ Error clicking next page: {e}")
            return False
    
    def scrape_category_with_pagination(self, primary_cat, sub_cat, child_cat=None):
        """Scrape all pages of a category"""
        page_num = 1
        total_products = 0
        
        while True:
            print(f"📄 Scraping page {page_num} of {sub_cat}")
            
            products_count = self.scrape_current_page(primary_cat, sub_cat, child_cat)
            total_products += products_count
            
            if products_count == 0:
                print(f"⚠️ No products found on page {page_num}, moving to next category")
                break
            
            # Check for next page
            if self.has_next_page():
                if self.click_next_page():
                    page_num += 1
                    time.sleep(2)
                else:
                    break
            else:
                break
        
        print(f"✅ Completed {sub_cat}: {total_products} total products across {page_num} pages")
        return total_products
    
    def scrape_all_categories(self):
        """Main scraping function"""
        try:
            print("🚀 Starting FileCR scraper...")
            self.driver.get(self.base_url)
            time.sleep(3)
            
            # Get primary categories
            primary_categories = self.get_primary_categories()
            
            if not primary_categories:
                print("❌ No primary categories found!")
                return
            
            # Start from saved progress
            start_primary = self.progress["current_primary_index"]
            
            for primary_idx in range(start_primary, len(primary_categories)):
                primary_cat = primary_categories[primary_idx]
                
                print(f"\n🎯 Processing PRIMARY CATEGORY: {primary_cat['name']} ({primary_idx + 1}/{len(primary_categories)})")
                
                # Skip if already completed
                if primary_cat['name'] in self.progress["completed_categories"]:
                    print(f"⏭️ Skipping already completed category: {primary_cat['name']}")
                    continue
                
                # Click on primary category
                self.driver.get(primary_cat['url'])
                time.sleep(3)
                
                # Get subcategories
                subcategories = self.get_subcategories()
                
                if not subcategories:
                    print(f"⚠️ No subcategories found for {primary_cat['name']}")
                    continue
                
                # Start from saved sub-category progress
                start_sub = self.progress["current_sub_index"] if primary_idx == start_primary else 0
                
                for sub_idx in range(start_sub, len(subcategories)):
                    sub_cat = subcategories[sub_idx]
                    
                    print(f"\n  🔸 Processing SUB CATEGORY: {sub_cat['name']} ({sub_idx + 1}/{len(subcategories)})")
                    
                    # Click subcategory
                    if self.click_subcategory(sub_cat):
                        # Scrape with pagination
                        self.scrape_category_with_pagination(
                            primary_cat['name'], 
                            sub_cat['name']
                        )
                        
                        print(f"✅ COMPLETED SUB CATEGORY: {sub_cat['name']}")
                        
                        # Update progress
                        self.progress["current_sub_index"] = sub_idx + 1
                        self.save_progress()
                        self.save_data()
                    
                    time.sleep(2)
                
                # Mark primary category as completed
                self.progress["completed_categories"].append(primary_cat['name'])
                self.progress["current_primary_index"] = primary_idx + 1
                self.progress["current_sub_index"] = 0
                self.save_progress()
                
                print(f"🎉 COMPLETED PRIMARY CATEGORY: {primary_cat['name']}")
            
            print(f"\n🎊 SCRAPING COMPLETED! Total products: {len(self.scraped_data)}")
            
        except KeyboardInterrupt:
            print("\n⏸️ Scraping interrupted by user")
        except Exception as e:
            print(f"❌ Critical error: {e}")
        finally:
            self.save_progress()
            self.save_data()
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
        print("🧹 Cleanup completed")

def main():
    scraper = FileCRScraper(headless=False)  # Set to True for headless mode
    try:
        scraper.scrape_all_categories()
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    main()


# ---------------------------------updated ---------------------

