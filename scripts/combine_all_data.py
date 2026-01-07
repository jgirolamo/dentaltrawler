"""
Combine all dental clinic data sources and update frontend
"""

import json
from pathlib import Path
from typing import List, Dict
import re

def normalize_phone(phone: str) -> str:
    """Normalize phone number for comparison"""
    if not phone:
        return ''
    # Remove all non-digits except +
    return re.sub(r'[^\d+]', '', phone)

def normalize_name(name: str) -> str:
    """Normalize clinic name for comparison"""
    if not name:
        return ''
    # Lowercase, remove common words, extra spaces
    name = name.lower().strip()
    name = re.sub(r'\b(dental|dentist|surgery|practice|clinic|centre|center|ltd|limited)\b', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def merge_clinic_data(existing: Dict, new: Dict) -> Dict:
    """Merge two clinic records, preferring non-empty values"""
    merged = existing.copy()

    for key, value in new.items():
        if value and not merged.get(key):
            merged[key] = value
        # For lists, merge them
        elif isinstance(value, list) and value:
            existing_list = merged.get(key, [])
            if isinstance(existing_list, list):
                merged[key] = list(set(existing_list + value))

    return merged

def load_json_file(filepath: Path) -> List[Dict]:
    """Load JSON file safely"""
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"  ⚠️  Error loading {filepath}: {e}")
    return []

def main():
    print("="*60)
    print("Combining All Dental Clinic Data Sources")
    print("="*60)

    base_path = Path("/Users/g/projects/dentaltrawler")

    # Load all data sources
    sources = [
        ("Overpass API", base_path / "data" / "dental_clinics_overpass.json"),
        ("Private Clinics", base_path / "data" / "private_dental_clinics_london.json"),
        ("General Clinics", base_path / "data" / "dental_clinics_london.json"),
    ]

    all_clinics = []

    for name, filepath in sources:
        print(f"\n📂 Loading {name}...")
        data = load_json_file(filepath)
        print(f"   Found {len(data)} records")
        all_clinics.extend(data)

    print(f"\n📊 Total raw records: {len(all_clinics)}")

    # Deduplicate by name + phone/address
    print("\n🔄 Deduplicating...")
    seen = {}
    unique_clinics = []

    for clinic in all_clinics:
        name = clinic.get('name', '')
        if not name:
            continue

        # Create identifier
        norm_name = normalize_name(name)
        norm_phone = normalize_phone(clinic.get('phone', ''))
        postcode = (clinic.get('postcode') or '').replace(' ', '').upper()

        # Try multiple identifiers
        identifiers = [
            f"{norm_name}:{norm_phone}" if norm_phone else None,
            f"{norm_name}:{postcode}" if postcode else None,
            norm_name if not norm_phone and not postcode else None,
        ]

        matched = False
        for identifier in identifiers:
            if identifier and identifier in seen:
                # Merge with existing
                idx = seen[identifier]
                unique_clinics[idx] = merge_clinic_data(unique_clinics[idx], clinic)
                matched = True
                break

        if not matched:
            # Add new clinic
            idx = len(unique_clinics)
            for identifier in identifiers:
                if identifier:
                    seen[identifier] = idx
            unique_clinics.append(clinic)

    print(f"   Unique clinics: {len(unique_clinics)}")

    # Sort by completeness (more data = higher priority)
    def completeness_score(clinic):
        score = 0
        if clinic.get('phone'): score += 3
        if clinic.get('link'): score += 2
        if clinic.get('address'): score += 2
        if clinic.get('postcode'): score += 1
        if clinic.get('email'): score += 1
        if clinic.get('opening_hours'): score += 1
        return score

    unique_clinics.sort(key=completeness_score, reverse=True)

    # Calculate stats
    with_phone = sum(1 for c in unique_clinics if c.get('phone'))
    with_website = sum(1 for c in unique_clinics if c.get('link'))
    with_address = sum(1 for c in unique_clinics if c.get('address'))
    with_postcode = sum(1 for c in unique_clinics if c.get('postcode'))

    print(f"\n📊 Data Quality Stats:")
    print(f"   📞 With phone: {with_phone} ({100*with_phone//len(unique_clinics)}%)")
    print(f"   🌐 With website: {with_website} ({100*with_website//len(unique_clinics)}%)")
    print(f"   📍 With address: {with_address} ({100*with_address//len(unique_clinics)}%)")
    print(f"   📮 With postcode: {with_postcode} ({100*with_postcode//len(unique_clinics)}%)")

    # Save combined data
    output_json = base_path / "data" / "all_clinics_combined.json"
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(unique_clinics, f, indent=2, ensure_ascii=False)
    print(f"\n✅ Saved to {output_json}")

    # Update frontend clinics.js
    frontend_file = base_path / "dentaltrawler" / "src" / "clinics.js"
    js_content = "// London dental clinic data - Auto-generated\n"
    js_content += f"// Total clinics: {len(unique_clinics)}\n"
    js_content += f"// With phone: {with_phone}, With website: {with_website}\n"
    js_content += "// Source: OpenStreetMap + Various\n\n"
    js_content += "export const clinicsData = "
    js_content += json.dumps(unique_clinics, indent=2, ensure_ascii=False)
    js_content += ";\n"

    with open(frontend_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ Updated frontend: {frontend_file}")

    # Show top 10 most complete clinics
    print(f"\n{'='*60}")
    print("Top 10 Most Complete Clinics:")
    print("="*60)
    for i, clinic in enumerate(unique_clinics[:10], 1):
        print(f"\n{i}. {clinic.get('name', 'Unknown')}")
        if clinic.get('address'):
            print(f"   📍 {clinic.get('address')}")
        if clinic.get('phone'):
            print(f"   📞 {clinic.get('phone')}")
        if clinic.get('link'):
            print(f"   🌐 {clinic.get('link')}")
        if clinic.get('opening_hours'):
            print(f"   🕐 {clinic.get('opening_hours')}")


if __name__ == "__main__":
    main()
