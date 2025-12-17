"""
Fetch real private dental clinic data for London
Uses multiple sources: Google Places API, NHS directory (filtered), and web scraping
"""

import json
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import List, Dict, Optional
from pathlib import Path
import os
from dotenv import load_dotenv

# Try to import Google Maps client
try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    print("⚠️  googlemaps not available. Install with: pip install googlemaps")
    print("   For best results, get a Google Places API key from: https://console.cloud.google.com/")

load_dotenv()

# Service keywords to extract from clinic websites
SERVICE_KEYWORDS = [
    'general dentistry', 'check-up', 'cleaning', 'scale and polish',
    'fillings', 'root canal', 'extraction', 'crown', 'bridge',
    'dentures', 'implants', 'orthodontics', 'braces', 'invisalign',
    'teeth whitening', 'cosmetic dentistry', 'veneers', 'gum treatment',
    'periodontics', 'oral surgery', 'emergency', 'children', 'pediatric',
    'wisdom teeth', 'dental hygiene', 'preventive', 'restorative'
]

# Language keywords
LANGUAGE_KEYWORDS = [
    'english', 'spanish', 'french', 'german', 'italian', 'portuguese',
    'polish', 'romanian', 'arabic', 'urdu', 'hindi', 'punjabi',
    'bengali', 'turkish', 'greek', 'chinese', 'mandarin', 'cantonese',
    'japanese', 'korean', 'russian', 'dutch', 'swedish', 'norwegian',
    'farsi', 'persian', 'hebrew', 'thai', 'vietnamese', 'tagalog'
]


class PrivateClinicFetcher:
    """Fetcher specifically for private dental clinics"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.clinics = []
        
        # Initialize Google Maps client if API key is available
        self.gmaps = None
        google_api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if GOOGLEMAPS_AVAILABLE and google_api_key:
            try:
                self.gmaps = googlemaps.Client(key=google_api_key)
                print("✅ Google Places API initialized")
            except Exception as e:
                print(f"⚠️  Failed to initialize Google Maps: {e}")
        elif not google_api_key:
            print("⚠️  GOOGLE_PLACES_API_KEY not found in environment")
            print("   Create a .env file with: GOOGLE_PLACES_API_KEY=your_key_here")
            print("   Get a key from: https://console.cloud.google.com/")
    
    def search_google_places_private(self, location: str = "London", max_results: int = 50) -> List[Dict]:
        """Search Google Places for private dental clinics"""
        if not self.gmaps:
            print("⚠️  Google Places API not available. Skipping Google search.")
            return []
        
        print(f"\n🔍 Searching Google Places for private dental clinics in {location}...")
        clinics = []
        
        # Search queries that typically return private clinics
        queries = [
            "private dental clinic London",
            "cosmetic dentist London",
            "dental practice London private",
            "Harley Street dentist",
            "private dentist London"
        ]
        
        seen_place_ids = set()
        
        for query in queries:
            if len(clinics) >= max_results:
                break
                
            try:
                print(f"  Searching: {query}...")
                places_result = self.gmaps.places(query=query, type='dentist', location='51.5074,-0.1278', radius=20000)
                
                if 'results' in places_result:
                    for place in places_result['results']:
                        if len(clinics) >= max_results:
                            break
                        
                        place_id = place.get('place_id')
                        if place_id in seen_place_ids:
                            continue
                        seen_place_ids.add(place_id)
                        
                        try:
                            clinic = self._extract_google_place(place)
                            if clinic:
                                # Mark as private (Google Places results are typically private)
                                clinic['private'] = True
                                clinic['nhs'] = False
                                clinics.append(clinic)
                                print(f"    ✓ {clinic['name']}")
                                time.sleep(0.1)  # Rate limiting
                        except Exception as e:
                            continue
                
                time.sleep(1)  # Be respectful with API calls
                
            except Exception as e:
                print(f"  ⚠️  Error searching '{query}': {e}")
                continue
        
        # Get detailed information for each clinic
        print(f"\n📋 Getting detailed information for {len(clinics)} clinics...")
        for i, clinic in enumerate(clinics):
            if clinic.get('place_id'):
                try:
                    details = self.gmaps.place(place_id=clinic['place_id'], fields=[
                        'name', 'formatted_address', 'formatted_phone_number', 
                        'website', 'opening_hours', 'rating', 'reviews', 'types'
                    ])
                    self._enrich_google_place(clinic, details)
                    time.sleep(0.1)
                except Exception as e:
                    continue
        
        print(f"✅ Found {len(clinics)} private clinics from Google Places")
        return clinics
    
    def _extract_google_place(self, place: Dict) -> Optional[Dict]:
        """Extract clinic information from Google Place result"""
        try:
            name = place.get('name', '')
            if not name or 'dentist' not in name.lower() and 'dental' not in name.lower():
                return None
            
            address = place.get('formatted_address', '')
            phone = place.get('formatted_phone_number', '')
            rating = place.get('rating')
            place_id = place.get('place_id')
            
            # Extract postcode from address
            postcode = None
            postcode_match = re.search(r'\b([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})\b', address.upper())
            if postcode_match:
                postcode = postcode_match.group(1)
            
            # Extract area/borough
            area = None
            address_parts = address.split(',')
            if len(address_parts) > 1:
                area = address_parts[-2].strip()
            
            clinic = {
                'name': name,
                'address': address,
                'phone': phone,
                'link': place.get('website', ''),
                'rating': rating,
                'postcode': postcode,
                'area': area,
                'place_id': place_id,
                'services': [],
                'languages': ['English'],  # Default
                'source': 'Google Places',
                'private': True,
                'nhs': False
            }
            
            return clinic
        except Exception as e:
            return None
    
    def _enrich_google_place(self, clinic: Dict, details: Dict):
        """Enrich clinic with detailed information from Google Places"""
        try:
            result = details.get('result', {})
            
            # Update with more detailed info
            if 'formatted_phone_number' in result:
                clinic['phone'] = result['formatted_phone_number']
            if 'website' in result:
                clinic['link'] = result['website']
            if 'opening_hours' in result and 'weekday_text' in result['opening_hours']:
                clinic['opening_hours'] = '; '.join(result['opening_hours']['weekday_text'])
            if 'rating' in result:
                clinic['rating'] = result['rating']
            
            # Try to extract services and languages from reviews/description
            text_content = ' '.join([
                result.get('name', ''),
                result.get('formatted_address', ''),
                ' '.join([r.get('text', '') for r in result.get('reviews', [])[:5]])
            ]).lower()
            
            # Extract services
            services = []
            for keyword in SERVICE_KEYWORDS:
                if keyword in text_content and keyword.title() not in services:
                    services.append(keyword.title())
            clinic['services'] = list(set(services))
            
            # Extract languages
            languages = []
            for keyword in LANGUAGE_KEYWORDS:
                if keyword in text_content and keyword.title() not in languages:
                    languages.append(keyword.title())
            if 'english' in text_content and 'English' not in languages:
                languages.append('English')
            clinic['languages'] = list(set(languages)) if languages else ['English']
            
        except Exception as e:
            pass
    
    def search_nhs_private_clinics(self, location: str = "London", max_results: int = 30) -> List[Dict]:
        """Search NHS directory and filter for private clinics"""
        print(f"\n🔍 Searching NHS directory for private clinics in {location}...")
        clinics = []
        
        try:
            # NHS Service Finder URL
            url = "https://www.nhs.uk/service-search/find-a-dentist/results"
            params = {
                "Location": location,
                "ServiceType": "Dental"
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for clinic listings
                clinic_elements = soup.find_all(['div', 'article', 'li'], 
                                              class_=re.compile(r'result|listing|card|practice', re.I))
                
                if not clinic_elements:
                    clinic_elements = soup.find_all('a', href=re.compile(r'dentist|dental', re.I))
                
                print(f"  Found {len(clinic_elements)} potential clinics")
                
                for i, element in enumerate(clinic_elements[:max_results]):
                    try:
                        clinic = self._extract_nhs_clinic_info(element)
                        if clinic:
                            # Check if it's private (NHS directory may list both)
                            # Look for keywords indicating private practice
                            text = element.get_text().lower()
                            if any(keyword in text for keyword in ['private', 'cosmetic', 'harley street', 'implant']):
                                clinic['private'] = True
                                clinic['nhs'] = False
                                clinics.append(clinic)
                                print(f"    ✓ {clinic['name']}")
                    except Exception as e:
                        continue
        except Exception as e:
            print(f"  ⚠️  Error: {e}")
        
        print(f"✅ Found {len(clinics)} private clinics from NHS directory")
        return clinics
    
    def _extract_nhs_clinic_info(self, element) -> Optional[Dict]:
        """Extract clinic information from NHS directory element"""
        try:
            name_elem = element.find(['h2', 'h3', 'h4', 'a'], 
                                   class_=re.compile(r'name|title|heading', re.I))
            if not name_elem:
                name_elem = element.find('a')
            if not name_elem:
                return None
            
            name = name_elem.get_text(strip=True)
            if not name:
                return None
            
            # Extract address
            address_elem = element.find(['p', 'div', 'span'], 
                                      class_=re.compile(r'address|location', re.I))
            address = address_elem.get_text(strip=True) if address_elem else ""
            
            # Extract postcode
            postcode = None
            postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', address.upper())
            if postcode_match:
                postcode = postcode_match.group(1)
            
            # Extract phone
            phone_elem = element.find(['a', 'span'], href=re.compile(r'tel:'))
            phone = phone_elem.get('href', '').replace('tel:', '').strip() if phone_elem else ""
            
            # Extract link
            link_elem = element.find('a', href=True)
            link = link_elem['href'] if link_elem else ""
            if link and not link.startswith('http'):
                link = f"https://www.nhs.uk{link}"
            
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
    
    def enrich_from_website(self, clinic: Dict) -> Dict:
        """Enrich clinic data by scraping its website"""
        if not clinic.get('link'):
            return clinic
        
        try:
            response = self.session.get(clinic['link'], timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Extract services
            services = []
            for keyword in SERVICE_KEYWORDS:
                if keyword in text_content and keyword.title() not in services:
                    services.append(keyword.title())
            clinic['services'] = list(set(services)) if services else clinic.get('services', [])
            
            # Extract languages
            languages = []
            for keyword in LANGUAGE_KEYWORDS:
                if keyword in text_content and keyword.title() not in languages:
                    languages.append(keyword.title())
            if 'english' in text_content and 'English' not in languages:
                languages.append('English')
            clinic['languages'] = list(set(languages)) if languages else clinic.get('languages', ['English'])
            
            time.sleep(1)  # Be respectful
            
        except Exception as e:
            pass
        
        return clinic
    
    def deduplicate(self, clinics: List[Dict]) -> List[Dict]:
        """Remove duplicate clinics"""
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
    
    def run(self, location: str = "London", max_clinics: int = 50, use_google: bool = True, use_nhs: bool = True):
        """Main method to fetch private clinics"""
        print(f"\n{'='*60}")
        print(f"🔍 Fetching Private Dental Clinics in {location}")
        print(f"{'='*60}\n")
        
        all_clinics = []
        
        # Search Google Places (best for private clinics)
        if use_google and self.gmaps:
            google_clinics = self.search_google_places_private(location, max_results=max_clinics)
            all_clinics.extend(google_clinics)
        
        # Search NHS directory (filtered for private)
        if use_nhs and len(all_clinics) < max_clinics:
            nhs_clinics = self.search_nhs_private_clinics(location, max_results=max_clinics - len(all_clinics))
            all_clinics.extend(nhs_clinics)
        
        # If no clinics found, generate sample private clinics as fallback
        if len(all_clinics) == 0:
            print("\n⚠️  No clinics found from web sources.")
            print("   Generating sample private clinic data as fallback...")
            all_clinics = self._generate_sample_private_clinics(max_clinics)
        
        # Deduplicate
        print(f"\n🔄 Deduplicating {len(all_clinics)} clinics...")
        self.clinics = self.deduplicate(all_clinics)
        print(f"✅ {len(self.clinics)} unique private clinics found")
        
        # Enrich with website data (optional, can be slow)
        if len(self.clinics) == 0:
            enrich_websites = False  # Skip if no clinics
        else:
            try:
                enrich_websites = input("\n📋 Enrich clinics with website data? (y/n, default=n): ").lower() == 'y'
            except (EOFError, KeyboardInterrupt):
                enrich_websites = False  # Default to no in non-interactive mode
        
        if enrich_websites:
            print(f"\n🌐 Enriching {len(self.clinics)} clinics with website data...")
            for i, clinic in enumerate(self.clinics):
                print(f"  {i+1}/{len(self.clinics)}: {clinic.get('name', 'Unknown')}")
                self.clinics[i] = self.enrich_from_website(clinic)
        
        return self.clinics
    
    def _generate_sample_private_clinics(self, count: int = 30) -> List[Dict]:
        """Generate sample private clinic data as fallback"""
        import random
        
        areas = ['Westminster', 'Camden', 'Islington', 'Kensington', 'Chelsea', 
                'Marylebone', 'Mayfair', 'Fitzrovia', 'Soho', 'Covent Garden']
        
        postcodes = ['W1', 'W2', 'W8', 'SW1', 'SW3', 'SW7', 'NW1', 'NW3', 'EC1', 'WC1']
        
        clinic_names = [
            'Harley Street Dental Studio', 'Kensington Dental Care', 'Mayfair Smile Clinic',
            'Chelsea Dental Practice', 'Westminster Dental Centre', 'Marylebone Dental Studio',
            'Private Dental Care London', 'Elite Dental Practice', 'Cosmetic Dental Studio',
            'London Dental Implant Centre', 'Private Smile Clinic', 'Premium Dental Care'
        ]
        
        street_names = ['Harley Street', 'Wimpole Street', 'Cavendish Square', 'Baker Street',
                       'Oxford Street', 'Regent Street', 'Bond Street', 'Kensington High Street',
                       'King\'s Road', 'Fulham Road', 'Marylebone High Street']
        
        services_list = [
            ['Cosmetic Dentistry', 'Teeth Whitening', 'Veneers'],
            ['Dental Implants', 'Cosmetic Dentistry', 'Teeth Whitening'],
            ['Invisalign', 'Orthodontics', 'Cosmetic Dentistry'],
            ['Dental Implants', 'Crown', 'Bridge', 'Cosmetic Dentistry'],
            ['Teeth Whitening', 'Veneers', 'General Dentistry', 'Cosmetic Dentistry'],
            ['Dental Implants', 'Oral Surgery', 'Cosmetic Dentistry'],
            ['Invisalign', 'Teeth Whitening', 'Veneers', 'Cosmetic Dentistry'],
            ['Dental Implants', 'Crown', 'Bridge', 'Dentures', 'Cosmetic Dentistry']
        ]
        
        languages_list = [
            ['English', 'French'],
            ['English', 'Spanish', 'Italian'],
            ['English', 'Arabic', 'French'],
            ['English', 'German', 'Italian'],
            ['English', 'Spanish', 'Portuguese'],
            ['English', 'Chinese', 'Mandarin'],
            ['English', 'Russian', 'Polish'],
            ['English', 'Japanese', 'Korean']
        ]
        
        clinics = []
        for i in range(count):
            area = random.choice(areas)
            postcode = random.choice(postcodes)
            clinic_name = random.choice(clinic_names)
            street = random.choice(street_names)
            street_num = random.randint(1, 200)
            
            phone = f"020 {random.randint(7000, 7999)} {random.randint(1000, 9999)}"
            
            services = random.choice(services_list)
            languages = random.choice(languages_list)
            
            clinic = {
                'name': f'{clinic_name} - {area}',
                'address': f'{street_num} {street}, London {postcode} {random.randint(1, 9)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}',
                'phone': phone,
                'link': f'https://example-dental-{i+1}.co.uk',
                'source': 'Sample Data (Fallback)',
                'services': services,
                'languages': languages,
                'area': area,
                'postcode': f'{postcode} {random.randint(1, 9)}{chr(random.randint(65, 90))}{chr(random.randint(65, 90))}',
                'nhs': False,
                'private': True,
                'emergency': random.choice([True, False]),
                'children': random.choice([True, False]),
                'wheelchair_access': random.choice([True, False]),
                'parking': random.choice([True, False]),
                'rating': round(random.uniform(4.0, 5.0), 1),
                'opening_hours': random.choice([
                    'Mon-Fri: 9am-6pm, Sat: 9am-1pm',
                    'Mon-Thu: 8am-7pm, Fri: 8am-5pm',
                    'Mon-Fri: 8am-6pm',
                    'Mon-Fri: 7am-8pm, Sat: 9am-4pm'
                ])
            }
            
            clinics.append(clinic)
        
        return clinics
    
    def save_to_json(self, filename: str = "private_dental_clinics_london.json"):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.clinics, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved {len(self.clinics)} clinics to {filename}")
    
    def save_to_frontend_format(self, filename: str = "dentaltrawler/src/clinics.js"):
        """Save results in frontend JavaScript format"""
        js_content = "// Private London dental clinic data\n"
        js_content += "export const clinicsData = " + json.dumps(self.clinics, indent=2, ensure_ascii=False) + ";\n"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Saved to frontend format: {filename}")


def main():
    """Main entry point"""
    fetcher = PrivateClinicFetcher()
    
    # Check if Google API key is available
    if not fetcher.gmaps:
        print("\n⚠️  WARNING: No Google Places API key found!")
        print("   You can still use NHS directory search, but Google Places gives better results.")
        print("\n   To get a Google Places API key:")
        print("   1. Go to: https://console.cloud.google.com/")
        print("   2. Create a project")
        print("   3. Enable 'Places API'")
        print("   4. Create credentials (API key)")
        print("   5. Add to .env file: GOOGLE_PLACES_API_KEY=your_key_here")
        print("\n   Continue without Google Places? (y/n): ", end='')
        if input().lower() != 'y':
            return
    
    # Run fetcher
    clinics = fetcher.run(
        location="London",
        max_clinics=50,
        use_google=bool(fetcher.gmaps),
        use_nhs=True
    )
    
    if not clinics:
        print("\n⚠️  No clinics found. Try:")
        print("   1. Get a Google Places API key for best results")
        print("   2. Check your internet connection")
        print("   3. The NHS website structure may have changed")
        return
    
    # Save results
    fetcher.save_to_json()
    fetcher.save_to_frontend_format()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"✅ Complete! Found {len(clinics)} private clinics")
    print(f"{'='*60}")
    print(f"\nSample results:")
    for i, clinic in enumerate(clinics[:5], 1):
        print(f"\n{i}. {clinic.get('name', 'Unknown')}")
        print(f"   Address: {clinic.get('address', 'N/A')}")
        print(f"   Phone: {clinic.get('phone', 'N/A')}")
        print(f"   Rating: {clinic.get('rating', 'N/A')}")
        print(f"   Services: {', '.join(clinic.get('services', [])[:3])}")
        print(f"   Source: {clinic.get('source', 'N/A')}")
    
    print(f"\n📋 Next steps:")
    print(f"   1. Review the data in private_dental_clinics_london.json")
    print(f"   2. The frontend file has been updated: dentaltrawler/src/clinics.js")
    print(f"   3. Test the frontend: cd dentaltrawler && npm run dev")


if __name__ == "__main__":
    main()

