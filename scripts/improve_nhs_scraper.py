"""
Improved NHS Scraper with Better Selectors
Use this after manually inspecting the NHS website structure
"""

import json
import time
import re
from pathlib import Path
from typing import List, Dict, Optional

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium webdriver-manager")

class ImprovedNHSScraper:
    """Improved NHS scraper with configurable selectors"""
    
    def __init__(self):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required")
        
        self.clinics = []
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome driver"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        import shutil
        for binary in ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']:
            binary_path = shutil.which(binary)
            if binary_path and 'snap' not in binary_path:
                chrome_options.binary_location = binary_path
                print(f"✅ Using: {binary}")
                break
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver initialized")
    
    def scrape_with_custom_selectors(self, location: str = "London", selectors_config: Dict = None):
        """Scrape with custom selectors (update these after inspecting the site)"""
        print(f"\n🔍 Scraping NHS for: {location}")
        
        # Default selectors (UPDATE THESE after inspecting the site)
        config = selectors_config or {
            'search_input': "input[type='text'], input[name='location'], #location-input",
            'search_button': "button[type='submit'], button[aria-label*='Search']",
            'practice_listings': "div[class*='practice'], article[class*='result'], div[class*='service-card']",
            'practice_name': "h2, h3, [class*='name'], [class*='title']",
            'practice_address': "[class*='address'], [class*='location']",
            'practice_phone': "[class*='phone'], [href^='tel:']",
            'practice_link': "a[href*='/service/'], a[href*='/dentist/']",
        }
        
        try:
            url = "https://www.nhs.uk/service-search/find-a-dentist"
            self.driver.get(url)
            time.sleep(3)
            
            # Search
            try:
                search_input = self.driver.find_element(By.CSS_SELECTOR, config['search_input'].split(',')[0])
                search_input.clear()
                search_input.send_keys(location)
                time.sleep(2)
                
                # Try to select from suggestions
                try:
                    suggestions = self.driver.find_elements(By.CSS_SELECTOR, "ul[role='listbox'] li, [role='option']")
                    for sug in suggestions:
                        if 'london' in sug.text.lower():
                            sug.click()
                            time.sleep(3)
                            break
                except:
                    pass
                
                # Click search
                try:
                    search_btn = self.driver.find_element(By.CSS_SELECTOR, config['search_button'].split(',')[0])
                    search_btn.click()
                    time.sleep(5)
                except:
                    from selenium.webdriver.common.keys import Keys
                    search_input.send_keys(Keys.RETURN)
                    time.sleep(5)
            except Exception as e:
                print(f"  ⚠️  Search error: {e}")
            
            # Find practice listings
            listings = self.driver.find_elements(By.CSS_SELECTOR, config['practice_listings'].split(',')[0])
            print(f"  Found {len(listings)} potential listings")
            
            # Extract clinic info
            for listing in listings:
                try:
                    clinic = self._extract_with_selectors(listing, config)
                    if clinic and clinic.get('name') and len(clinic['name']) > 5:
                        self.clinics.append(clinic)
                        print(f"    ✓ {clinic['name']}")
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
        finally:
            if self.driver:
                self.driver.quit()
        
        return self.clinics
    
    def _extract_with_selectors(self, element, config: Dict) -> Optional[Dict]:
        """Extract clinic info using configured selectors"""
        try:
            # Name
            name = ""
            for selector in config['practice_name'].split(','):
                try:
                    name_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                    name = name_elem.text.strip()
                    if name:
                        break
                except:
                    continue
            
            if not name:
                return None
            
            # Address
            address = ""
            for selector in config['practice_address'].split(','):
                try:
                    addr_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                    address = addr_elem.text.strip()
                    if address:
                        break
                except:
                    continue
            
            # Phone
            phone = ""
            for selector in config['practice_phone'].split(','):
                try:
                    phone_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                    phone = phone_elem.get_attribute('href') if 'href' in selector else phone_elem.text.strip()
                    if phone:
                        phone = phone.replace('tel:', '').strip()
                        break
                except:
                    continue
            
            # Link
            link = ""
            for selector in config['practice_link'].split(','):
                try:
                    link_elem = element.find_element(By.CSS_SELECTOR, selector.strip())
                    link = link_elem.get_attribute('href')
                    if link and not link.startswith('http'):
                        link = f"https://www.nhs.uk{link}"
                    if link:
                        break
                except:
                    continue
            
            # Extract postcode
            postcode = None
            text = (address + " " + element.text).upper()
            postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', text)
            if postcode_match:
                postcode = postcode_match.group(1)
            
            return {
                'name': name,
                'address': address or name,
                'phone': phone,
                'link': link,
                'postcode': postcode,
                'services': [],
                'languages': ['English'],
                'source': 'NHS Directory (Improved)',
                'private': False,
                'nhs': True
            }
        except:
            return None
    
    def save_results(self):
        """Save results"""
        if not self.clinics:
            return
        
        # Save to JSON
        json_file = Path("data/private_dental_clinics_london.json")
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.clinics, f, indent=2, ensure_ascii=False)
        
        # Save to frontend
        js_file = Path("dentaltrawler/src/clinics.js")
        js_content = "// Private London dental clinic data\n"
        js_content += "export const clinicsData = "
        js_content += json.dumps(self.clinics, indent=2, ensure_ascii=False)
        js_content += ";\n"
        
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"\n✅ Saved {len(self.clinics)} clinics")

def main():
    """Main entry point"""
    print("="*60)
    print("Improved NHS Scraper")
    print("="*60)
    print("\nTo use this:")
    print("1. Inspect NHS website in browser")
    print("2. Find the actual selectors for practice listings")
    print("3. Update selectors_config in this script")
    print("4. Run again\n")
    
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium not installed")
        return
    
    scraper = ImprovedNHSScraper()
    
    # Custom selectors (UPDATE THESE after inspecting the site)
    custom_selectors = {
        'search_input': "input[type='text']",
        'search_button': "button[type='submit']",
        'practice_listings': "div[class*='practice'], article[class*='result']",
        'practice_name': "h2, h3",
        'practice_address': "p, div[class*='address']",
        'practice_phone': "a[href^='tel:']",
        'practice_link': "a[href*='/service/']",
    }
    
    clinics = scraper.scrape_with_custom_selectors("London", custom_selectors)
    scraper.save_results()
    
    if clinics:
        print(f"\n✅ Found {len(clinics)} clinics")
    else:
        print("\n⚠️  No clinics found. Update selectors_config with correct selectors.")

if __name__ == "__main__":
    main()

