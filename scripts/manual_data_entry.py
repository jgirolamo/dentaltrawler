"""
Manual Data Entry Helper
Helps you add real clinic data manually
"""

import json
from pathlib import Path
from typing import List, Dict

def load_existing_clinics() -> List[Dict]:
    """Load existing clinics from file"""
    clinics_file = Path("dentaltrawler/src/clinics.js")
    if clinics_file.exists():
        try:
            content = clinics_file.read_text(encoding='utf-8')
            # Extract JSON from JavaScript file
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
        except:
            pass
    return []

def add_clinic_interactive():
    """Interactive function to add a clinic"""
    print("\n" + "="*60)
    print("Add New Dental Clinic")
    print("="*60 + "\n")
    
    clinic = {}
    
    # Name
    name = input("Clinic Name: ").strip()
    if not name:
        print("❌ Name is required")
        return None
    clinic['name'] = name
    
    # Address
    address = input("Address: ").strip()
    clinic['address'] = address
    
    # Postcode
    postcode = input("Postcode (e.g., W1 1AA): ").strip().upper()
    clinic['postcode'] = postcode if postcode else None
    
    # Area
    area = input("Area (e.g., Westminster): ").strip()
    clinic['area'] = area if area else None
    
    # Phone
    phone = input("Phone (e.g., 020 1234 5678): ").strip()
    clinic['phone'] = phone if phone else None
    
    # Website
    link = input("Website URL (optional): ").strip()
    clinic['link'] = link if link else None
    
    # Services
    print("\nServices (comma-separated, e.g., General Dentistry, Implants, Cosmetic):")
    services_input = input("Services: ").strip()
    clinic['services'] = [s.strip() for s in services_input.split(',') if s.strip()] if services_input else []
    
    # Languages
    print("\nLanguages (comma-separated, e.g., English, Spanish, French):")
    languages_input = input("Languages: ").strip()
    clinic['languages'] = [l.strip() for l in languages_input.split(',') if l.strip()] if languages_input else ['English']
    
    # Features
    print("\nFeatures (y/n):")
    clinic['nhs'] = input("  NHS accepting? (y/n): ").lower() == 'y'
    clinic['private'] = input("  Private? (y/n): ").lower() == 'y'
    clinic['emergency'] = input("  Emergency services? (y/n): ").lower() == 'y'
    clinic['children'] = input("  Children/Pediatric? (y/n): ").lower() == 'y'
    clinic['wheelchair_access'] = input("  Wheelchair access? (y/n): ").lower() == 'y'
    clinic['parking'] = input("  Parking available? (y/n): ").lower() == 'y'
    
    # Rating
    rating_input = input("Rating (0-5, optional): ").strip()
    clinic['rating'] = float(rating_input) if rating_input and rating_input.replace('.', '').isdigit() else None
    
    # Opening hours
    opening_hours = input("Opening hours (e.g., Mon-Fri: 9am-6pm): ").strip()
    clinic['opening_hours'] = opening_hours if opening_hours else None
    
    # Source
    clinic['source'] = 'Manual Entry'
    
    return clinic

def save_clinics(clinics: List[Dict]):
    """Save clinics to both JSON and frontend format"""
    # Save to JSON
    json_file = Path("data/private_dental_clinics_london.json")
    json_file.parent.mkdir(parents=True, exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(clinics, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(clinics)} clinics to {json_file}")
    
    # Save to frontend format
    js_file = Path("dentaltrawler/src/clinics.js")
    js_content = "// Private London dental clinic data\n"
    js_content += "export const clinicsData = "
    js_content += json.dumps(clinics, indent=2, ensure_ascii=False)
    js_content += ";\n"
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ Saved to frontend format: {js_file}")

def main():
    """Main entry point"""
    print("="*60)
    print("Manual Dental Clinic Data Entry")
    print("="*60)
    print("\nThis tool helps you add real clinic data manually.")
    print("You can add clinics one by one with all their details.\n")
    
    clinics = load_existing_clinics()
    print(f"📋 Loaded {len(clinics)} existing clinics\n")
    
    while True:
        clinic = add_clinic_interactive()
        if clinic:
            clinics.append(clinic)
            print(f"\n✅ Added: {clinic['name']}")
            
            # Ask if they want to add more
            more = input("\nAdd another clinic? (y/n): ").lower()
            if more != 'y':
                break
        else:
            retry = input("\nTry again? (y/n): ").lower()
            if retry != 'y':
                break
    
    if clinics:
        save_clinics(clinics)
        print(f"\n✅ Complete! Total clinics: {len(clinics)}")
    else:
        print("\n⚠️  No clinics added")

if __name__ == "__main__":
    main()

