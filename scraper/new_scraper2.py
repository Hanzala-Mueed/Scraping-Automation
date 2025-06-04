import json
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from bs4 import BeautifulSoup
from datetime import datetime

class FileCRScraper:
    def __init__(self, base_url="https://filecr.com", headless=False):
        self.base_url = base_url
        self.scraped_data = []
        self.progress_file = "scraping_progress2.json"
        self.output_file = "new_scraper_data2.json"
        self.progress = self.load_progress()
        
        # Setup Chrome driver
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)  # Increased timeout
        
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
    
    def debug_page_structure(self):
        """Debug method to understand current page structure"""
        try:
            print("🔍 DEBUG: Analyzing page structure...")
            
            # Check for common sidebar/widget elements
            sidebar_selectors = [
                "aside.sidebar",
                ".sidebar",
                "[class*='sidebar']",
                "[class*='widget']",
                ".widget_wrap__lfits"
            ]
            
            for selector in sidebar_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"  ✓ Found {len(elements)} elements with selector: {selector}")
                    
            # Look for text containing 'Sub' or 'Category'
            text_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'Sub') or contains(text(), 'Category')]")
            print(f"  ✓ Found {len(text_elements)} elements containing 'Sub' or 'Category'")
            
            for i, elem in enumerate(text_elements[:5]):
                try:
                    print(f"    {i+1}. {elem.tag_name}: '{elem.text[:50]}...'")
                except:
                    pass
            
            # Look for checkboxes and form elements
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
            print(f"  ✓ Found {len(checkboxes)} checkboxes on page")
            
            # Look for links that might be subcategories
            all_links = self.driver.find_elements(By.TAG_NAME, 'a')
            category_links = [link for link in all_links if 'category' in link.get_attribute('href').lower()]
            print(f"  ✓ Found {len(category_links)} links containing 'category'")
            
        except Exception as e:
            print(f"❌ Debug failed: {e}")
    
    def get_subcategories(self):
        """Extract subcategories from sidebar - ROBUST VERSION with multiple strategies"""
        try:
            print("🔍 Searching for subcategories...")
            time.sleep(3)  # Wait for page to fully load
            
            subcategories = []
            
            # Strategy 1: Original method - exact XPath
            try:
                print("🔄 Trying Strategy 1: Original XPath...")
                sub_category_widget = self.wait.until(
                    EC.presence_of_element_located((
                        By.XPATH, 
                        "//div[@class='widget_wrap__lfits']//h3[text()='Sub Category']/ancestor::div[@class='widget_wrap__lfits']"
                    ))
                )
                
                filter_options = sub_category_widget.find_elements(By.CSS_SELECTOR, "div.form-group.sub-category-filter")
                
                for option in filter_options:
                    try:
                        checkbox = option.find_element(By.CSS_SELECTOR, "div.custom-input input[type='checkbox']")
                        label = option.find_element(By.TAG_NAME, "label")
                        
                        name = label.text.strip()
                        if "Private Category" in name:
                            name = name.replace("Private Category", "").strip()
                        
                        subcategories.append({
                            "name": name,
                            "checkbox_id": checkbox.get_attribute("id"),
                            "label_for": label.get_attribute("for"),
                            "label_text": name
                        })
                        
                    except Exception as e:
                        continue
                
                if subcategories:
                    print(f"✅ Strategy 1 SUCCESS: Found {len(subcategories)} subcategories")
                    return subcategories
                    
            except (TimeoutException, NoSuchElementException):
                print("⚠️ Strategy 1 failed, trying alternatives...")
            
            # Strategy 2: Look for 'Sub Category' text anywhere and find nearby elements
            try:
                print("🔄 Trying Strategy 2: Alternative Sub Category search...")
                
                sub_category_headers = self.driver.find_elements(By.XPATH, "//h3[contains(text(), 'Sub Category')]")
                
                for header in sub_category_headers:
                    parent_widget = header.find_element(By.XPATH, "./ancestor::div[contains(@class, 'widget')]")
                    checkboxes = parent_widget.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                    
                    for checkbox in checkboxes:
                        try:
                            label = parent_widget.find_element(By.CSS_SELECTOR, f"label[for='{checkbox.get_attribute('id')}']")
                            name = label.text.strip()
                            
                            if name and len(name) > 1:
                                subcategories.append({
                                    "name": name,
                                    "checkbox_id": checkbox.get_attribute("id"),
                                    "label_for": label.get_attribute("for"),
                                    "label_text": name
                                })
                        except:
                            continue
                
                if subcategories:
                    print(f"✅ Strategy 2 SUCCESS: Found {len(subcategories)} subcategories")
                    return subcategories
                    
            except Exception as e:
                print(f"⚠️ Strategy 2 failed: {e}")
            
            # Strategy 3: Look for any sidebar with checkboxes
            try:
                print("🔄 Trying Strategy 3: Generic sidebar checkbox search...")
                
                sidebar_selectors = [
                    "aside.sidebar",
                    ".sidebar",
                    "[class*='sidebar']",
                    "[class*='widget']"
                ]
                
                for selector in sidebar_selectors:
                    sidebars = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    
                    for sidebar in sidebars:
                        checkboxes = sidebar.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
                        
                        for checkbox in checkboxes:
                            try:
                                checkbox_id = checkbox.get_attribute("id")
                                if checkbox_id:
                                    label = sidebar.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                                    name = label.text.strip()
                                    
                                    # Filter out non-category items
                                    if (name and len(name) > 1 and 
                                        not any(skip in name.lower() for skip in ['search', 'filter', 'sort', 'view'])):
                                        
                                        subcategories.append({
                                            "name": name,
                                            "checkbox_id": checkbox_id,
                                            "label_for": label.get_attribute("for"),
                                            "label_text": name
                                        })
                            except:
                                continue
                
                if subcategories:
                    # Remove duplicates
                    seen = set()
                    unique_subcategories = []
                    for sub in subcategories:
                        if sub['name'] not in seen:
                            seen.add(sub['name'])
                            unique_subcategories.append(sub)
                    
                    print(f"✅ Strategy 3 SUCCESS: Found {len(unique_subcategories)} unique subcategories")
                    return unique_subcategories
                    
            except Exception as e:
                print(f"⚠️ Strategy 3 failed: {e}")
            
            # Strategy 4: Look for category links in sidebar
            try:
                print("🔄 Trying Strategy 4: Category links search...")
                
                category_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'category') or contains(@href, 'cat')]")
                
                for link in category_links:
                    try:
                        name = link.text.strip()
                        href = link.get_attribute('href')
                        
                        if name and href and 'filecr.com' in href:
                            subcategories.append({
                                "name": name,
                                "url": href,
                                "type": "link"
                            })
                    except:
                        continue
                
                if subcategories:
                    print(f"✅ Strategy 4 SUCCESS: Found {len(subcategories)} category links")
                    return subcategories
                    
            except Exception as e:
                print(f"⚠️ Strategy 4 failed: {e}")
            
            # If all strategies failed, run debug
            print("🔍 All strategies failed, running debug analysis...")
            self.debug_page_structure()
            
            print("❌ No subcategories found with any method")
            return []
            
        except Exception as e:
            print(f"❌ Error getting subcategories: {e}")
            self.debug_page_structure()
            return []
    
    def safe_click_element(self, by, value, max_retries=3):
        """Safely click an element with retry logic for stale elements"""
        for attempt in range(max_retries):
            try:
                element = self.wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].click();", element)
                return True
            except StaleElementReferenceException:
                if attempt < max_retries - 1:
                    print(f"🔄 Stale element detected, retrying... (attempt {attempt + 1})")
                    time.sleep(1)
                    continue
                else:
                    print(f"❌ Failed to click element after {max_retries} attempts")
                    return False
            except TimeoutException:
                print(f"⏰ Timeout waiting for element: {value}")
                return False
            except Exception as e:
                print(f"❌ Error clicking element: {e}")
                return False
    
    def click_subcategory(self, subcategory):
        """Click on a subcategory - UPDATED with better error handling"""
        try:
            print(f"🔄 Attempting to select subcategory: {subcategory['name']}")
            
            # Handle link-type subcategories (from Strategy 4)
            if subcategory.get('type') == 'link' and subcategory.get('url'):
                print(f"🔗 Navigating to category URL: {subcategory['url']}")
                self.driver.get(subcategory['url'])
                time.sleep(3)
                return True
            
            # Method 1: Try by checkbox ID
            if subcategory.get('checkbox_id'):
                checkbox_selector = f"input[id='{subcategory['checkbox_id']}']"
                if self.safe_click_element(By.CSS_SELECTOR, checkbox_selector):
                    time.sleep(3)
                    print(f"✅ Selected subcategory by ID: {subcategory['name']}")
                    return True
            
            # Method 2: Try by label 'for' attribute  
            if subcategory.get('label_for'):
                label_selector = f"label[for='{subcategory['label_for']}']"
                if self.safe_click_element(By.CSS_SELECTOR, label_selector):
                    time.sleep(3)
                    print(f"✅ Selected subcategory by label: {subcategory['name']}")
                    return True
            
            # Method 3: Try by exact label text match
            label_xpath = f"//label[normalize-space(text())='{subcategory['name']}']"
            if self.safe_click_element(By.XPATH, label_xpath):
                time.sleep(3)
                print(f"✅ Selected subcategory by exact label text: {subcategory['name']}")
                return True
            
            # Method 4: Try partial text match
            label_xpath_partial = f"//label[contains(text(), '{subcategory['name'][:10]}')]"
            if self.safe_click_element(By.XPATH, label_xpath_partial):
                time.sleep(3)
                print(f"✅ Selected subcategory by partial text: {subcategory['name']}")
                return True
            
            print(f"❌ Failed to click subcategory: {subcategory['name']}")
            return False
            
        except Exception as e:
            print(f"❌ Error clicking subcategory {subcategory['name']}: {e}")
            return False
    
    def scrape_current_page(self, primary_cat, sub_cat, child_cat=None):
        """Scrape all products from current page"""
        try:
            time.sleep(2)
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find product containers
            products = soup.find_all('div', class_='card_wrap__S35wt')

            if not products:
                print("🔍 DEBUG: No products found with card_wrap__S35wt selector")
                print("📋 Looking for alternative card selectors...")
                
                # Try alternative card selectors
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
            
            page_count = 0
            for product in products:
                try:
                    # Extract URL from the card_icon__mmJ8V link
                    link_elem = product.find('a', class_='card_icon__mmJ8V')
                    
                    if not link_elem:
                        # Fallback: try any link in the card
                        link_elem = product.find('a', href=True)
                    
                    if not link_elem or not link_elem.get('href'):
                        continue
                    
                    url = link_elem.get('href')
                    
                    # Extract title from the img alt attribute
                    title = None
                    img_elem = link_elem.find('img')
                    if img_elem and img_elem.get('alt'):
                        title = img_elem.get('alt').strip()
                    
                    # Fallback title extraction methods
                    if not title:
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
                            title = url.split('/')[-2].replace('-', ' ').title() if '/' in url else "Unknown"
                    
                    # Skip if still no proper title
                    if not title or len(title.strip()) < 3:
                        continue
                    
                    # Clean up title
                    title = ' '.join(title.split())
                    
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
            if self.safe_click_element(By.CSS_SELECTOR, "div.pagination button[aria-label='pagination next']"):
                time.sleep(3)
                return True
            return False
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
        """Main scraping function - UPDATED with better error recovery"""
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
                
                try:
                    # Navigate to primary category
                    print(f"🌐 Navigating to: {primary_cat['url']}")
                    self.driver.get(primary_cat['url'])
                    time.sleep(3)
                    
                    # Get fresh subcategories after navigation
                    subcategories = self.get_subcategories()
                    
                    if not subcategories:
                        print(f"⚠️ No subcategories found for {primary_cat['name']}")
                        # Try to scrape the main category page directly
                        print(f"🔄 Attempting to scrape main category page directly...")
                        total_products = self.scrape_category_with_pagination(primary_cat['name'], "Main Category")
                        
                        if total_products > 0:
                            print(f"✅ Scraped {total_products} products from main category")
                        
                        # Mark as completed
                        self.progress["completed_categories"].append(primary_cat['name'])
                        self.progress["current_primary_index"] = primary_idx + 1
                        self.progress["current_sub_index"] = 0
                        self.save_progress()
                        continue
                    
                    # Start from saved sub-category progress
                    start_sub = self.progress["current_sub_index"] if primary_idx == start_primary else 0
                    
                    for sub_idx in range(start_sub, len(subcategories)):
                        sub_cat = subcategories[sub_idx]
                        
                        print(f"\n  🔸 Processing SUB CATEGORY: {sub_cat['name']} ({sub_idx + 1}/{len(subcategories)})")
                        
                        try:
                            # Click subcategory with retry logic
                            if self.click_subcategory(sub_cat):
                                # Scrape with pagination
                                self.scrape_category_with_pagination(
                                    primary_cat['name'], 
                                    sub_cat['name']
                                )
                                
                                print(f"✅ COMPLETED SUB CATEGORY: {sub_cat['name']}")
                            else:
                                print(f"⚠️ SKIPPED SUB CATEGORY (couldn't click): {sub_cat['name']}")
                            
                            # Update progress after each subcategory
                            self.progress["current_sub_index"] = sub_idx + 1
                            self.save_progress()
                            self.save_data()
                            
                        except Exception as e:
                            print(f"❌ Error processing subcategory {sub_cat['name']}: {e}")
                            # Continue with next subcategory instead of stopping
                            continue
                        
                        time.sleep(2)
                    
                    # Mark primary category as completed
                    self.progress["completed_categories"].append(primary_cat['name'])
                    self.progress["current_primary_index"] = primary_idx + 1
                    self.progress["current_sub_index"] = 0
                    self.save_progress()
                    
                    print(f"🎉 COMPLETED PRIMARY CATEGORY: {primary_cat['name']}")
                    
                except Exception as e:
                    print(f"❌ Error processing primary category {primary_cat['name']}: {e}")
                    # Save progress and continue with next primary category
                    self.progress["current_primary_index"] = primary_idx + 1
                    self.progress["current_sub_index"] = 0
                    self.save_progress()
                    continue
            
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