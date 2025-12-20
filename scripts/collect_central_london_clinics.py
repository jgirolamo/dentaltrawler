#!/usr/bin/env python3
"""
Automated clinic collection for London Zones 1 and 2
Runs periodically to collect clinics until 500 are found
Focuses on London Underground Zone 1 and Zone 2 postcodes and areas
"""

import json
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import requests

# London Zone 1 and Zone 2 postcodes
ZONE_1_2_POSTCODES = [
    # Zone 1
    "W1", "W2", "WC1", "WC2", "EC1", "EC2", "EC3", "EC4", 
    "SW1", "SW3", "SW5", "SW7", "SW10",
    "N1", "N7", "E1", "E2", "SE1", "SE11",
    # Zone 2 additions
    "W3", "W4", "W5", "W6", "W8", "W9", "W10", "W11", "W12", "W14",
    "WC1", "WC2",  # Already in Zone 1
    "SW2", "SW4", "SW6", "SW8", "SW9", "SW11", "SW12", "SW13", "SW14", "SW15", "SW16", "SW17", "SW18", "SW19",
    "NW1", "NW2", "NW3", "NW5", "NW6", "NW8", "NW10",
    "N2", "N3", "N4", "N5", "N6", "N8", "N9", "N10", "N11", "N12", "N13", "N14", "N15", "N16", "N17", "N18", "N19", "N20", "N21", "N22",
    "E3", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", "E14", "E15", "E16", "E17", "E18",
    "SE2", "SE3", "SE4", "SE5", "SE6", "SE7", "SE8", "SE9", "SE10", "SE12", "SE13", "SE14", "SE15", "SE16", "SE17", "SE18", "SE19", "SE20", "SE21", "SE22", "SE23", "SE24", "SE25", "SE26", "SE27", "SE28"
]

# London Zone 1 and Zone 2 areas
ZONE_1_2_AREAS = [
    # Zone 1
    "Westminster", "Camden", "Islington", "Hackney", "Tower Hamlets",
    "Southwark", "Lambeth", "Kensington and Chelsea", "Hammersmith and Fulham",
    "City of London", "Marylebone", "Soho", "Covent Garden",
    "Fitzrovia", "Bloomsbury", "Holborn", "Clerkenwell", "Shoreditch",
    "Spitalfields", "Whitechapel", "Bermondsey", "South Bank", "Vauxhall",
    # Zone 2 additions
    "Acton", "Battersea", "Bayswater", "Bethnal Green", "Brixton", "Camden Town",
    "Chelsea", "Chiswick", "Clapham", "Deptford", "Ealing", "Earl's Court",
    "Fulham", "Greenwich", "Hackney", "Hammersmith", "Hampstead", "Highbury",
    "Holloway", "Islington", "Kensington", "King's Cross", "Lambeth", "Lewisham",
    "Maida Vale", "Notting Hill", "Paddington", "Peckham", "Pimlico", "Putney",
    "Richmond", "Shoreditch", "Southwark", "Stoke Newington", "Stratford",
    "Tower Hamlets", "Wandsworth", "Westminster", "Wimbledon", "Woolwich"
]

TARGET_CLINICS = 500
INTERVAL_HOURS = 3  # Run every 3 hours
STATE_FILE = Path("data/collection_state.json")
CLINICS_FILE = Path("dentaltrawler/src/clinics.js")
JSON_FILE = Path("data/private_dental_clinics_london.json")


class Zone1Zone2Collector:
    """Collects dental clinics from London Zones 1 and 2"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {
            'User-Agent': 'DentalTrawler/1.0'
        }
        self.state = self.load_state()
    
    def load_state(self) -> Dict:
        """Load collection state"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {
            'total_collected': 0,
            'last_run': None,
            'areas_searched': [],
            'postcodes_searched': [],
            'last_clinic_count': 0
        }
    
    def save_state(self):
        """Save collection state"""
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(STATE_FILE, 'w') as f:
            json.dump(self.state, f, indent=2)
    
    def load_existing_clinics(self) -> List[Dict]:
        """Load existing clinics from file"""
        clinics = []
        if CLINICS_FILE.exists():
            try:
                content = CLINICS_FILE.read_text(encoding='utf-8')
                json_start = content.find('[')
                json_end = content.rfind(']') + 1
                if json_start >= 0 and json_end > json_start:
                    clinics = json.loads(content[json_start:json_end])
            except Exception as e:
                print(f"⚠️  Error loading existing clinics: {e}")
        return clinics
    
    def is_zone_1_2(self, clinic: Dict) -> bool:
        """Check if clinic is in London Zone 1 or Zone 2"""
        address = (clinic.get('address', '') or '').lower()
        area = (clinic.get('area', '') or '').lower()
        postcode = (clinic.get('postcode', '') or '').upper()
        
        # Check postcode
        for pc in ZONE_1_2_POSTCODES:
            if postcode.startswith(pc):
                return True
        
        # Check area
        for zone_area in ZONE_1_2_AREAS:
            if zone_area.lower() in area or zone_area.lower() in address:
                return True
        
        # Check for Zone 1/2 keywords
        zone_keywords = [
            'westminster', 'camden', 'islington', 'hackney', 'tower hamlets',
            'southwark', 'lambeth', 'kensington', 'chelsea', 'hammersmith',
            'fulham', 'city of london', 'marylebone', 'soho', 'covent garden',
            'fitzrovia', 'bloomsbury', 'holborn', 'clerkenwell', 'shoreditch',
            'spitalfields', 'whitechapel', 'bermondsey', 'vauxhall', 'battersea',
            'brixton', 'clapham', 'greenwich', 'lewisham', 'peckham', 'putney',
            'wandsworth', 'wimbledon', 'acton', 'ealing', 'chiswick', 'hampstead',
            'notting hill', 'paddington', 'richmond', 'stratford', 'woolwich'
        ]
        for keyword in zone_keywords:
            if keyword in address or keyword in area:
                return True
        
        return False
    
    def search_osm(self, query: str, location: str = "Central London", limit: int = 50) -> List[Dict]:
        """Search OpenStreetMap"""
        url = f"{self.base_url}/search"
        params = {
            'q': f"{query} {location}",
            'format': 'json',
            'limit': min(limit, 50),
            'addressdetails': 1,
            'extratags': 1
        }
        
        try:
            time.sleep(1)  # Rate limiting
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"  ⚠️  API Error: {e}")
            return []
    
    def convert_to_clinic_format(self, place: Dict) -> Dict:
        """Convert OSM place to clinic format"""
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
        postcode = address.get('postcode', '')
        area = address.get('suburb') or address.get('city') or address.get('town', '')
        name = place.get('name') or place.get('display_name', '').split(',')[0]
        
        tags = place.get('extratags', {}) or {}
        phone = tags.get('phone') or tags.get('contact:phone')
        link = tags.get('website') or tags.get('contact:website')
        
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
    
    def deduplicate_clinics(self, clinics: List[Dict]) -> List[Dict]:
        """Remove duplicate clinics"""
        seen: Set[str] = set()
        unique = []
        
        for clinic in clinics:
            name = (clinic.get('name', '') or '').lower().strip()
            address = (clinic.get('address', '') or '').lower().strip()
            phone = (clinic.get('phone') or '').replace(' ', '').replace('-', '').replace('+', '')
            
            # Create unique identifier
            if phone:
                identifier = f"{name}:{phone}"
            else:
                identifier = f"{name}:{address[:50]}"
            
            if identifier not in seen and name:
                seen.add(identifier)
                unique.append(clinic)
        
        return unique
    
    def collect_clinics(self) -> int:
        """Collect new clinics from London Zones 1 and 2"""
        print(f"\n{'='*60}")
        print(f"🔍 Collecting London Zone 1 & 2 Dental Clinics")
        print(f"{'='*60}")
        print(f"Target: {TARGET_CLINICS} clinics")
        print(f"Current: {self.state['last_clinic_count']} clinics")
        print(f"Remaining: {max(0, TARGET_CLINICS - self.state['last_clinic_count'])} clinics\n")
        
        existing_clinics = self.load_existing_clinics()
        print(f"📊 Loaded {len(existing_clinics)} existing clinics")
        
        # Filter to only Zone 1 & 2
        zone_clinics = [c for c in existing_clinics if self.is_zone_1_2(c)]
        print(f"📍 Found {len(zone_clinics)} Zone 1 & 2 clinics\n")
        
        new_clinics = []
        search_queries = [
            ("dentist", "London"),
            ("dental practice", "London"),
            ("dental clinic", "London"),
            ("orthodontist", "London"),
            ("dental surgery", "London"),
        ]
        
        # Search by area
        for area in ZONE_1_2_AREAS[:20]:  # Limit to avoid too many requests
            if area in self.state.get('areas_searched', []):
                continue
            
            print(f"🔍 Searching {area}...")
            for query, _ in search_queries:
                places = self.search_osm(query, location=area, limit=20)
                for place in places:
                    clinic = self.convert_to_clinic_format(place)
                    if clinic.get('name') and self.is_zone_1_2(clinic):
                        new_clinics.append(clinic)
                time.sleep(1)  # Rate limiting
            
            self.state['areas_searched'].append(area)
            time.sleep(2)  # Extra delay between areas
        
        # Search by postcode
        for postcode in ZONE_1_2_POSTCODES[:30]:  # Search more postcodes for Zone 1 & 2
            if postcode in self.state.get('postcodes_searched', []):
                continue
            
            print(f"🔍 Searching postcode {postcode}...")
            places = self.search_osm("dentist", location=f"London {postcode}", limit=20)
            for place in places:
                clinic = self.convert_to_clinic_format(place)
                if clinic.get('name') and self.is_zone_1_2(clinic):
                    new_clinics.append(clinic)
            time.sleep(1)
            
            self.state['postcodes_searched'].append(postcode)
            time.sleep(2)
        
        # Deduplicate
        print(f"\n📋 Found {len(new_clinics)} potential new clinics")
        new_clinics = self.deduplicate_clinics(new_clinics)
        
        # Remove duplicates with existing
        existing_identifiers = set()
        for clinic in zone_clinics:
            name = (clinic.get('name', '') or '').lower().strip()
            phone = (clinic.get('phone') or '').replace(' ', '').replace('-', '').replace('+', '')
            if phone:
                existing_identifiers.add(f"{name}:{phone}")
            else:
                address = (clinic.get('address', '') or '').lower().strip()
                existing_identifiers.add(f"{name}:{address[:50]}")
        
        truly_new = []
        for clinic in new_clinics:
            name = (clinic.get('name', '') or '').lower().strip()
            phone = (clinic.get('phone') or '').replace(' ', '').replace('-', '').replace('+', '')
            if phone:
                identifier = f"{name}:{phone}"
            else:
                address = (clinic.get('address', '') or '').lower().strip()
                identifier = f"{name}:{address[:50]}"
            
            if identifier not in existing_identifiers:
                truly_new.append(clinic)
        
        print(f"✅ {len(truly_new)} new unique clinics found")
        
        # Merge with existing
        all_clinics = existing_clinics + truly_new
        all_clinics = self.deduplicate_clinics(all_clinics)
        
        # Save
        self.save_clinics(all_clinics)
        
        # Update state
        self.state['last_clinic_count'] = len(all_clinics)
        self.state['total_collected'] += len(truly_new)
        self.state['last_run'] = datetime.now().isoformat()
        self.save_state()
        
        return len(truly_new)
    
    def save_clinics(self, clinics: List[Dict]):
        """Save clinics to files"""
        # Save JSON
        JSON_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_FILE, 'w', encoding='utf-8') as f:
            json.dump(clinics, f, indent=2, ensure_ascii=False)
        
        # Save JS
        js_content = "// Private London dental clinic data\n"
        js_content += "export const clinicsData = "
        js_content += json.dumps(clinics, indent=2, ensure_ascii=False)
        js_content += ";\n"
        
        CLINICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CLINICS_FILE, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        print(f"✅ Saved {len(clinics)} clinics to {CLINICS_FILE}")


def run_continuous():
    """Run collection continuously every few hours"""
    collector = Zone1Zone2Collector()
    
    print(f"\n{'='*60}")
    print(f"🚀 Starting Continuous Clinic Collection")
    print(f"{'='*60}")
    print(f"Target: {TARGET_CLINICS} London Zone 1 & 2 clinics")
    print(f"Interval: Every {INTERVAL_HOURS} hours")
    print(f"Press Ctrl+C to stop\n")
    
    try:
        while True:
            existing = collector.load_existing_clinics()
            current_count = len([c for c in existing if collector.is_zone_1_2(c)])
            
            if current_count >= TARGET_CLINICS:
                print(f"\n🎉 Target reached! Found {current_count} Central London clinics")
                print("Stopping collection...")
                break
            
            print(f"\n⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            new_count = collector.collect_clinics()
            
            existing = collector.load_existing_clinics()
            current_count = len([c for c in existing if collector.is_zone_1_2(c)])
            
            print(f"\n📊 Progress: {current_count}/{TARGET_CLINICS} clinics ({current_count/TARGET_CLINICS*100:.1f}%)")
            
            if current_count >= TARGET_CLINICS:
                print(f"\n🎉 Target reached! Found {current_count} Zone 1 & 2 clinics")
                break
            
            print(f"\n⏳ Waiting {INTERVAL_HOURS} hours until next collection...")
            print(f"   Next run: {(datetime.now().timestamp() + INTERVAL_HOURS * 3600):.0f}")
            time.sleep(INTERVAL_HOURS * 3600)  # Convert hours to seconds
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Collection stopped by user")
        print(f"Current count: {collector.state['last_clinic_count']} clinics")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


def run_once():
    """Run collection once"""
    collector = Zone1Zone2Collector()
    new_count = collector.collect_clinics()
    
    existing = collector.load_existing_clinics()
    current_count = len([c for c in existing if collector.is_zone_1_2(c)])
    
    print(f"\n{'='*60}")
    print(f"✅ Collection Complete")
    print(f"{'='*60}")
    print(f"New clinics found: {new_count}")
    print(f"Total Zone 1 & 2 clinics: {current_count}/{TARGET_CLINICS}")
    print(f"Progress: {current_count/TARGET_CLINICS*100:.1f}%")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        run_continuous()
    else:
        run_once()

