#!/usr/bin/env python3
"""
Quick status check for clinic collection progress
"""

import json
from pathlib import Path

STATE_FILE = Path("data/collection_state.json")
CLINICS_FILE = Path("dentaltrawler/src/clinics.js")
TARGET = 500

def is_zone_1_2(clinic):
    """Check if clinic is in London Zone 1 or Zone 2"""
    ZONE_1_2_POSTCODES = [
        "W1", "W2", "W3", "W4", "W5", "W6", "W8", "W9", "W10", "W11", "W12", "W14",
        "WC1", "WC2", "EC1", "EC2", "EC3", "EC4", 
        "SW1", "SW2", "SW3", "SW4", "SW5", "SW6", "SW7", "SW8", "SW9", "SW10", 
        "SW11", "SW12", "SW13", "SW14", "SW15", "SW16", "SW17", "SW18", "SW19",
        "NW1", "NW2", "NW3", "NW5", "NW6", "NW8", "NW10",
        "N1", "N2", "N3", "N4", "N5", "N6", "N7", "N8", "N9", "N10", "N11", "N12", 
        "N13", "N14", "N15", "N16", "N17", "N18", "N19", "N20", "N21", "N22",
        "E1", "E2", "E3", "E5", "E6", "E7", "E8", "E9", "E10", "E11", "E12", "E13", 
        "E14", "E15", "E16", "E17", "E18",
        "SE1", "SE2", "SE3", "SE4", "SE5", "SE6", "SE7", "SE8", "SE9", "SE10", 
        "SE11", "SE12", "SE13", "SE14", "SE15", "SE16", "SE17", "SE18", "SE19", 
        "SE20", "SE21", "SE22", "SE23", "SE24", "SE25", "SE26", "SE27", "SE28"
    ]
    
    address = (clinic.get('address', '') or '').lower()
    area = (clinic.get('area', '') or '').lower()
    postcode = (clinic.get('postcode', '') or '').upper()
    
    # Check postcode
    for pc in ZONE_1_2_POSTCODES:
        if postcode.startswith(pc):
            return True
    
    # Check area/address
    text = f"{address} {area}"
    zone_areas = [
        'westminster', 'camden', 'islington', 'hackney', 'tower hamlets',
        'southwark', 'lambeth', 'kensington', 'chelsea', 'hammersmith',
        'fulham', 'battersea', 'brixton', 'clapham', 'greenwich', 'lewisham',
        'peckham', 'putney', 'wandsworth', 'wimbledon', 'acton', 'ealing',
        'chiswick', 'hampstead', 'notting hill', 'paddington', 'richmond',
        'stratford', 'woolwich', 'marylebone', 'soho', 'covent garden',
        'holborn', 'clerkenwell', 'shoreditch', 'spitalfields'
    ]
    for zone_area in zone_areas:
        if zone_area in text:
            return True
    
    return False

def main():
    print("=" * 60)
    print("📊 Clinic Collection Status")
    print("=" * 60)
    
    # Load state
    state = {}
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, 'r') as f:
                state = json.load(f)
        except:
            pass
    
    # Load clinics
    clinics = []
    if CLINICS_FILE.exists():
        try:
            content = CLINICS_FILE.read_text(encoding='utf-8')
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                clinics = json.loads(content[json_start:json_end])
        except Exception as e:
            print(f"⚠️  Error loading clinics: {e}")
    
    # Count Zone 1 & 2 clinics
    zone_clinics = [c for c in clinics if is_zone_1_2(c)]
    total_clinics = len(clinics)
    
    print(f"\n📈 Statistics:")
    print(f"   Total clinics: {total_clinics}")
    print(f"   Zone 1 & 2: {len(zone_clinics)}")
    print(f"   Target: {TARGET}")
    print(f"   Progress: {len(zone_clinics)}/{TARGET} ({len(zone_clinics)/TARGET*100:.1f}%)")
    
    if state:
        print(f"\n📅 Collection Info:")
        if state.get('last_run'):
            print(f"   Last run: {state['last_run']}")
        if state.get('total_collected'):
            print(f"   Total collected: {state['total_collected']}")
        if state.get('areas_searched'):
            print(f"   Areas searched: {len(state['areas_searched'])}")
        if state.get('postcodes_searched'):
            print(f"   Postcodes searched: {len(state['postcodes_searched'])}")
    
    print("\n" + "=" * 60)
    
    if len(zone_clinics) >= TARGET:
        print("🎉 Target reached!")
    else:
        remaining = TARGET - len(zone_clinics)
        print(f"⏳ {remaining} more clinics needed")

if __name__ == "__main__":
    main()

