"""
Data Management Tools
Various utilities for managing clinic data
"""

import json
from pathlib import Path
from typing import List, Dict

def merge_clinic_data(*sources: List[Dict]) -> List[Dict]:
    """Merge multiple clinic data sources, removing duplicates"""
    all_clinics = []
    seen = set()
    
    for source in sources:
        for clinic in source:
            # Create unique identifier
            name = clinic.get('name', '').lower().strip()
            phone = clinic.get('phone', '').replace(' ', '').replace('-', '')
            identifier = f"{name}:{phone}" if phone else name
            
            if identifier not in seen and name:
                seen.add(identifier)
                all_clinics.append(clinic)
    
    return all_clinics

def validate_clinic(clinic: Dict) -> bool:
    """Validate clinic data"""
    if not clinic.get('name'):
        return False
    if len(clinic.get('name', '')) < 3:
        return False
    return True

def clean_clinic_data(clinics: List[Dict]) -> List[Dict]:
    """Clean and normalize clinic data"""
    cleaned = []
    
    for clinic in clinics:
        if not validate_clinic(clinic):
            continue
        
        # Normalize fields
        clinic['name'] = clinic.get('name', '').strip()
        clinic['address'] = clinic.get('address', '').strip()
        clinic['phone'] = clinic.get('phone', '').strip() or None
        clinic['link'] = clinic.get('link', '').strip() or None
        clinic['postcode'] = clinic.get('postcode', '').strip().upper() or None
        clinic['area'] = clinic.get('area', '').strip() or None
        
        # Ensure lists
        clinic['services'] = clinic.get('services', []) or []
        clinic['languages'] = clinic.get('languages', []) or ['English']
        
        # Ensure booleans
        clinic['nhs'] = bool(clinic.get('nhs', False))
        clinic['private'] = bool(clinic.get('private', False))
        clinic['emergency'] = bool(clinic.get('emergency', False))
        clinic['children'] = bool(clinic.get('children', False))
        clinic['wheelchair_access'] = bool(clinic.get('wheelchair_access', False))
        clinic['parking'] = bool(clinic.get('parking', False))
        
        cleaned.append(clinic)
    
    return cleaned

def export_to_csv(clinics: List[Dict], output_file: str):
    """Export clinics to CSV"""
    import csv
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        if not clinics:
            return
        
        fieldnames = [
            'name', 'address', 'postcode', 'phone', 'link', 'area',
            'services', 'languages', 'nhs', 'private', 'emergency', 'children',
            'wheelchair_access', 'parking', 'rating', 'opening_hours', 'source'
        ]
        
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for clinic in clinics:
            row = {field: clinic.get(field, '') for field in fieldnames}
            # Convert lists to strings
            row['services'] = ', '.join(row.get('services', []) or [])
            row['languages'] = ', '.join(row.get('languages', []) or [])
            # Convert booleans
            for bool_field in ['nhs', 'private', 'emergency', 'children', 'wheelchair_access', 'parking']:
                row[bool_field] = 'yes' if row.get(bool_field) else 'no'
            writer.writerow(row)
    
    print(f"✅ Exported {len(clinics)} clinics to {output_file}")

def load_clinics_from_file(file_path: str) -> List[Dict]:
    """Load clinics from JSON or JS file"""
    path = Path(file_path)
    
    if not path.exists():
        return []
    
    try:
        content = path.read_text(encoding='utf-8')
        
        # If it's a JS file, extract JSON
        if file_path.endswith('.js'):
            json_start = content.find('[')
            json_end = content.rfind(']') + 1
            if json_start >= 0 and json_end > json_start:
                content = content[json_start:json_end]
        
        return json.loads(content)
    except Exception as e:
        print(f"⚠️  Error loading {file_path}: {e}")
        return []

def main():
    """CLI for data tools"""
    import sys
    
    if len(sys.argv) < 2:
        print("Data Management Tools")
        print("\nUsage:")
        print("  python3 data_tools.py clean <input_file> <output_file>")
        print("  python3 data_tools.py export <input_file> <output_csv>")
        print("  python3 data_tools.py merge <file1> <file2> ... <output_file>")
        return
    
    command = sys.argv[1]
    
    if command == 'clean':
        if len(sys.argv) < 4:
            print("Usage: python3 data_tools.py clean <input_file> <output_file>")
            return
        
        clinics = load_clinics_from_file(sys.argv[2])
        cleaned = clean_clinic_data(clinics)
        
        output_file = Path(sys.argv[3])
        if output_file.suffix == '.js':
            js_content = "export const clinicsData = "
            js_content += json.dumps(cleaned, indent=2, ensure_ascii=False)
            js_content += ";\n"
            output_file.write_text(js_content, encoding='utf-8')
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(cleaned, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Cleaned {len(cleaned)} clinics (from {len(clinics)})")
    
    elif command == 'export':
        if len(sys.argv) < 4:
            print("Usage: python3 data_tools.py export <input_file> <output_csv>")
            return
        
        clinics = load_clinics_from_file(sys.argv[2])
        export_to_csv(clinics, sys.argv[3])
    
    elif command == 'merge':
        if len(sys.argv) < 4:
            print("Usage: python3 data_tools.py merge <file1> <file2> ... <output_file>")
            return
        
        sources = []
        for file_path in sys.argv[2:-1]:
            clinics = load_clinics_from_file(file_path)
            sources.append(clinics)
        
        merged = merge_clinic_data(*sources)
        output_file = Path(sys.argv[-1])
        
        if output_file.suffix == '.js':
            js_content = "export const clinicsData = "
            js_content += json.dumps(merged, indent=2, ensure_ascii=False)
            js_content += ";\n"
            output_file.write_text(js_content, encoding='utf-8')
        else:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(merged, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Merged {len(merged)} unique clinics")

if __name__ == "__main__":
    main()

