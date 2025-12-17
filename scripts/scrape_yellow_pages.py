"""
Scrape dental clinic data from Yellow Pages (Yell.com)
"""

import json
import re
import time
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
    from selenium.webdriver.common.keys import Keys
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️  Selenium not available. Install with: pip install selenium webdriver-manager")

class YellowPagesScraper:
    """Scraper for Yellow Pages (Yell.com)"""
    
    def __init__(self):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required. Install with: pip install selenium webdriver-manager")
        
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
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            print("✅ Chrome driver initialized")
        except Exception as e:
            print(f"⚠️  Error with new headless mode: {e}")
            # Try old headless
            chrome_options_old = Options()
            chrome_options_old.add_argument('--headless')
            chrome_options_old.add_argument('--no-sandbox')
            chrome_options_old.add_argument('--disable-dev-shm-usage')
            chrome_options_old.add_argument('--disable-gpu')
            chrome_options_old.binary_location = chrome_options.binary_location
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options_old)
            print("✅ Chrome driver initialized (old headless mode)")
    
    def search_dentists(self, location: str = "London", max_results: int = 50) -> List[Dict]:
        """Search for dentists on Yellow Pages"""
        print(f"\n🔍 Searching Yellow Pages for dentists in {location}...")
        clinics = []
        
        try:
            # Yellow Pages search URL
            url = f"https://www.yell.com/s/dentists-{location.lower().replace(' ', '-')}.html"
            print(f"  Loading: {url}")
            self.driver.get(url)
            
            # Wait for page to load
            time.sleep(5)
            
            # Check if we need to accept cookies
            try:
                cookie_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[id*='accept'], button[class*='accept'], a[href*='accept']"))
                )
                cookie_button.click()
                time.sleep(2)
                print("  Accepted cookies")
            except:
                pass
            
            # Scroll to load more results
            print("  Scrolling to load results...")
            for i in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Check page title
            try:
                page_title = self.driver.title
                print(f"  Page title: {page_title}")
            except:
                pass
            
            # Look for business listings
            print("  Looking for business listings...")
            
            # Wait a bit more for dynamic content
            time.sleep(3)
            
            # Yellow Pages uses various selectors - try many
            listing_selectors = [
                "div[class*='businessCapsule']",
                "div[class*='business-card']",
                "div[class*='listing']",
                "article[class*='business']",
                "div[data-testid*='business']",
                "div[class*='result']",
                "div[class*='capsule']",
                "li[class*='business']",
                "div[class*='company']",
                "div[class*='entry']",
                "div[itemtype*='LocalBusiness']",
                "article",
                "div[class*='card']",
            ]
            
            listings = []
            for selector in listing_selectors:
                try:
                    found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if found:
                        print(f"  Found {len(found)} elements with: {selector}")
                        if len(found) > 2:
                            listings = found
                            print(f"  ✅ Using: {selector}")
                            break
                except:
                    continue
            
            if not listings:
                # Try alternative: look for business names/links
                print("  Trying alternative selectors...")
                alt_selectors = [
                    "h2 a",
                    "h3 a", 
                    "a[class*='business']",
                    "a[href*='/business/']",
                    "a[href*='/dentist/']",
                    "div[class*='title'] a",
                ]
                for selector in alt_selectors:
                    try:
                        found = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if found and len(found) > 2:
                            listings = found
                            print(f"  ✅ Found {len(found)} links with: {selector}")
                            break
                    except:
                        continue
            
            # Debug: save page source
            if not listings:
                print("  ⚠️  No listings found. Saving page source for debugging...")
                try:
                    page_source = self.driver.page_source
                    debug_file = Path("data/yell_page_source.html")
                    debug_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(debug_file, 'w', encoding='utf-8') as f:
                        f.write(page_source)
                    print(f"  Page source saved to: {debug_file}")
                    
                    # Try to find any text that might be clinic names
                    print("  Trying to extract any potential clinic names from page...")
                    all_text_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
                    potential_names = []
                    for elem in all_text_elements[:100]:  # Limit to avoid too much
                        try:
                            text = elem.text.strip()
                            if (len(text) > 10 and len(text) < 100 and
                                text[0].isupper() and
                                ('dental' in text.lower() or 'dentist' in text.lower())):
                                potential_names.append(text)
                        except:
                            continue
                    
                    if potential_names:
                        print(f"  Found {len(potential_names)} potential clinic names")
                        for name in potential_names[:10]:
                            print(f"    - {name}")
                except Exception as e:
                    print(f"  Error saving debug info: {e}")
            
            # Extract clinic info
            print(f"  Extracting data from {len(listings)} listings...")
            for i, listing in enumerate(listings[:max_results]):
                try:
                    clinic = self._extract_listing(listing)
                    if clinic and clinic.get('name') and len(clinic['name']) > 3:
                        # Filter out non-dental businesses
                        name_lower = clinic['name'].lower()
                        text_lower = listing.text.lower()
                        if ('dental' in name_lower or 'dentist' in name_lower or 
                            'dental' in text_lower or 'dentist' in text_lower or
                            'teeth' in text_lower or 'orthodont' in text_lower):
                            clinics.append(clinic)
                            print(f"    ✓ {clinic['name']}")
                except Exception as e:
                    continue
                
                # Be respectful
                if (i + 1) % 10 == 0:
                    time.sleep(1)
            
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
        
        print(f"✅ Found {len(clinics)} dental clinics from Yellow Pages")
        return clinics
    
    def _extract_listing(self, element) -> Optional[Dict]:
        """Extract clinic information from Yellow Pages listing"""
        try:
            text = element.text
            
            # Extract name
            name = ""
            # Try to find name in heading or link
            try:
                name_elem = element.find_element(By.CSS_SELECTOR, "h2, h3, a[class*='business'], a[class*='name']")
                name = name_elem.text.strip()
            except:
                # Try first substantial line
                lines = [l.strip() for l in text.split('\n') if l.strip()]
                for line in lines:
                    if len(line) > 5 and line[0].isupper():
                        name = line
                        break
            
            if not name or len(name) < 3:
                return None
            
            # Extract address
            address = ""
            postcode = None
            
            # Look for postcode first
            postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', text.upper())
            if postcode_match:
                postcode = postcode_match.group(1)
                # Get text before postcode as address
                idx = text.upper().find(postcode)
                if idx > 0:
                    address_text = text[max(0, idx-150):idx + len(postcode)].strip()
                    # Clean up address
                    address_lines = [l.strip() for l in address_text.split('\n') if l.strip()]
                    # Filter out name and other non-address lines
                    address_parts = []
                    for line in address_lines:
                        if (line != name and
                            not re.match(r'^Tel:', line, re.I) and
                            not re.match(r'^Phone:', line, re.I) and
                            len(line) > 3):
                            address_parts.append(line)
                    address = ', '.join(address_parts[-3:])  # Last 3 lines likely address
            
            # Extract phone
            phone = ""
            phone_patterns = [
                r'Tel[:\s]+(\d{5}\s?\d{6})',
                r'Phone[:\s]+(\d{5}\s?\d{6})',
                r'Call[:\s]+(\d{5}\s?\d{6})',
                r'(\d{5}\s?\d{6})',
                r'(\d{4}\s?\d{3}\s?\d{4})',
            ]
            for pattern in phone_patterns:
                match = re.search(pattern, text)
                if match:
                    phone = match.group(1).strip()
                    break
            
            # Also try tel: link
            if not phone:
                try:
                    tel_link = element.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
                    phone = tel_link.get_attribute('href').replace('tel:', '').strip()
                except:
                    pass
            
            # Extract website link
            link = ""
            try:
                link_elem = element.find_element(By.CSS_SELECTOR, "a[href*='http'], a[class*='website'], a[class*='link']")
                link = link_elem.get_attribute('href')
                if link and not link.startswith('http'):
                    link = f"https://www.yell.com{link}"
            except:
                pass
            
            # Extract area from address or postcode
            area = ""
            if address:
                # Try to extract area name
                area_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*[A-Z]{1,2}\d', address)
                if area_match:
                    area = area_match.group(1)
            
            # Determine if private (look for keywords)
            is_private = False
            text_lower = text.lower()
            if any(kw in text_lower for kw in ['private', 'cosmetic', 'implant', 'harley street', 'private practice']):
                is_private = True
            
            # Extract services from text
            services = []
            service_keywords = [
                'General Dentistry', 'Implants', 'Cosmetic', 'Orthodontics', 'Invisalign',
                'Teeth Whitening', 'Veneers', 'Root Canal', 'Crown', 'Bridge', 'Dentures',
                'Emergency', 'Children', 'Pediatric', 'Oral Surgery', 'Periodontics'
            ]
            for service in service_keywords:
                if service.lower() in text_lower:
                    services.append(service)
            
            # Extract languages
            languages = ['English']  # Default
            language_keywords = [
                'Spanish', 'French', 'German', 'Italian', 'Portuguese',
                'Polish', 'Arabic', 'Urdu', 'Hindi', 'Punjabi', 'Chinese'
            ]
            for lang in language_keywords:
                if lang.lower() in text_lower:
                    languages.append(lang)
            
            return {
                'name': name,
                'address': address if address else (f"{name}, {postcode}" if postcode else name),
                'phone': phone,
                'link': link,
                'postcode': postcode,
                'area': area,
                'services': services,
                'languages': languages,
                'source': 'Yellow Pages (Yell.com)',
                'private': is_private,
                'nhs': not is_private,
                'emergency': 'emergency' in text_lower,
                'children': 'children' in text_lower or 'pediatric' in text_lower,
                'wheelchair_access': 'wheelchair' in text_lower or 'accessible' in text_lower,
                'parking': 'parking' in text_lower,
                'rating': None,
                'opening_hours': None
            }
        except Exception as e:
            return None
    
    def deduplicate(self, clinics: List[Dict]) -> List[Dict]:
        """Remove duplicate clinics"""
        seen = set()
        unique = []
        
        for clinic in clinics:
            name = clinic.get('name', '').lower().strip()
            phone = clinic.get('phone', '').replace(' ', '').replace('-', '')
            
            identifier = f"{name}:{phone}" if phone else name
            if identifier not in seen and name:
                seen.add(identifier)
                unique.append(clinic)
        
        return unique
    
    def save_results(self):
        """Save results to files"""
        if not self.clinics:
            print("⚠️  No clinics to save")
            return
        
        # Load existing clinics
        existing_file = Path("dentaltrawler/src/clinics.js")
        existing_clinics = []
        if existing_file.exists():
            try:
                content = existing_file.read_text(encoding='utf-8')
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    existing_clinics = json.loads(content[json_start:json_end])
            except:
                pass
        
        # Merge and deduplicate
        all_clinics = existing_clinics + self.clinics
        all_clinics = self.deduplicate(all_clinics)
        
        # Save to JSON
        json_file = Path("data/private_dental_clinics_london.json")
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(all_clinics, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(all_clinics)} total clinics to {json_file}")
        
        # Save to frontend format
        js_file = Path("dentaltrawler/src/clinics.js")
        js_content = "// Private London dental clinic data\n"
        js_content += "export const clinicsData = "
        js_content += json.dumps(all_clinics, indent=2, ensure_ascii=False)
        js_content += ";\n"
        
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Saved to frontend format: {js_file}")
        print(f"   Added {len(self.clinics)} new clinics from Yellow Pages")
    
    def run(self, location: str = "London", max_clinics: int = 50):
        """Main method"""
        print(f"\n{'='*60}")
        print(f"🔍 Scraping Yellow Pages for Dental Clinics in {location}")
        print(f"{'='*60}\n")
        
        clinics = self.search_dentists(location, max_results=max_clinics)
        self.clinics = self.deduplicate(clinics)
        
        if self.clinics:
            self.save_results()
        else:
            print("\n⚠️  No clinics found.")
        
        return self.clinics


def main():
    """Main entry point"""
    if not SELENIUM_AVAILABLE:
        print("❌ Selenium is not installed.")
        print("   Install with: pip install selenium webdriver-manager")
        print("   Also need Chrome/Chromium browser installed")
        return
    
    import sys
    
    location = sys.argv[1] if len(sys.argv) > 1 else "London"
    max_clinics = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    try:
        scraper = YellowPagesScraper()
        clinics = scraper.run(location=location, max_clinics=max_clinics)
        
        if clinics:
            print(f"\n{'='*60}")
            print(f"✅ Complete! Found {len(clinics)} clinics from Yellow Pages")
            print(f"{'='*60}")
            print(f"\nSample results:")
            for i, clinic in enumerate(clinics[:5], 1):
                print(f"\n{i}. {clinic.get('name', 'Unknown')}")
                print(f"   Address: {clinic.get('address', 'N/A')[:60]}...")
                print(f"   Phone: {clinic.get('phone', 'N/A')}")
                print(f"   Services: {', '.join(clinic.get('services', [])[:3])}")
        else:
            print("\n⚠️  No clinics found. The website structure may have changed.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

