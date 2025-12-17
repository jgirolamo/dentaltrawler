"""
Fetch dental clinic data using OpenStreetMap Nominatim API
FREE - No API key needed!
Similar to Yelp but open-source
"""

import json
import requests
import time
import re
from pathlib import Path
from typing import List, Dict

class OpenStreetMapClient:
    """Client for OpenStreetMap Nominatim API (free, no key needed)"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            'User-Agent': 'DentalTrawler/1.0'  # Required by OSM
        }
    
    def search_places(self, query: str = "dentist", location: str = "London", limit: int = 50) -> List[Dict]:
        """Search for places using OpenStreetMap"""
        print(f"\n🔍 Searching OpenStreetMap for {query} in {location}...")
        print("  (Free API - no key needed, but rate limited to 1 req/sec)")
        
        url = f"{self.base_url}/search"
        params = {
            'q': f"{query} {location}",
            'format': 'json',
            'limit': min(limit, 50),
            'addressdetails': 1,
            'extratags': 1
        }
        
        all_places = []
        
        try:
            # Rate limiting - OSM requires max 1 request per second
            time.sleep(1)
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            places = response.json()
            
            print(f"  Found {len(places)} places")
            all_places.extend(places)
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  API Error: {e}")
        
        return all_places[:limit]
    
    def get_place_details(self, place_id: str) -> Dict:
        """Get detailed information about a place"""
        url = f"{self.base_url}/details"
        params = {
            'place_id': place_id,
            'format': 'json',
            'addressdetails': 1
        }
        
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error getting details: {e}")
            return {}
    
    def convert_to_clinic_format(self, place: Dict) -> Dict:
        """Convert OSM place data to clinic format"""
        address = place.get('address', {})
        
        # Build address
        address_parts = []
        if address.get('road'):
            address_parts.append(address['road'])
        if address.get('house_number'):
            address_parts.insert(0, address['house_number'])
        if address.get('city') or address.get('town'):
            address_parts.append(address.get('city') or address.get('town'))
        if address.get('postcode'):
            address_parts.append(address['postcode'])
        
        full_address = ', '.join(address_parts) if address_parts else place.get('display_name', '')
        
        # Extract postcode
        postcode = address.get('postcode')
        
        # Extract area
        area = address.get('suburb') or address.get('city') or address.get('town')
        
        # Get name
        name = place.get('name') or place.get('display_name', '').split(',')[0]
        
        # Extract phone from tags
        tags = place.get('extratags', {})
        phone = tags.get('phone') or tags.get('contact:phone')
        
        # Extract website
        link = tags.get('website') or tags.get('contact:website')
        
        # Get categories/types
        place_type = place.get('type', '')
        category = place.get('class', '')
        
        return {
            'name': name,
            'address': full_address,
            'phone': phone,
            'link': link,
            'postcode': postcode,
            'area': area,
            'services': [],
            'languages': ['English'],
            'source': 'OpenStreetMap (Free)',
            'private': True,
            'nhs': False,
            'emergency': False,
            'children': False,
            'wheelchair_access': False,
            'parking': False,
            'rating': None,
            'opening_hours': tags.get('opening_hours')
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
        print(f"   Added {len(clinics)} new clinics from OpenStreetMap")


def main():
    """Main entry point"""
    import sys
    
    print("="*60)
    print("OpenStreetMap Nominatim API Client")
    print("="*60)
    print("\n✅ FREE - No API key needed!")
    print("⚠️  Rate limited to 1 request per second\n")
    
    location = sys.argv[1] if len(sys.argv) > 1 else "London"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    try:
        client = OpenStreetMapClient()
        
        # Search for dentists
        places = client.search_places(query="dentist", location=location, limit=limit)
        
        if not places:
            print("⚠️  No places found")
            return
        
        # Convert to clinic format
        print(f"\n📋 Converting {len(places)} places to clinic format...")
        clinics = []
        for i, place in enumerate(places):
            clinic = client.convert_to_clinic_format(place)
            if clinic.get('name'):
                clinics.append(clinic)
                print(f"    ✓ {clinic['name']}")
            
            # Rate limiting
            if (i + 1) % 10 == 0:
                time.sleep(1)
        
        if clinics:
            client.save_results(clinics)
            print(f"\n{'='*60}")
            print(f"✅ Complete! Found {len(clinics)} clinics from OpenStreetMap")
            print(f"{'='*60}")
            print(f"\nSample results:")
            for i, clinic in enumerate(clinics[:5], 1):
                print(f"\n{i}. {clinic.get('name', 'Unknown')}")
                print(f"   Address: {clinic.get('address', 'N/A')[:60]}...")
                print(f"   Phone: {clinic.get('phone', 'N/A')}")
        else:
            print("⚠️  No clinics converted")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

