from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

def inspect_filecr_html():
    """Quick HTML inspector for FileCR website"""
    
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("🔍 Inspecting FileCR HTML structure...")
        
        # Navigate to Windows category
        driver.get("https://filecr.com/ms-windows/")
        time.sleep(5)
        
        print("\n" + "="*50)
        print("FULL PAGE TITLE:", driver.title)
        print("="*50)
        
        # Save full HTML
        with open('filecr_full.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print("📄 Full HTML saved as 'filecr_full.html'")
        
        # Look for sidebar
        print("\n🔍 SEARCHING FOR SIDEBAR ELEMENTS:")
        sidebar_selectors = [
            "aside.sidebar",
            ".sidebar", 
            "[class*='sidebar']",
            "[class*='widget']",
            ".widget_wrap__lfits"
        ]
        
        for selector in sidebar_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"✅ Found {len(elements)} elements: {selector}")
                
                # Save first sidebar element HTML
                #with open(f'sidebar_{selector.replace("[", "").replace("]", "").replace("*", "").replace("=", "").replace("'", "")}.html', 'w', encoding='utf-8') as f:
                safe_selector = selector.replace("[", "")\
                        .replace("]", "")\
                        .replace("*", "")\
                        .replace("=", "")\
                        .replace("'", "")

                filename = f"sidebar_{safe_selector}.html"

                # Now open the file safely
                with open(filename, 'w', encoding='utf-8') as f:

                    f.write(elements[0].get_attribute('outerHTML'))
                print(f"   💾 Saved first element HTML")

                
        
        # Look for text containing key words
        print("\n🔍 SEARCHING FOR KEY TEXT ELEMENTS:")
        key_texts = ["Sub Category", "Category", "Filter", "subcategory"]
        
        for text in key_texts:
            elements = driver.find_elements(By.XPATH, f"//*[contains(text(), '{text}')]")
            print(f"📝 '{text}': {len(elements)} elements found")
            
            for i, elem in enumerate(elements[:3]):
                try:
                    print(f"   {i+1}. {elem.tag_name}: '{elem.text[:100]}...'")
                    if i == 0:  # Save first element's parent HTML
                        parent = elem.find_element(By.XPATH, "./parent::*")
                        with open(f'text_{text.replace(" ", "_").lower()}_parent.html', 'w', encoding='utf-8') as f:
                            f.write(parent.get_attribute('outerHTML'))
                except Exception as e:
                    print(f"   {i+1}. Error getting element info: {e}")
        
        # Look for form elements
        print("\n🔍 SEARCHING FOR FORM ELEMENTS:")
        checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
        print(f"☑️ Checkboxes found: {len(checkboxes)}")
        
        radios = driver.find_elements(By.CSS_SELECTOR, "input[type='radio']")  
        print(f"🔘 Radio buttons found: {len(radios)}")
        
        labels = driver.find_elements(By.TAG_NAME, "label")
        print(f"🏷️ Labels found: {len(labels)}")
        
        if checkboxes:
            print("\n📋 CHECKBOX DETAILS:")
            for i, checkbox in enumerate(checkboxes[:5]):
                try:
                    checkbox_id = checkbox.get_attribute('id')
                    checkbox_name = checkbox.get_attribute('name')
                    print(f"   {i+1}. ID: {checkbox_id}, Name: {checkbox_name}")
                    
                    # Find associated label
                    if checkbox_id:
                        try:
                            label = driver.find_element(By.CSS_SELECTOR, f"label[for='{checkbox_id}']")
                            print(f"      Label: '{label.text}'")
                        except:
                            print(f"      No label found for ID: {checkbox_id}")
                            
                except Exception as e:
                    print(f"   {i+1}. Error: {e}")
        
        print(f"\n✅ Inspection complete! Check the saved HTML files for details.")
        
    except Exception as e:
        print(f"❌ Inspection failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    inspect_filecr_html()