"""
Import clinic data from CSV file
Format: name,address,postcode,phone,website,services,languages,nhs,private,emergency,children,wheelchair,parking,rating,opening_hours
"""

import csv
import json
from pathlib import Path
from typing import List, Dict

def import_from_csv(csv_file: str) -> List[Dict]:
    """Import clinics from CSV file"""
    clinics = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            clinic = {
                'name': row.get('name', '').strip(),
                'address': row.get('address', '').strip(),
                'postcode': row.get('postcode', '').strip().upper() or None,
                'phone': row.get('phone', '').strip() or None,
                'link': row.get('website', row.get('link', '')).strip() or None,
                'area': row.get('area', '').strip() or None,
                'services': [s.strip() for s in row.get('services', '').split(',') if s.strip()],
                'languages': [l.strip() for l in row.get('languages', 'English').split(',') if l.strip()] or ['English'],
                'nhs': row.get('nhs', '').lower() in ['true', 'yes', 'y', '1'],
                'private': row.get('private', '').lower() in ['true', 'yes', 'y', '1'],
                'emergency': row.get('emergency', '').lower() in ['true', 'yes', 'y', '1'],
                'children': row.get('children', '').lower() in ['true', 'yes', 'y', '1'],
                'wheelchair_access': row.get('wheelchair', row.get('wheelchair_access', '')).lower() in ['true', 'yes', 'y', '1'],
                'parking': row.get('parking', '').lower() in ['true', 'yes', 'y', '1'],
                'rating': float(row['rating']) if row.get('rating') and row['rating'].replace('.', '').isdigit() else None,
                'opening_hours': row.get('opening_hours', '').strip() or None,
                'source': 'CSV Import'
            }
            
            if clinic['name']:
                clinics.append(clinic)
    
    return clinics

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

def create_csv_template():
    """Create a CSV template file"""
    template_file = Path("data/clinic_template.csv")
    template_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(template_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'name', 'address', 'postcode', 'phone', 'website', 'area',
            'services', 'languages', 'nhs', 'private', 'emergency', 'children',
            'wheelchair', 'parking', 'rating', 'opening_hours'
        ])
        # Add example row
        writer.writerow([
            'Example Dental Practice',
            '123 High Street, London',
            'W1 1AA',
            '020 1234 5678',
            'https://example.com',
            'Westminster',
            'General Dentistry, Implants, Cosmetic',
            'English, Spanish, French',
            'yes',
            'yes',
            'yes',
            'yes',
            'yes',
            'yes',
            '4.5',
            'Mon-Fri: 9am-6pm'
        ])
    
    print(f"✅ Created template: {template_file}")
    print("   Fill it with your clinic data, then run:")
    print(f"   python3 scripts/import_from_csv.py {template_file}")

def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 import_from_csv.py <csv_file>")
        print("\nOr create a template first:")
        print("  python3 import_from_csv.py --template")
        create_csv_template()
        return
    
    if sys.argv[1] == '--template':
        create_csv_template()
        return
    
    csv_file = sys.argv[1]
    
    if not Path(csv_file).exists():
        print(f"❌ File not found: {csv_file}")
        print("   Create a template with: python3 import_from_csv.py --template")
        return
    
    print(f"📋 Importing clinics from: {csv_file}")
    clinics = import_from_csv(csv_file)
    
    if clinics:
        save_clinics(clinics)
        print(f"\n✅ Imported {len(clinics)} clinics!")
    else:
        print("\n⚠️  No clinics found in CSV file")

if __name__ == "__main__":
    main()

