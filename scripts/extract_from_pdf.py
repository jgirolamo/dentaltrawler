"""
Extract dental clinic data from PDF files
Supports scanned PDFs (OCR) and text-based PDFs
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional

# Try to import PDF libraries
try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using available libraries"""
    text = ""
    
    # Try pdfplumber first (best for structured data)
    if PDFPLUMBER_AVAILABLE:
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                print("✅ Extracted text using pdfplumber")
                return text
        except Exception as e:
            print(f"⚠️  pdfplumber failed: {e}")
    
    # Try PyPDF2 as fallback
    if PYPDF2_AVAILABLE:
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            if text.strip():
                print("✅ Extracted text using PyPDF2")
                return text
        except Exception as e:
            print(f"⚠️  PyPDF2 failed: {e}")
    
    # Try OCR for scanned PDFs
    if OCR_AVAILABLE and not text.strip():
        try:
            print("📄 PDF appears to be scanned, attempting OCR...")
            images = convert_from_path(pdf_path)
            for img in images:
                ocr_text = pytesseract.image_to_string(img)
                text += ocr_text + "\n"
            if text.strip():
                print("✅ Extracted text using OCR")
                return text
        except Exception as e:
            print(f"⚠️  OCR failed: {e}")
            print("   Install: pip install pytesseract pdf2image")
            print("   Also need: sudo apt-get install tesseract-ocr")
    
    return text

def parse_clinic_from_text(text: str) -> List[Dict]:
    """Parse clinic information from extracted text"""
    clinics = []
    
    # Split text into potential clinic entries
    # Common patterns: new lines, numbered lists, etc.
    lines = text.split('\n')
    
    current_clinic = {}
    buffer = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Look for clinic name patterns
        # Names are usually: capitalized, 3+ words, may contain "Dental", "Clinic", "Practice"
        name_patterns = [
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+){2,}(?:\s+(?:Dental|Clinic|Practice|Surgery|Centre))?)',
            r'^(\d+\.\s*)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,}(?:\s+(?:Dental|Clinic|Practice))?)',
        ]
        
        # Check if this looks like a clinic name
        is_name = False
        for pattern in name_patterns:
            match = re.match(pattern, line)
            if match:
                name = match.group(2) if match.group(2) else match.group(1)
                if len(name) > 10:  # Reasonable name length
                    # Save previous clinic if exists
                    if current_clinic.get('name'):
                        clinic = finalize_clinic(current_clinic, buffer)
                        if clinic:
                            clinics.append(clinic)
                    
                    # Start new clinic
                    current_clinic = {'name': name}
                    buffer = [line]
                    is_name = True
                    break
        
        if not is_name and current_clinic:
            buffer.append(line)
    
    # Save last clinic
    if current_clinic.get('name'):
        clinic = finalize_clinic(current_clinic, buffer)
        if clinic:
            clinics.append(clinic)
    
    # If no structured parsing worked, try to extract all potential clinics
    if not clinics:
        clinics = extract_clinics_fallback(text)
    
    return clinics

def finalize_clinic(clinic: Dict, buffer: List[str]) -> Optional[Dict]:
    """Finalize clinic data from buffer"""
    text = ' '.join(buffer)
    
    # Extract address (look for postcode)
    postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', text.upper())
    if postcode_match:
        clinic['postcode'] = postcode_match.group(1)
        # Get text before postcode as address
        idx = text.upper().find(postcode_match.group(1))
        if idx > 0:
            address = text[max(0, idx-100):idx].strip()
            clinic['address'] = address
    
    # Extract phone
    phone_patterns = [
        r'Tel[:\s]+(\d{5}\s?\d{6})',
        r'Phone[:\s]+(\d{5}\s?\d{6})',
        r'(\d{5}\s?\d{6})',
        r'(\d{4}\s?\d{3}\s?\d{4})',
        r'(\d{3}\s?\d{3}\s?\d{4})',
    ]
    for pattern in phone_patterns:
        match = re.search(pattern, text)
        if match:
            clinic['phone'] = match.group(1).strip()
            break
    
    # Extract website/email
    url_match = re.search(r'(https?://[^\s]+|www\.[^\s]+|[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,})', text, re.I)
    if url_match:
        link = url_match.group(1)
        if not link.startswith('http'):
            link = 'https://' + link
        clinic['link'] = link
    
    # Extract services (common dental services)
    services_keywords = [
        'General Dentistry', 'Implants', 'Cosmetic', 'Orthodontics', 'Invisalign',
        'Teeth Whitening', 'Veneers', 'Root Canal', 'Crown', 'Bridge', 'Dentures',
        'Emergency', 'Children', 'Pediatric', 'Oral Surgery', 'Periodontics'
    ]
    found_services = []
    text_lower = text.lower()
    for service in services_keywords:
        if service.lower() in text_lower:
            found_services.append(service)
    clinic['services'] = found_services if found_services else []
    
    # Extract languages
    languages_keywords = [
        'English', 'Spanish', 'French', 'German', 'Italian', 'Portuguese',
        'Polish', 'Arabic', 'Urdu', 'Hindi', 'Punjabi', 'Chinese'
    ]
    found_languages = ['English']  # Default
    for lang in languages_keywords:
        if lang.lower() in text_lower:
            found_languages.append(lang)
    clinic['languages'] = list(set(found_languages))
    
    # Set defaults
    clinic['area'] = None
    clinic['nhs'] = False
    clinic['private'] = True
    clinic['emergency'] = 'emergency' in text_lower
    clinic['children'] = 'children' in text_lower or 'pediatric' in text_lower
    clinic['wheelchair_access'] = 'wheelchair' in text_lower or 'accessible' in text_lower
    clinic['parking'] = 'parking' in text_lower
    clinic['rating'] = None
    clinic['opening_hours'] = None
    clinic['source'] = 'PDF Extraction'
    
    # Validate
    if not clinic.get('name') or len(clinic['name']) < 5:
        return None
    
    return clinic

def extract_clinics_fallback(text: str) -> List[Dict]:
    """Fallback extraction - look for any clinic-like patterns"""
    clinics = []
    
    # Look for patterns like: Name, Address, Phone
    # Common formats in directories
    paragraphs = text.split('\n\n')
    
    for para in paragraphs:
        para = para.strip()
        if len(para) < 20:  # Too short
            continue
        
        # Look for postcode (indicates address)
        postcode_match = re.search(r'([A-Z]{1,2}\d{1,2}\s?\d[A-Z]{2})', para.upper())
        if not postcode_match:
            continue
        
        # Look for phone
        phone_match = re.search(r'(\d{5}\s?\d{6}|\d{4}\s?\d{3}\s?\d{4})', para)
        if not phone_match:
            continue
        
        # First line might be name
        lines = para.split('\n')
        name = lines[0].strip() if lines else ""
        
        if len(name) > 5:
            clinic = {
                'name': name,
                'address': para,
                'phone': phone_match.group(1),
                'postcode': postcode_match.group(1),
                'link': None,
                'area': None,
                'services': [],
                'languages': ['English'],
                'source': 'PDF Extraction (Fallback)',
                'nhs': False,
                'private': True,
                'emergency': False,
                'children': False,
                'wheelchair_access': False,
                'parking': False,
                'rating': None,
                'opening_hours': None
            }
            clinics.append(clinic)
    
    return clinics

def save_clinics(clinics: List[Dict], output_file: str = None):
    """Save extracted clinics"""
    if not clinics:
        print("⚠️  No clinics extracted")
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
    
    # Merge (avoid duplicates)
    all_clinics = existing_clinics.copy()
    seen = set()
    for clinic in existing_clinics:
        name = clinic.get('name', '').lower()
        seen.add(name)
    
    for clinic in clinics:
        name = clinic.get('name', '').lower()
        if name and name not in seen:
            all_clinics.append(clinic)
            seen.add(name)
    
    # Save to JSON
    json_file = Path("data/private_dental_clinics_london.json")
    json_file.parent.mkdir(parents=True, exist_ok=True)
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(all_clinics, f, indent=2, ensure_ascii=False)
    print(f"✅ Saved {len(all_clinics)} total clinics to {json_file}")
    
    # Save to frontend format
    js_file = Path("dentaltrawler/src/clinics.js")
    js_content = "// Private London dental clinic data\n"
    js_content += "export const clinicsData = "
    js_content += json.dumps(all_clinics, indent=2, ensure_ascii=False)
    js_content += ";\n"
    
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print(f"✅ Saved to frontend format: {js_file}")
    print(f"   Added {len(clinics)} new clinics from PDF")

def main():
    """Main entry point"""
    import sys
    
    print("="*60)
    print("PDF Clinic Data Extractor")
    print("="*60)
    
    if len(sys.argv) < 2:
        print("\nUsage: python3 extract_from_pdf.py <pdf_file>")
        print("\nExample:")
        print("  python3 extract_from_pdf.py data/dental_directory.pdf")
        print("\nRequirements:")
        print("  pip install pdfplumber  # For text PDFs")
        print("  pip install PyPDF2      # Alternative")
        print("  pip install pytesseract pdf2image  # For scanned PDFs (OCR)")
        print("  sudo apt-get install tesseract-ocr  # For OCR")
        return
    
    pdf_file = sys.argv[1]
    
    if not Path(pdf_file).exists():
        print(f"❌ File not found: {pdf_file}")
        return
    
    # Check available libraries
    if not PDFPLUMBER_AVAILABLE and not PYPDF2_AVAILABLE:
        print("❌ No PDF libraries available!")
        print("   Install: pip install pdfplumber")
        print("   Or: pip install PyPDF2")
        return
    
    print(f"\n📄 Extracting text from: {pdf_file}")
    text = extract_text_from_pdf(pdf_file)
    
    if not text.strip():
        print("❌ Could not extract text from PDF")
        print("   If it's a scanned PDF, install OCR:")
        print("     pip install pytesseract pdf2image")
        print("     sudo apt-get install tesseract-ocr")
        return
    
    # Save extracted text for review
    text_file = Path("data/extracted_text.txt")
    text_file.parent.mkdir(parents=True, exist_ok=True)
    with open(text_file, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"✅ Extracted text saved to: {text_file}")
    print(f"   Text length: {len(text)} characters")
    
    print("\n🔍 Parsing clinic data...")
    clinics = parse_clinic_from_text(text)
    
    if clinics:
        print(f"✅ Found {len(clinics)} clinics")
        print("\nSample clinics:")
        for i, clinic in enumerate(clinics[:3], 1):
            print(f"\n{i}. {clinic.get('name', 'Unknown')}")
            print(f"   Address: {clinic.get('address', 'N/A')[:50]}...")
            print(f"   Phone: {clinic.get('phone', 'N/A')}")
        
        # Ask to save
        save = input(f"\nSave {len(clinics)} clinics? (y/n): ").lower()
        if save == 'y':
            save_clinics(clinics)
        else:
            print("⚠️  Not saved. Review extracted_text.txt and run again if needed.")
    else:
        print("⚠️  No clinics found in PDF")
        print("   Review extracted_text.txt to see what was extracted")
        print("   You may need to manually adjust the parsing logic")

if __name__ == "__main__":
    main()

