"""
Fetch dental clinic data using OpenStreetMap Overpass API
FREE - No API key needed, better data than Nominatim
"""

import json
import requests
import time
from pathlib import Path
from typing import List, Dict

class OverpassClient:
    """Client for OpenStreetMap Overpass API - better for bulk queries"""

    def __init__(self):
        self.base_url = "https://overpass-api.de/api/interpreter"
        self.headers = {
            'User-Agent': 'DentalTrawler/1.0'
        }

    def fetch_dentists_london(self) -> List[Dict]:
        """Fetch all dentists in Greater London using Overpass QL"""
        print("\n🔍 Fetching dentists from OpenStreetMap Overpass API...")
        print("  (Free API - comprehensive data for London area)")

        # Overpass QL query for dentists in Greater London
        # Bounding box: roughly Greater London area
        query = """
        [out:json][timeout:60];
        (
          // Dentists in Greater London area
          node["amenity"="dentist"](51.28,-0.51,51.69,0.33);
          way["amenity"="dentist"](51.28,-0.51,51.69,0.33);

          // Also get dental clinics
          node["healthcare"="dentist"](51.28,-0.51,51.69,0.33);
          way["healthcare"="dentist"](51.28,-0.51,51.69,0.33);
        );
        out body;
        >;
        out skel qt;
        """

        try:
            response = requests.post(
                self.base_url,
                data={'data': query},
                headers=self.headers,
                timeout=90
            )
            response.raise_for_status()
            data = response.json()

            elements = data.get('elements', [])
            print(f"  Found {len(elements)} elements")

            return elements

        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  API Error: {e}")
            return []

    def convert_to_clinic_format(self, element: Dict) -> Dict:
        """Convert Overpass element to clinic format"""
        tags = element.get('tags', {})

        # Get name
        name = tags.get('name', '')
        if not name:
            return None

        # Build address
        address_parts = []
        if tags.get('addr:housenumber'):
            address_parts.append(tags['addr:housenumber'])
        if tags.get('addr:street'):
            address_parts.append(tags['addr:street'])
        if tags.get('addr:city'):
            address_parts.append(tags['addr:city'])
        if tags.get('addr:postcode'):
            address_parts.append(tags['addr:postcode'])

        address = ', '.join(address_parts) if address_parts else ''

        # Get coordinates
        lat = element.get('lat')
        lon = element.get('lon')

        # Extract phone (various formats in OSM)
        phone = (tags.get('phone') or
                tags.get('contact:phone') or
                tags.get('telephone') or
                tags.get('contact:telephone'))

        # Clean phone number
        if phone:
            phone = phone.split(';')[0].strip()  # Take first if multiple

        # Extract website
        website = (tags.get('website') or
                  tags.get('contact:website') or
                  tags.get('url'))

        # Extract email
        email = tags.get('email') or tags.get('contact:email')

        # Opening hours
        opening_hours = tags.get('opening_hours')

        # Features
        wheelchair = tags.get('wheelchair') == 'yes'

        # NHS status
        nhs = 'nhs' in name.lower() or tags.get('nhs') == 'yes'

        return {
            'name': name,
            'address': address,
            'phone': phone,
            'link': website,
            'email': email,
            'postcode': tags.get('addr:postcode'),
            'area': tags.get('addr:city') or tags.get('addr:suburb'),
            'lat': lat,
            'lon': lon,
            'services': [],
            'languages': ['English'],
            'source': 'OpenStreetMap',
            'private': not nhs,
            'nhs': nhs,
            'emergency': 'emergency' in name.lower(),
            'children': 'child' in name.lower() or 'kids' in name.lower(),
            'wheelchair_access': wheelchair,
            'parking': tags.get('parking') is not None,
            'rating': None,
            'opening_hours': opening_hours
        }

    def save_results(self, clinics: List[Dict]):
        """Save results to files"""
        if not clinics:
            print("⚠️  No clinics to save")
            return

        # Save to JSON
        json_file = Path("data/dental_clinics_overpass.json")
        json_file.parent.mkdir(parents=True, exist_ok=True)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(clinics, f, indent=2, ensure_ascii=False)
        print(f"✅ Saved {len(clinics)} clinics to {json_file}")

        return clinics


def main():
    """Main entry point"""
    print("="*60)
    print("OpenStreetMap Overpass API - Dental Clinics")
    print("="*60)
    print("\n✅ FREE - No API key needed!")
    print("📍 Fetching all dentists in Greater London area\n")

    try:
        client = OverpassClient()

        # Fetch dentists
        elements = client.fetch_dentists_london()

        if not elements:
            print("⚠️  No elements found")
            return

        # Convert to clinic format
        print(f"\n📋 Converting elements to clinic format...")
        clinics = []
        for element in elements:
            if element.get('type') in ('node', 'way') and element.get('tags'):
                clinic = client.convert_to_clinic_format(element)
                if clinic:
                    clinics.append(clinic)

        print(f"  Converted {len(clinics)} valid clinics")

        if clinics:
            client.save_results(clinics)

            # Show stats
            with_phone = sum(1 for c in clinics if c.get('phone'))
            with_website = sum(1 for c in clinics if c.get('link'))
            with_address = sum(1 for c in clinics if c.get('address'))

            print(f"\n{'='*60}")
            print(f"✅ Complete! Found {len(clinics)} dental clinics")
            print(f"{'='*60}")
            print(f"\nData quality:")
            print(f"  📞 With phone: {with_phone} ({100*with_phone//len(clinics)}%)")
            print(f"  🌐 With website: {with_website} ({100*with_website//len(clinics)}%)")
            print(f"  📍 With address: {with_address} ({100*with_address//len(clinics)}%)")

            print(f"\nSample results:")
            for i, clinic in enumerate(clinics[:10], 1):
                print(f"\n{i}. {clinic.get('name', 'Unknown')}")
                if clinic.get('address'):
                    print(f"   📍 {clinic.get('address')}")
                if clinic.get('phone'):
                    print(f"   📞 {clinic.get('phone')}")
                if clinic.get('link'):
                    print(f"   🌐 {clinic.get('link')}")
        else:
            print("⚠️  No clinics converted")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
