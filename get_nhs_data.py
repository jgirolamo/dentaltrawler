"""
Get real NHS dental clinic data using NHS Service Finder
This uses the public NHS website to get real clinic data
"""
import requests
import json
import re
from bs4 import BeautifulSoup

def get_nhs_dentists(postcode="London", limit=50):
    """Get real NHS dental clinics"""
    clinics = []
    
    try:
        # NHS Service Finder URL
        url = "https://www.nhs.uk/service-search/find-a-dentist/results"
        params = {
            "Location": postcode,
            "ServiceType": "Dental"
        }
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        print(f"Fetching NHS dental clinics for {postcode}...")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to find clinic listings
            # NHS website structure may vary, so we try multiple selectors
            clinic_elements = soup.find_all(['div', 'article', 'li'], 
                                          class_=re.compile(r'result|listing|card|practice', re.I))
            
            if not clinic_elements:
                # Try alternative: look for links with dentist in href
                clinic_elements = soup.find_all('a', href=re.compile(r'dentist|dental', re.I))
            
            print(f"Found {len(clinic_elements)} potential clinics")
            
            for i, element in enumerate(clinic_elements[:limit]):
                try:
                    clinic = extract_clinic_info(element)
                    if clinic and clinic.get('name'):
                        clinics.append(clinic)
                        print(f"  {i+1}. {clinic['name']}")
                except Exception as e:
                    continue
            
        else:
            print(f"Error: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"Error fetching data: {e}")
    
    return clinics

def extract_clinic_info(element):
    """Extract clinic information from HTML element"""
    clinic = {
        "name": "",
        "address": "",
        "phone": "",
        "services": [],
        "languages": [],
        "postcode": "",
        "nhs": True,
        "private": False,
        "emergency": False,
        "children": False,
        "wheelchair_access": False,
        "rating": 0
    }
    
    # Extract name
    name_elem = element.find(['h2', 'h3', 'h4', 'a', 'span'], 
                             class_=re.compile(r'name|title|heading', re.I))
    if not name_elem:
        name_elem = element.find('a')
    if name_elem:
        clinic['name'] = name_elem.get_text(strip=True)
    
    # Extract address
    address_elem = element.find(['p', 'div', 'span'], 
                               class_=re.compile(r'address|location', re.I))
    if address_elem:
        clinic['address'] = address_elem.get_text(strip=True)
        # Extract postcode
        postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', clinic['address'])
        if postcode_match:
            clinic['postcode'] = postcode_match.group(1)
    
    # Extract phone
    phone_elem = element.find(['a', 'span'], href=re.compile(r'tel:'))
    if phone_elem:
        clinic['phone'] = phone_elem.get('href', '').replace('tel:', '').strip()
    else:
        phone_text = re.search(r'(\d{3}\s?\d{3}\s?\d{4})', element.get_text())
        if phone_text:
            clinic['phone'] = phone_text.group(1)
    
    return clinic if clinic['name'] else None

def convert_to_frontend_format(clinics):
    """Convert to frontend JavaScript format"""
    js_content = "// Real NHS dental clinic data\n"
    js_content += "export const clinicsData = " + json.dumps(clinics, indent=2, ensure_ascii=False) + ";\n"
    return js_content

if __name__ == "__main__":
    print("Fetching real NHS dental clinic data...")
    print("This may take a minute...\n")
    
    clinics = get_nhs_dentists("London", limit=30)
    
    if clinics:
        print(f"\n✅ Found {len(clinics)} real clinics!")
        
        # Save to JavaScript file
        js_content = convert_to_frontend_format(clinics)
        output_file = "dentaltrawler/src/clinics.js"
        
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(js_content)
        
        print(f"✅ Saved to {output_file}")
        print("\nNext: git add dentaltrawler/src/clinics.js && git commit -m 'Real NHS data' && git push")
    else:
        print("\n⚠️  No clinics found. NHS website structure may have changed.")
        print("You may need to run the full scraper: python dental_trawler.py")

