"""
Scrape real private dental clinic data from free sources
No API keys required - uses web scraping only
"""

import requests
from bs4 import BeautifulSoup
import json
import re
import time
from typing import List, Dict, Optional
from pathlib import Path

class FreeClinicScraper:
    """Scraper for free sources - no API keys needed"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.clinics = []
    
    def scrape_yell(self, location: str = "London", max_results: int = 50) -> List[Dict]:
        """Scrape Yell.com for private dental clinics"""
        print(f"\n🔍 Scraping Yell.com for private dental clinics in {location}...")
        clinics = []
        
        try:
            # Yell.com search URL
            url = "https://www.yell.com/s/dentists-london.html"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for business listings
                listings = soup.find_all(['article', 'div'], class_=re.compile(r'business|listing|result|card', re.I))
                
                if not listings:
                    # Try alternative selectors
                    listings = soup.find_all('div', {'data-testid': re.compile(r'business|listing', re.I)})
                
                print(f"  Found {len(listings)} potential listings")
                
                for i, listing in enumerate(listings[:max_results]):
                    try:
                        clinic = self._extract_yell_listing(listing)
                        if clinic and clinic.get('name'):
                            # Filter for private clinics (look for keywords)
                            text = listing.get_text().lower()
                            if any(kw in text for kw in ['private', 'cosmetic', 'implant', 'harley']):
                                clinic['private'] = True
                                clinic['nhs'] = False
                                clinics.append(clinic)
                                print(f"    ✓ {clinic['name']}")
                    except Exception as e:
                        continue
                
                time.sleep(2)  # Be respectful
        except Exception as e:
            print(f"  ⚠️  Error scraping Yell: {e}")
        
        print(f"✅ Found {len(clinics)} clinics from Yell.com")
        return clinics
    
    def _extract_yell_listing(self, element) -> Optional[Dict]:
        """Extract clinic info from Yell listing"""
        try:
            # Find name
            name_elem = element.find(['h2', 'h3', 'a'], class_=re.compile(r'name|title|business', re.I))
            if not name_elem:
                name_elem = element.find('a', href=True)
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            if not name:
                return None
            
            # Find address
            address_elem = element.find(['p', 'div', 'span'], class_=re.compile(r'address|location', re.I))
            address = address_elem.get_text(strip=True) if address_elem else ""
            
            # Find phone
            phone_elem = element.find(['a', 'span'], href=re.compile(r'tel:'))
            phone = phone_elem.get('href', '').replace('tel:', '').strip() if phone_elem else ""
            
            # Find link
            link_elem = element.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = f"https://www.yell.com{link}"
            
            # Extract postcode
            postcode = None
            if address:
                postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', address.upper())
                if postcode_match:
                    postcode = postcode_match.group(1)
            
            return {
                'name': name,
                'address': address,
                'phone': phone,
                'link': link,
                'postcode': postcode,
                'services': [],
                'languages': ['English'],
                'source': 'Yell.com',
                'private': True,
                'nhs': False
            }
        except Exception as e:
            return None
    
    def scrape_freeindex(self, location: str = "London", max_results: int = 50) -> List[Dict]:
        """Scrape FreeIndex for dental clinics"""
        print(f"\n🔍 Scraping FreeIndex for dental clinics in {location}...")
        clinics = []
        
        try:
            url = "https://www.freeindex.co.uk/categories/dentists/london"
            
            response = self.session.get(url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for listings
                listings = soup.find_all(['div', 'article'], class_=re.compile(r'listing|business|result', re.I))
                
                print(f"  Found {len(listings)} potential listings")
                
                for listing in listings[:max_results]:
                    try:
                        clinic = self._extract_freeindex_listing(listing)
                        if clinic and clinic.get('name'):
                            clinics.append(clinic)
                            print(f"    ✓ {clinic['name']}")
                    except Exception as e:
                        continue
                
                time.sleep(2)
        except Exception as e:
            print(f"  ⚠️  Error scraping FreeIndex: {e}")
        
        print(f"✅ Found {len(clinics)} clinics from FreeIndex")
        return clinics
    
    def _extract_freeindex_listing(self, element) -> Optional[Dict]:
        """Extract clinic info from FreeIndex listing"""
        try:
            name_elem = element.find(['h2', 'h3', 'a'], class_=re.compile(r'name|title', re.I))
            if not name_elem:
                name_elem = element.find('a', href=True)
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            if not name:
                return None
            
            address_elem = element.find(['p', 'div'], class_=re.compile(r'address', re.I))
            address = address_elem.get_text(strip=True) if address_elem else ""
            
            phone_elem = element.find(['a', 'span'], href=re.compile(r'tel:'))
            phone = phone_elem.get('href', '').replace('tel:', '').strip() if phone_elem else ""
            
            link_elem = element.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            
            postcode = None
            if address:
                postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', address.upper())
                if postcode_match:
                    postcode = postcode_match.group(1)
            
            return {
                'name': name,
                'address': address,
                'phone': phone,
                'link': link,
                'postcode': postcode,
                'services': [],
                'languages': ['English'],
                'source': 'FreeIndex',
                'private': True,
                'nhs': False
            }
        except Exception as e:
            return None
    
    def scrape_nhs_improved(self, location: str = "London", max_results: int = 50) -> List[Dict]:
        """Improved NHS scraping with multiple URL attempts"""
        print(f"\n🔍 Scraping NHS directory (improved method) for {location}...")
        clinics = []
        
        # Try multiple NHS URL patterns
        urls_to_try = [
            "https://www.nhs.uk/service-search/find-a-dentist",
            "https://www.nhs.uk/service-search/find-a-dentist/results/London",
            "https://www.nhs.uk/service-search/find-a-dentist/results?Location=London&ServiceType=Dental",
        ]
        
        for url in urls_to_try:
            try:
                print(f"  Trying: {url}")
                response = self.session.get(url, timeout=15)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Try multiple selectors
                    selectors = [
                        ('div', {'class': re.compile(r'result|listing|card|practice', re.I)}),
                        ('article', {'class': re.compile(r'result|listing', re.I)}),
                        ('li', {'class': re.compile(r'result|listing', re.I)}),
                        ('div', {'data-testid': re.compile(r'result|listing', re.I)}),
                        ('a', {'href': re.compile(r'dentist|dental|practice', re.I)}),
                    ]
                    
                    listings = []
                    for tag, attrs in selectors:
                        found = soup.find_all(tag, attrs)
                        if found:
                            listings = found
                            print(f"    Found {len(found)} results with {tag} selector")
                            break
                    
                    if listings:
                        for listing in listings[:max_results]:
                            try:
                                clinic = self._extract_nhs_listing(listing)
                                if clinic and clinic.get('name'):
                                    clinics.append(clinic)
                                    print(f"    ✓ {clinic['name']}")
                            except Exception as e:
                                continue
                        break  # Success, stop trying other URLs
                
                time.sleep(2)
            except Exception as e:
                print(f"    ⚠️  Error: {e}")
                continue
        
        print(f"✅ Found {len(clinics)} clinics from NHS directory")
        return clinics
    
    def _extract_nhs_listing(self, element) -> Optional[Dict]:
        """Extract clinic info from NHS listing"""
        try:
            name_elem = element.find(['h2', 'h3', 'h4', 'a'], class_=re.compile(r'name|title|heading', re.I))
            if not name_elem:
                name_elem = element.find('a')
            name = name_elem.get_text(strip=True) if name_elem else ""
            
            if not name:
                return None
            
            address_elem = element.find(['p', 'div', 'span'], class_=re.compile(r'address|location', re.I))
            address = address_elem.get_text(strip=True) if address_elem else ""
            
            phone_elem = element.find(['a', 'span'], href=re.compile(r'tel:'))
            phone = phone_elem.get('href', '').replace('tel:', '').strip() if phone_elem else ""
            
            link_elem = element.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = f"https://www.nhs.uk{link}"
            
            postcode = None
            if address:
                postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', address.upper())
                if postcode_match:
                    postcode = postcode_match.group(1)
            
            return {
                'name': name,
                'address': address,
                'phone': phone,
                'link': link,
                'postcode': postcode,
                'services': [],
                'languages': ['English'],
                'source': 'NHS Directory',
                'private': True,
                'nhs': False
            }
        except Exception as e:
            return None
    
    def deduplicate(self, clinics: List[Dict]) -> List[Dict]:
        """Remove duplicates"""
        seen = set()
        unique = []
        
        for clinic in clinics:
            name = clinic.get('name', '').lower().strip()
            phone = clinic.get('phone', '').replace(' ', '').replace('-', '')
            
            identifier = f"{name}:{phone}" if phone else name
            if identifier not in seen:
                seen.add(identifier)
                unique.append(clinic)
        
        return unique
    
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
        
        js_content = "// Private London dental clinic data (scraped from free sources)\n"
        js_content += "export const clinicsData = "
        js_content += json.dumps(self.clinics, indent=2, ensure_ascii=False)
        js_content += ";\n"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Saved to frontend format: {filename}")
    
    def run(self, location: str = "London", max_clinics: int = 50):
        """Main method to scrape from all free sources"""
        print(f"\n{'='*60}")
        print(f"🔍 Scraping Free Sources for Private Dental Clinics in {location}")
        print(f"{'='*60}\n")
        
        all_clinics = []
        
        # Try NHS (improved)
        nhs_clinics = self.scrape_nhs_improved(location, max_results=max_clinics)
        all_clinics.extend(nhs_clinics)
        
        # Try Yell.com
        if len(all_clinics) < max_clinics:
            yell_clinics = self.scrape_yell(location, max_results=max_clinics - len(all_clinics))
            all_clinics.extend(yell_clinics)
        
        # Try FreeIndex
        if len(all_clinics) < max_clinics:
            freeindex_clinics = self.scrape_freeindex(location, max_results=max_clinics - len(all_clinics))
            all_clinics.extend(freeindex_clinics)
        
        # Deduplicate
        print(f"\n🔄 Deduplicating {len(all_clinics)} clinics...")
        self.clinics = self.deduplicate(all_clinics)
        print(f"✅ {len(self.clinics)} unique clinics found")
        
        # Save results
        if self.clinics:
            self.save_to_json()
            self.save_to_frontend_format()
        else:
            print("\n⚠️  No clinics found from free sources.")
            print("   The websites may have changed their structure or blocked scraping.")
        
        return self.clinics


def main():
    """Main entry point"""
    scraper = FreeClinicScraper()
    
    clinics = scraper.run(
        location="London",
        max_clinics=50
    )
    
    if clinics:
        print(f"\n{'='*60}")
        print(f"✅ Complete! Found {len(clinics)} clinics from free sources")
        print(f"{'='*60}")
        print(f"\nSample results:")
        for i, clinic in enumerate(clinics[:5], 1):
            print(f"\n{i}. {clinic.get('name', 'Unknown')}")
            print(f"   Address: {clinic.get('address', 'N/A')}")
            print(f"   Phone: {clinic.get('phone', 'N/A')}")
            print(f"   Source: {clinic.get('source', 'N/A')}")
    else:
        print("\n⚠️  No clinics found. The websites may have:")
        print("   1. Changed their structure")
        print("   2. Blocked automated requests")
        print("   3. Require JavaScript rendering (need Selenium)")
        print("\n   Consider using Selenium for JavaScript-rendered sites.")


if __name__ == "__main__":
    main()

