"""
Fetch dental clinic data using Foursquare Places API
Similar to Yelp - provides business listings with ratings
"""

import json
import requests
import re
from pathlib import Path
from typing import List, Dict
import os
from dotenv import load_dotenv
import time

load_dotenv()

class FoursquareAPIClient:
    """Client for Foursquare Places API"""
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv('FOURSQUARE_API_KEY')
        self.api_secret = api_secret or os.getenv('FOURSQUARE_API_SECRET')
        
        if not self.api_key:
            raise ValueError("FOURSQUARE_API_KEY not found. Set it in .env file.")
        
        # Foursquare uses API version
        self.api_version = "20240101"
        self.base_url = "https://api.foursquare.com/v3"
        self.headers = {
            'Authorization': self.api_key,
            'Accept': 'application/json'
        }
    
    def search_places(self, query: str = "dentist", location: str = "London", limit: int = 50) -> List[Dict]:
        """Search for places using Foursquare API"""
        print(f"\n🔍 Searching Foursquare for {query} in {location}...")
        
        url = f"{self.base_url}/places/search"
        params = {
            'query': query,
            'near': location,
            'limit': min(limit, 50),
            'categories': '16000'  # Health & Medical Services
        }
        
        all_places = []
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            places = data.get('results', [])
            
            print(f"  Found {len(places)} places")
            all_places.extend(places)
            
            # Rate limiting
            time.sleep(1)
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  API Error: {e}")
        
        return all_places[:limit]
    
    def get_place_details(self, fsq_id: str) -> Dict:
        """Get detailed information about a place"""
        url = f"{self.base_url}/places/{fsq_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error getting details: {e}")
            return {}
    
    def convert_to_clinic_format(self, place: Dict) -> Dict:
        """Convert Foursquare place data to clinic format"""
        location = place.get('location', {})
        address_parts = location.get('formatted_address', '').split(',')
        address = location.get('formatted_address', '')
        
        # Extract postcode
        postcode = None
        for part in reversed(address_parts):
            postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', part.upper())
            if postcode_match:
                postcode = postcode_match.group(1)
                break
        
        # Extract area
        area = location.get('locality') or location.get('region')
        
        # Get categories
        categories = place.get('categories', [])
        services = [cat.get('name', '') for cat in categories if cat.get('name')]
        
        # Get contact info
        contact = place.get('tel', '') or place.get('phone', '')
        
        return {
            'name': place.get('name', ''),
            'address': address,
            'phone': contact,
            'link': place.get('website', ''),
            'postcode': postcode,
            'area': area,
            'services': services,
            'languages': ['English'],
            'source': 'Foursquare API',
            'private': True,
            'nhs': False,
            'emergency': False,
            'children': False,
            'wheelchair_access': False,
            'parking': False,
            'rating': place.get('rating'),
            'opening_hours': None
        }
    
    def save_results(self, clinics: List[Dict]):
        """Save results to files"""
        if not clinics:
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
        all_clinics = existing_clinics + clinics
        seen = set()
        unique = []
        for clinic in all_clinics:
            name = clinic.get('name', '').lower().strip()
            phone = clinic.get('phone') or ''
            phone = phone.replace(' ', '').replace('-', '') if phone else ''
            identifier = f"{name}:{phone}" if phone else name
            if identifier not in seen and name:
                seen.add(identifier)
                unique.append(clinic)
        
        # Save to JSON
        json_file = Path("data/private_dental_clinics_london.json")
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(unique, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(unique)} total clinics to {json_file}")
        
        # Save to frontend format
        js_file = Path("dentaltrawler/src/clinics.js")
        js_content = "// Private London dental clinic data\n"
        js_content += "export const clinicsData = "
        js_content += json.dumps(unique, indent=2, ensure_ascii=False)
        js_content += ";\n"
        
        with open(js_file, 'w', encoding='utf-8') as f:
            f.write(js_content)
        print(f"✅ Saved to frontend format: {js_file}")
        print(f"   Added {len(clinics)} new clinics from Foursquare API")


def main():
    """Main entry point"""
    import sys
    
    print("="*60)
    print("Foursquare Places API Client")
    print("="*60)
    print("\nGet your API key from: https://developer.foursquare.com/")
    print("Add to .env file: FOURSQUARE_API_KEY=your_key_here\n")
    
    # Check for API key
    api_key = os.getenv('FOURSQUARE_API_KEY')
    if not api_key:
        print("❌ FOURSQUARE_API_KEY not found!")
        print("\nTo get an API key:")
        print("1. Go to https://developer.foursquare.com/")
        print("2. Sign up / Log in")
        print("3. Create an app")
        print("4. Copy your API key")
        print("5. Add to .env file: FOURSQUARE_API_KEY=your_key_here")
        return
    
    location = sys.argv[1] if len(sys.argv) > 1 else "London"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    try:
        client = FoursquareAPIClient(api_key=api_key)
        
        # Search for dentists
        places = client.search_places(query="dentist", location=location, limit=limit)
        
        if not places:
            print("⚠️  No places found")
            return
        
        # Convert to clinic format
        print(f"\n📋 Converting {len(places)} places to clinic format...")
        clinics = []
        for place in places:
            clinic = client.convert_to_clinic_format(place)
            if clinic.get('name'):
                clinics.append(clinic)
                print(f"    ✓ {clinic['name']}")
        
        if clinics:
            client.save_results(clinics)
            print(f"\n{'='*60}")
            print(f"✅ Complete! Found {len(clinics)} clinics from Foursquare")
            print(f"{'='*60}")
            print(f"\nSample results:")
            for i, clinic in enumerate(clinics[:5], 1):
                print(f"\n{i}. {clinic.get('name', 'Unknown')}")
                print(f"   Address: {clinic.get('address', 'N/A')[:60]}...")
                print(f"   Phone: {clinic.get('phone', 'N/A')}")
                print(f"   Rating: {clinic.get('rating', 'N/A')}")
        else:
            print("⚠️  No clinics converted")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

