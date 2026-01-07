"""
Scrape dental clinic data from Yell.com (Yellow Pages UK) using requests
No Selenium needed - uses direct HTML parsing
"""

import json
import re
import time
from pathlib import Path
from typing import List, Dict
import requests
from bs4 import BeautifulSoup

class YellScraper:
    """Simple scraper for Yell.com"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-GB,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }
        self.clinics = []

    def search_page(self, location: str, page: int = 1) -> List[Dict]:
        """Scrape a single page of results"""
        # Yell.com URL format
        if page == 1:
            url = f"https://www.yell.com/s/dentists-{location}.html"
        else:
            url = f"https://www.yell.com/s/dentists-{location}-page{page}.html"

        print(f"  📄 Page {page}: {url}")

        try:
            time.sleep(2)  # Be polite
            response = self.session.get(url, timeout=15)

            if response.status_code == 404:
                return []  # No more pages
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'lxml')

            # Find business listings
            listings = soup.find_all('article', class_=re.compile(r'businessCapsule'))
            if not listings:
                listings = soup.find_all('div', class_=re.compile(r'businessCapsule'))
            if not listings:
                # Try alternative selectors
                listings = soup.find_all('div', {'data-testid': re.compile(r'business')})

            clinics = []
            for listing in listings:
                clinic = self.parse_listing(listing)
                if clinic and clinic.get('name'):
                    clinics.append(clinic)

            return clinics

        except requests.exceptions.RequestException as e:
            print(f"    ⚠️  Error: {e}")
            return []

    def parse_listing(self, listing) -> Dict:
        """Parse a single business listing"""
        try:
            # Name
            name_elem = listing.find(['h2', 'h3'], class_=re.compile(r'businessCapsule--name|businessName'))
            if not name_elem:
                name_elem = listing.find('a', class_=re.compile(r'businessCapsule--name'))
            name = name_elem.get_text(strip=True) if name_elem else ''

            # Phone
            phone = None
            phone_elem = listing.find('span', class_=re.compile(r'telephone|phone'))
            if phone_elem:
                phone = phone_elem.get_text(strip=True)
            else:
                # Try finding tel: links
                tel_link = listing.find('a', href=re.compile(r'^tel:'))
                if tel_link:
                    phone = tel_link.get('href', '').replace('tel:', '')

            # Address
            address = None
            addr_elem = listing.find('span', class_=re.compile(r'address'))
            if addr_elem:
                address = addr_elem.get_text(strip=True)
            else:
                addr_elem = listing.find('address')
                if addr_elem:
                    address = addr_elem.get_text(strip=True)

            # Website
            website = None
            website_elem = listing.find('a', class_=re.compile(r'website'))
            if website_elem:
                website = website_elem.get('href')
            else:
                # Look for external links
                for link in listing.find_all('a', href=True):
                    href = link.get('href', '')
                    if href.startswith('http') and 'yell.com' not in href:
                        website = href
                        break

            # Extract postcode from address
            postcode = None
            if address:
                pc_match = re.search(r'([A-Z]{1,2}\d{1,2}[A-Z]?\s*\d[A-Z]{2})', address, re.I)
                if pc_match:
                    postcode = pc_match.group(1).upper()

            # Rating
            rating = None
            rating_elem = listing.find('span', class_=re.compile(r'rating|stars'))
            if rating_elem:
                rating_text = rating_elem.get_text(strip=True)
                rating_match = re.search(r'(\d+\.?\d*)', rating_text)
                if rating_match:
                    rating = float(rating_match.group(1))

            return {
                'name': name,
                'address': address,
                'phone': phone,
                'link': website,
                'postcode': postcode,
                'area': None,
                'services': [],
                'languages': ['English'],
                'source': 'Yell.com',
                'private': True,
                'nhs': 'nhs' in name.lower() if name else False,
                'emergency': False,
                'children': False,
                'wheelchair_access': False,
                'parking': False,
                'rating': rating,
                'opening_hours': None
            }

        except Exception as e:
            print(f"    ⚠️  Parse error: {e}")
            return {}

    def scrape_all(self, location: str = "london", max_pages: int = 20) -> List[Dict]:
        """Scrape all pages for a location"""
        print(f"\n🔍 Scraping Yell.com for dentists in {location}...")

        all_clinics = []
        for page in range(1, max_pages + 1):
            clinics = self.search_page(location, page)
            if not clinics:
                print(f"    No more results at page {page}")
                break
            all_clinics.extend(clinics)
            print(f"    Found {len(clinics)} clinics (total: {len(all_clinics)})")

        return all_clinics

    def save_results(self, clinics: List[Dict]):
        """Save results to file"""
        output_file = Path("data/yell_dentists.json")
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(clinics, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Saved {len(clinics)} clinics to {output_file}")

        # Stats
        with_phone = sum(1 for c in clinics if c.get('phone'))
        with_website = sum(1 for c in clinics if c.get('link'))

        print(f"   📞 With phone: {with_phone}")
        print(f"   🌐 With website: {with_website}")


def main():
    print("="*60)
    print("Yell.com (Yellow Pages UK) Scraper")
    print("="*60)

    # London areas to scrape
    areas = [
        "london",
        "north-london",
        "south-london",
        "east-london",
        "west-london",
        "central-london",
    ]

    all_clinics = []
    scraper = YellScraper()

    for area in areas:
        clinics = scraper.scrape_all(area, max_pages=10)
        all_clinics.extend(clinics)
        print(f"  Total so far: {len(all_clinics)}")

    # Deduplicate by name + phone
    seen = set()
    unique = []
    for c in all_clinics:
        key = f"{c.get('name', '').lower()}:{c.get('phone', '')}"
        if key not in seen and c.get('name'):
            seen.add(key)
            unique.append(c)

    print(f"\n📊 Deduplicated: {len(all_clinics)} -> {len(unique)}")

    scraper.save_results(unique)

    # Show sample
    print(f"\n{'='*60}")
    print("Sample Results:")
    print("="*60)
    for i, c in enumerate(unique[:10], 1):
        print(f"\n{i}. {c.get('name', 'Unknown')}")
        if c.get('phone'):
            print(f"   📞 {c['phone']}")
        if c.get('address'):
            print(f"   📍 {c['address'][:60]}...")
        if c.get('link'):
            print(f"   🌐 {c['link']}")


if __name__ == "__main__":
    main()
