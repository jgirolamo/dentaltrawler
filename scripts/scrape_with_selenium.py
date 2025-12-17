"""
Scrape real private dental clinic data using Selenium (for JavaScript-rendered sites)
"""

import json
import re
import time
from typing import List, Dict, Optional
from pathlib import Path

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

class SeleniumClinicScraper:
    """Scraper using Selenium for JavaScript-rendered sites"""
    
    def __init__(self):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium webdriver-manager")
        
        self.clinics = []
        self.driver = None
        self._setup_driver()
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        chrome_options = Options()
        
        # Headless options (try new headless first, fallback to old)
        chrome_options.add_argument('--headless=new')  # New headless mode
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Try to find Chrome/Chromium binary
        chrome_binary = None
        import shutil
        import os
        
        # Check for snap chromium first
        snap_chromium_paths = [
            '/snap/chromium/current/usr/lib/chromium-browser/chromium-browser',
            '/snap/chromium/current/usr/lib/chromium/chromium',
        ]
        for snap_path in snap_chromium_paths:
            if os.path.exists(snap_path):
                chrome_binary = 'chromium (snap)'
                chrome_options.binary_location = snap_path
                print(f"✅ Found Chromium (snap): {snap_path}")
                break
        
        # If not found, try standard locations (prioritize Google Chrome)
        if not chrome_binary:
            for binary in ['google-chrome', 'google-chrome-stable', 'chromium-browser', 'chromium']:
                binary_path = shutil.which(binary)
                if binary_path and 'snap' not in binary_path:  # Skip snap wrappers
                    chrome_binary = binary
                    chrome_options.binary_location = binary_path
                    print(f"✅ Found Chrome/Chromium: {binary} at {binary_path}")
                    break
        
        if not chrome_binary:
            print("⚠️  Chrome/Chromium not found in PATH")
            print("   Install with: sudo apt-get install chromium-browser")
            print("   Or: sudo snap install chromium")
            raise Exception("Chrome/Chromium browser not found")
        
        # Additional options for better compatibility
        chrome_options.add_argument('--disable-setuid-sandbox')
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-plugins')
        # Don't disable JavaScript - NHS site needs it
        # chrome_options.add_argument('--disable-images')
        # chrome_options.add_argument('--single-process')  # Can cause issues
        
        try:
            service = Service(ChromeDriverManager().install())
            service.log_path = '/tmp/chromedriver.log'  # Log to file
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome driver initialized successfully")
        except Exception as e:
            print(f"⚠️  Error with new headless mode: {e}")
            print("   Trying with old headless mode...")
            # Try with old headless - create new options
            chrome_options_old = Options()
            chrome_options_old.add_argument('--headless')
            chrome_options_old.add_argument('--no-sandbox')
            chrome_options_old.add_argument('--disable-dev-shm-usage')
            chrome_options_old.add_argument('--disable-gpu')
            chrome_options_old.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options_old.add_argument('--window-size=1920,1080')
            chrome_options_old.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            chrome_options_old.binary_location = chrome_options.binary_location
            
            # For snap Chromium
            if 'snap' in chrome_options.binary_location.lower() or '/snap/' in chrome_options.binary_location:
                chrome_options_old.add_argument('--disable-setuid-sandbox')
                chrome_options_old.add_argument('--remote-debugging-port=9222')
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=chrome_options_old)
                print("✅ Chrome driver initialized with old headless mode")
            except Exception as e2:
                print(f"❌ Still failed: {e2}")
                print("   Trying without headless (will need display)...")
                # Last resort: try without headless
                chrome_options_no_headless = Options()
                chrome_options_no_headless.add_argument('--no-sandbox')
                chrome_options_no_headless.add_argument('--disable-dev-shm-usage')
                chrome_options_no_headless.binary_location = chrome_options.binary_location
                try:
                    service = Service(ChromeDriverManager().install())
                    self.driver = webdriver.Chrome(service=service, options=chrome_options_no_headless)
                    print("✅ Chrome driver initialized (non-headless mode)")
                except Exception as e3:
                    print(f"❌ All attempts failed: {e3}")
                    print("   Make sure Chrome/Chromium browser is installed")
                    raise
    
    def scrape_nhs_selenium(self, location: str = "London", max_results: int = 50) -> List[Dict]:
        """Scrape NHS directory using Selenium"""
        print(f"\n🔍 Scraping NHS directory with Selenium for {location}...")
        clinics = []
        
        try:
            url = "https://www.nhs.uk/service-search/find-a-dentist"
            print(f"  Loading: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            print("  Waiting for page to load...")
            time.sleep(5)
            
            # Check if page loaded
            try:
                page_title = self.driver.title
                print(f"  Page title: {page_title}")
            except Exception as e:
                print(f"  ⚠️  Could not get page title: {e}")
            
            # Try to find search box and enter location
            try:
                print("  Looking for search form...")
                # Try multiple possible selectors for search box
                search_selectors = [
                    (By.ID, "location-input"),
                    (By.NAME, "location"),
                    (By.CSS_SELECTOR, "input[type='text']"),
                    (By.CSS_SELECTOR, "input[placeholder*='location' i]"),
                    (By.CSS_SELECTOR, "input[placeholder*='postcode' i]"),
                ]
                
                search_box = None
                for by, selector in search_selectors:
                    try:
                        search_box = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((by, selector))
                        )
                        print(f"  Found search box with: {by}={selector}")
                        break
                    except:
                        continue
                
                if search_box:
                    search_box.clear()
                    # Try a full London postcode known to have practices
                    search_term = "SW1A 1AA"  # Westminster postcode
                    search_box.send_keys(search_term)
                    print(f"  Entered search term: {search_term}")
                    time.sleep(3)
                    
                    # Wait for suggestions and select first London result
                    try:
                        suggestions = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul[role='listbox'] li, .autocomplete-suggestion, [role='option']"))
                        )
                        # Find a London-related suggestion
                        london_suggestion = None
                        for sug in suggestions:
                            text = sug.text.lower()
                            if 'london' in text and ('greater london' in text or 'westminster' in text or 'camden' in text):
                                london_suggestion = sug
                                break
                        
                        if london_suggestion:
                            london_suggestion.click()
                            print(f"  Selected London location: {london_suggestion.text}")
                            time.sleep(4)
                        elif suggestions:
                            # Click first suggestion
                            suggestions[0].click()
                            print(f"  Selected first suggestion: {suggestions[0].text}")
                            time.sleep(4)
                    except Exception as e:
                        print(f"  No suggestions found: {e}")
                        # No suggestions, try search button
                        try:
                            search_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button[aria-label*='Search']")
                            search_button.click()
                            print("  Clicked search button")
                            time.sleep(5)
                        except:
                            # Try Enter key
                            from selenium.webdriver.common.keys import Keys
                            search_box.send_keys(Keys.RETURN)
                            print("  Pressed Enter")
                            time.sleep(5)
                    
                    # After search, look for "View practices" or similar link
                    try:
                        view_practices_links = self.driver.find_elements(
                            By.XPATH, 
                            "//a[contains(text(), 'View') or contains(text(), 'practices') or contains(text(), 'dentists')]"
                        )
                        if view_practices_links:
                            view_practices_links[0].click()
                            print("  Clicked 'View practices' link")
                            time.sleep(5)
                    except:
                        pass
            except Exception as e:
                print(f"  ⚠️  Could not interact with search form: {e}")
                print("  Trying direct URL approach...")
                # Try direct URL with area
                try:
                    # Try multiple London areas
                    for area in ["Westminster", "Camden", "Kensington"]:
                        try:
                            direct_url = f"https://www.nhs.uk/service-search/find-a-dentist/results/{area}"
                            self.driver.get(direct_url)
                            time.sleep(5)
                            print(f"  Loaded direct URL: {direct_url}")
                            # Check if we got results
                            page_text = self.driver.page_source
                            if 'practice' in page_text.lower() or 'dentist' in page_text.lower():
                                break
                        except:
                            continue
                except:
                    pass
            
            # Look for clinic listings - NHS website structure
            print("  Looking for clinic listings...")
            
            # Wait a bit more for results to load
            time.sleep(3)
            
            # Try multiple strategies to find actual clinic listings
            listings = []
            
            # Strategy 1: Look for result cards/items (most common)
            selectors = [
                ("div[class*='nhsuk-card']", "NHS card components"),
                ("article[class*='result']", "article results"),
                ("div[class*='practice']", "practice divs"),
                ("div[class*='service']", "service divs"),
                ("li[class*='result']", "list items with results"),
                ("div[data-testid*='result']", "testid results"),
                ("div[class*='listing']", "listing divs"),
            ]
            
            for selector, desc in selectors:
                try:
                    found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found and len(found) > 2:  # More than just navigation
                        listings = found
                        print(f"  Found {len(found)} results with: {desc}")
                        break
                except Exception as e:
                    continue
            
            # Strategy 2: Look for links to individual practice pages
            if not listings or len(listings) < 3:
                print("  Trying alternative: looking for practice detail links...")
                try:
                    # Look for links that go to practice detail pages
                    practice_links = self.driver.find_elements(
                        By.CSS_SELECTOR, 
                        "a[href*='/service/'][href*='dentist'], a[href*='/dentist/'], a[href*='practice']"
                    )
                    if practice_links:
                        print(f"  Found {len(practice_links)} practice detail links")
                        # Visit each link to get details
                        for link in practice_links[:min(10, max_results)]:
                            try:
                                href = link.get_attribute('href')
                                if href and '/service/' in href:
                                    # Get parent element which might have clinic info
                                    parent = link.find_element(By.XPATH, "./..")
                                    clinic = self._extract_listing_info(parent)
                                    if clinic and clinic.get('name') and len(clinic['name']) > 5:
                                        clinic['link'] = href
                                        clinics.append(clinic)
                                        print(f"    ✓ {clinic['name']}")
                            except:
                                continue
                except Exception as e:
                    print(f"  ⚠️  Error with practice links: {e}")
            
            # Strategy 3: Extract from current page listings
            if not clinics:
                print("  Extracting from page listings...")
                for i, listing in enumerate(listings[:max_results]):
                    try:
                        clinic = self._extract_listing_info(listing)
                        if clinic and clinic.get('name'):
                            # Filter out navigation items and short names
                            name = clinic['name'].strip()
                            # Less strict filtering - just exclude obvious navigation
                            if (len(name) > 3 and 
                                name.lower() not in ['dentists', 'find a dentist', 'search', 'none of these', 'try another'] and
                                'try another' not in name.lower()):
                                clinics.append(clinic)
                                print(f"    ✓ {clinic['name']}")
                    except Exception as e:
                        continue
            
            # Strategy 4: Try to find any text that looks like a clinic name
            if not clinics:
                print("  Trying fallback: extracting all potential clinic names...")
                try:
                    # Get all text elements
                    all_text = self.driver.find_elements(By.XPATH, "//*[text()]")
                    seen_names = set()
                    for elem in all_text:
                        try:
                            text = elem.text.strip()
                            # Look for text that might be clinic names
                            if (len(text) > 10 and len(text) < 100 and
                                text[0].isupper() and
                                text.lower() not in ['find a dentist', 'search', 'london', 'greater london'] and
                                not text.startswith('Little London') and
                                not text.startswith('London Apprentice') and
                                text not in seen_names):
                                # Check if it has address-like content
                                if re.search(r'[A-Z]{1,2}\d{1,2}', text) or 'Street' in text or 'Road' in text:
                                    clinic = {
                                        'name': text.split(',')[0].split('\n')[0].strip(),
                                        'address': text,
                                        'phone': '',
                                        'link': '',
                                        'postcode': None,
                                        'area': '',
                                        'services': [],
                                        'languages': ['English'],
                                        'source': 'NHS Directory (Selenium)',
                                        'private': False,
                                        'nhs': True
                                    }
                                    postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', text.upper())
                                    if postcode_match:
                                        clinic['postcode'] = postcode_match.group(1)
                                    
                                    if clinic['name'] and len(clinic['name']) > 5:
                                        clinics.append(clinic)
                                        seen_names.add(text)
                                        print(f"    ✓ {clinic['name']}")
                                        if len(clinics) >= max_results:
                                            break
                        except:
                            continue
                except Exception as e:
                    print(f"  ⚠️  Fallback extraction error: {e}")
            
            if not clinics:
                # Debug: save page source
                print("  No clinics found. Saving page source for debugging...")
                try:
                    with open('/tmp/nhs_page_source.html', 'w') as f:
                        f.write(self.driver.page_source)
                    print("  Page source saved to /tmp/nhs_page_source.html")
                except:
                    pass
            
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
        
        print(f"✅ Found {len(clinics)} clinics from NHS directory")
        return clinics
    
    def _extract_listing_info(self, element) -> Optional[Dict]:
        """Extract clinic info from listing element"""
        try:
            text = element.text
            
            # Extract name - try multiple strategies
            name = ""
            
            # Strategy 1: Look for heading tags
            for tag in ['h1', 'h2', 'h3', 'h4']:
                try:
                    name_elem = element.find_element(By.TAG_NAME, tag)
                    name = name_elem.text.strip()
                    if name and len(name) > 3:
                        break
                except:
                    continue
            
            # Strategy 2: Look for elements with specific classes
            if not name or len(name) < 3:
                name_selectors = [
                    "[class*='name']",
                    "[class*='title']",
                    "[class*='heading']",
                    "[class*='practice-name']",
                    "[class*='clinic-name']",
                ]
                for selector in name_selectors:
                    try:
                        name_elem = element.find_element(By.CSS_SELECTOR, selector)
                        name = name_elem.text.strip()
                        if name and len(name) > 3:
                            break
                    except:
                        continue
            
            # Strategy 3: Get first substantial line of text
            if not name or len(name) < 3:
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                for line in lines:
                    if (len(line) > 5 and 
                        line.lower() not in ['dentists', 'find a dentist', 'search', 'view details', 'get directions'] and
                        not line.startswith('Tel:') and
                        not line.startswith('Phone:')):
                        name = line
                        break
            
            if not name or len(name) < 3:
                return None
            
            # Extract address - look for postcode first, then get surrounding text
            address = ""
            postcode = None
            postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', text.upper())
            if postcode_match:
                postcode = postcode_match.group(1)
                # Get address lines before postcode
                idx = text.upper().find(postcode)
                if idx > 0:
                    # Get up to 100 chars before postcode
                    address_start = max(0, idx - 100)
                    address_text = text[address_start:idx + len(postcode)].strip()
                    # Clean up address
                    address_lines = [l.strip() for l in address_text.split('\n') if l.strip()]
                    # Filter out name and phone
                    address_parts = []
                    for line in address_lines:
                        if (not re.match(r'^Tel:', line, re.I) and
                            not re.match(r'^Phone:', line, re.I) and
                            line != name and
                            len(line) > 3):
                            address_parts.append(line)
                    address = ', '.join(address_parts[-3:])  # Last 3 lines likely address
            
            # Extract phone - multiple patterns
            phone = ""
            phone_patterns = [
                r'Tel[:\s]+(\d{5}\s?\d{6})',
                r'Phone[:\s]+(\d{5}\s?\d{6})',
                r'(\d{5}\s?\d{6})',
                r'(\d{4}\s?\d{3}\s?\d{4})',
                r'(\d{3}\s?\d{3}\s?\d{4})',
            ]
            for pattern in phone_patterns:
                phone_match = re.search(pattern, text)
                if phone_match:
                    phone = phone_match.group(1).strip()
                    break
            
            # Extract link
            link = ""
            try:
                link_elem = element.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href")
                if link and not link.startswith('http'):
                    link = f"https://www.nhs.uk{link}"
            except:
                pass
            
            # Extract area from address or name
            area = ""
            if address:
                # Try to extract area (usually before postcode)
                area_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[A-Z]{1,2}\d', address)
                if area_match:
                    area = area_match.group(1)
            
            # Determine if private (look for keywords)
            is_private = False
            text_lower = text.lower()
            if any(kw in text_lower for kw in ['private', 'cosmetic', 'implant', 'harley street', 'private practice']):
                is_private = True
            
            return {
                'name': name,
                'address': address if address else (f"{name}, {postcode}" if postcode else name),
                'phone': phone,
                'link': link,
                'postcode': postcode,
                'area': area,
                'services': [],
                'languages': ['English'],
                'source': 'NHS Directory (Selenium)',
                'private': is_private,
                'nhs': not is_private
            }
        except Exception as e:
            return None
    
    def save_to_json(self, filename: str = "data/private_dental_clinics_london.json"):
        """Save to JSON"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.clinics, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(self.clinics)} clinics to {filename}")
    
    def save_to_frontend_format(self, filename: str = "dentaltrawler/src/clinics.js"):
        """Save to frontend JavaScript format"""
        output_path = Path(filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        js_content = "// Private London dental clinic data (scraped with Selenium)\n"
        js_content += "export const clinicsData = "
        js_content += json.dumps(self.clinics, indent=2, ensure_ascii=False)
        js_content += ";\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Saved to frontend format: {filename}")
    
    def run(self, location: str = "London", max_clinics: int = 50):
        """Main method"""
        print(f"\n{'='*60}")
        print(f"🔍 Scraping with Selenium for Private Dental Clinics in {location}")
        print(f"{'='*60}\n")
        
        clinics = self.scrape_nhs_selenium(location, max_results=max_clinics)
        self.clinics = clinics
        
        if self.clinics:
            self.save_to_json()
            self.save_to_frontend_format()
        else:
            print("\n⚠️  No clinics found.")
        
        return self.clinics


def main():
    """Main entry point"""
    if not SELENIUM_AVAILABLE:
        print("\n❌ Selenium is not installed.")
        print("   Install with: pip install selenium webdriver-manager")
        return
    
    try:
        scraper = SeleniumClinicScraper()
        clinics = scraper.run(location="London", max_clinics=50)
        
        if clinics:
            print(f"\n{'='*60}")
            print(f"✅ Complete! Found {len(clinics)} clinics")
            print(f"{'='*60}")
            for i, clinic in enumerate(clinics[:5], 1):
                print(f"\n{i}. {clinic.get('name', 'Unknown')}")
                print(f"   Address: {clinic.get('address', 'N/A')}")
                print(f"   Phone: {clinic.get('phone', 'N/A')}")
        else:
            print("\n⚠️  No clinics found. The website structure may have changed.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. Chrome browser is installed")
        print("2. Selenium is installed: pip install selenium webdriver-manager")


if __name__ == "__main__":
    main()

