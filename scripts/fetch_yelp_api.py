"""
Fetch dental clinic data using Yelp Fusion API
Official API - no scraping needed!
"""

import json
import re
import time
import requests
from pathlib import Path
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()

class YelpAPIClient:
    """Client for Yelp Fusion API"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('YELP_API_KEY')
        if not self.api_key:
            raise ValueError("YELP_API_KEY not found. Set it in .env file or pass as argument.")
        
        self.base_url = "https://api.yelp.com/v3"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def search_businesses(self, term: str = "dentist", location: str = "London", limit: int = 50) -> List[Dict]:
        """Search for businesses using Yelp API"""
        print(f"\n🔍 Searching Yelp API for {term} in {location}...")
        
        url = f"{self.base_url}/businesses/search"
        params = {
            'term': term,
            'location': location,
            'limit': min(limit, 50),  # Yelp max is 50 per request
            'sort_by': 'rating',
            'categories': 'dentists'
        }
        
        all_businesses = []
        offset = 0
        
        while len(all_businesses) < limit:
            params['offset'] = offset
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                
                data = response.json()
                businesses = data.get('businesses', [])
                
                if not businesses:
                    break
                
                all_businesses.extend(businesses)
                print(f"  Found {len(businesses)} businesses (total: {len(all_businesses)})")
                
                # Check if there are more results
                if len(businesses) < params['limit']:
                    break
                
                offset += len(businesses)
                
                # Rate limiting - be respectful
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                print(f"  ⚠️  API Error: {e}")
                break
        
        return all_businesses[:limit]
    
    def get_business_details(self, business_id: str) -> Dict:
        """Get detailed information about a business"""
        url = f"{self.base_url}/businesses/{business_id}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Error getting details: {e}")
            return {}
    
    def convert_to_clinic_format(self, business: Dict) -> Dict:
        """Convert Yelp business data to clinic format"""
        location = business.get('location', {})
        address_parts = location.get('display_address', [])
        address = ', '.join(address_parts) if address_parts else ''
        
        # Extract postcode
        postcode = None
        if address_parts:
            for part in reversed(address_parts):
                postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', part.upper())
                if postcode_match:
                    postcode = postcode_match.group(1)
                    break
        
        # Extract area
        area = None
        if address_parts and len(address_parts) > 1:
            area = address_parts[-2] if len(address_parts) > 1 else None
        
        # Get categories as services
        categories = business.get('categories', [])
        services = [cat.get('title', '') for cat in categories if cat.get('title')]
        
        # Extract phone
        phone = business.get('display_phone', '') or business.get('phone', '')
        phone = phone.replace('+44', '0').replace(' ', '').strip()
        
        return {
            'name': business.get('name', ''),
            'address': address,
            'phone': phone,
            'link': business.get('url', ''),
            'postcode': postcode,
            'area': area,
            'services': services,
            'languages': ['English'],  # Yelp doesn't provide this
            'source': 'Yelp API',
            'private': True,  # Most Yelp dentists are private
            'nhs': False,
            'emergency': False,
            'children': False,
            'wheelchair_access': False,
            'parking': False,
            'rating': business.get('rating'),
            'opening_hours': None  # Would need to parse hours from business details
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
            phone = clinic.get('phone', '').replace(' ', '').replace('-', '')
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
        print(f"   Added {len(clinics)} new clinics from Yelp API")


def main():
    """Main entry point"""
    import sys
    
    print("="*60)
    print("Yelp Fusion API Client")
    print("="*60)
    print("\nGet your API key from: https://www.yelp.com/developers")
    print("Add to .env file: YELP_API_KEY=your_key_here\n")
    
    # Check for API key
    api_key = os.getenv('YELP_API_KEY')
    if not api_key:
        print("❌ YELP_API_KEY not found!")
        print("\nTo get an API key:")
        print("1. Go to https://www.yelp.com/developers")
        print("2. Create an app")
        print("3. Copy your API key")
        print("4. Add to .env file: YELP_API_KEY=your_key_here")
        return
    
    location = sys.argv[1] if len(sys.argv) > 1 else "London"
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 50
    
    try:
        client = YelpAPIClient(api_key)
        
        # Search for dentists
        businesses = client.search_businesses(term="dentist", location=location, limit=limit)
        
        if not businesses:
            print("⚠️  No businesses found")
            return
        
        # Convert to clinic format
        print(f"\n📋 Converting {len(businesses)} businesses to clinic format...")
        clinics = []
        for business in businesses:
            clinic = client.convert_to_clinic_format(business)
            if clinic.get('name'):
                clinics.append(clinic)
                print(f"    ✓ {clinic['name']}")
        
        if clinics:
            client.save_results(clinics)
            print(f"\n{'='*60}")
            print(f"✅ Complete! Found {len(clinics)} clinics from Yelp API")
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

