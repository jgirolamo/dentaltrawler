"""
Quick script to fetch real NHS dental clinic data and convert to frontend format
"""
import json
import sys
import os

# Try to import the scraper
try:
    from dental_trawler import DentalServiceTrawler
    SCRAPER_AVAILABLE = True
except ImportError:
    SCRAPER_AVAILABLE = False
    print("Scraper not available. Install dependencies: pip install -r requirements.txt")

def convert_to_frontend_format(clinics):
    """Convert scraper output to frontend format"""
    frontend_clinics = []
    
    for clinic in clinics:
        frontend_clinic = {
            "name": clinic.get("name", "Unknown"),
            "address": clinic.get("address", ""),
            "phone": clinic.get("phone", ""),
            "services": clinic.get("services", []),
            "languages": clinic.get("languages", []),
            "postcode": clinic.get("postcode", ""),
            "nhs": clinic.get("nhs", False),
            "private": clinic.get("private", False),
            "emergency": clinic.get("emergency", False),
            "children": clinic.get("children", False),
            "wheelchair_access": clinic.get("wheelchair_access", False),
            "rating": clinic.get("rating", 0)
        }
        frontend_clinics.append(frontend_clinic)
    
    return frontend_clinics

def main():
    if not SCRAPER_AVAILABLE:
        print("\nTo get real data:")
        print("1. Install: pip install -r requirements.txt")
        print("2. Run: python dental_trawler.py")
        print("3. This will create dental_clinics_london.json")
        return
    
    print("Fetching real NHS dental clinic data...")
    trawler = DentalServiceTrawler()
    
    # Get real clinics (limit to 20 for speed)
    clinics = trawler.run(location="London", max_clinics=20)
    
    if not clinics:
        print("No clinics found. The scraper may need updating for current NHS website structure.")
        return
    
    # Convert to frontend format
    frontend_clinics = convert_to_frontend_format(clinics)
    
    # Save as JavaScript file
    js_content = "// Real NHS dental clinic data\n"
    js_content += "export const clinicsData = " + json.dumps(frontend_clinics, indent=2, ensure_ascii=False) + ";\n"
    
    output_file = "dentaltrawler/src/clinics.js"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(js_content)
    
    print(f"\n✅ Successfully fetched {len(frontend_clinics)} real clinics!")
    print(f"✅ Saved to {output_file}")
    print("\nNext steps:")
    print("1. Review the data")
    print("2. git add dentaltrawler/src/clinics.js")
    print("3. git commit -m 'Update with real NHS data'")
    print("4. git push")

if __name__ == "__main__":
    main()

