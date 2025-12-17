# All Data Options - Complete Guide

This guide covers all available options for getting real dental clinic data.

## Option 1: Manual Data Entry ⭐ Easiest

**Best for:** Adding a few clinics manually with full control

```bash
python3 scripts/manual_data_entry.py
```

**Features:**
- Interactive form to add clinics one by one
- All fields: name, address, phone, services, languages, features
- Automatically saves to both JSON and frontend format
- Preserves existing data

## Option 2: CSV Import ⭐ Best for Bulk Data

**Best for:** When you have clinic data in a spreadsheet

**Step 1:** Create a template:
```bash
python3 scripts/import_from_csv.py --template
```

**Step 2:** Fill the CSV file with your data

**Step 3:** Import:
```bash
python3 scripts/import_from_csv.py data/clinic_template.csv
```

**CSV Format:**
- Columns: name, address, postcode, phone, website, area, services, languages, nhs, private, emergency, children, wheelchair, parking, rating, opening_hours
- Services and languages: comma-separated
- Boolean fields: yes/no or true/false

## Option 3: Improved NHS Scraper

**Best for:** After you've inspected the NHS website structure

**Step 1:** Inspect NHS website in browser:
1. Go to https://www.nhs.uk/service-search/find-a-dentist
2. Search for a location
3. Right-click on a practice listing → Inspect
4. Note the exact class names and HTML structure

**Step 2:** Update selectors in `scripts/improve_nhs_scraper.py`:
```python
custom_selectors = {
    'practice_listings': "div[class*='actual-class-name']",
    'practice_name': "h2.actual-class",
    # ... etc
}
```

**Step 3:** Run:
```bash
python3 scripts/improve_nhs_scraper.py
```

## Option 4: Google Places API ⭐ Best Quality

**Best for:** Getting high-quality, complete data automatically

**Step 1:** Get API key:
1. Go to https://console.cloud.google.com/
2. Create project
3. Enable "Places API"
4. Create API key

**Step 2:** Add to `.env`:
```bash
echo "GOOGLE_PLACES_API_KEY=your_key_here" > .env
```

**Step 3:** Run:
```bash
python3 scripts/fetch_private_clinics.py
```

**Cost:** Free tier: $200/month credit (≈1,000 requests/day)

## Option 5: PDF Extraction ⭐ Great for Directories

**Best for:** When you have a PDF directory or brochure with clinic listings

```bash
# Install PDF libraries
pip install pdfplumber PyPDF2

# For scanned PDFs (OCR)
pip install pytesseract pdf2image
sudo apt-get install tesseract-ocr

# Extract from PDF
python3 scripts/extract_from_pdf.py your_directory.pdf
```

**Features:**
- Extracts text from PDFs (text-based and scanned)
- Uses OCR for scanned PDFs
- Parses clinic information automatically
- Saves extracted text for review
- Merges with existing data

## Option 6: Yelp Scraper

**Best for:** Getting real clinic data with ratings

```bash
source venv/bin/activate
python3 scripts/scrape_yelp.py London 50
```

**Features:**
- Extracts clinic names, addresses, phones
- Gets ratings from Yelp
- Extracts services and features
- May need adjustments for Yelp's structure

**Note:** Yelp may have anti-bot measures. If it doesn't work, try:
- Running in non-headless mode
- Adding longer delays
- Using Yelp API (requires API key)

## Option 7: Selenium Scraper (Current)

**Best for:** Automated scraping when selectors are known

```bash
source venv/bin/activate
python3 scripts/scrape_with_selenium.py
```

**Status:** Working but needs correct selectors for NHS site

## Option 8: Data Management Tools

**Clean data:**
```bash
python3 scripts/data_tools.py clean input.json output.json
```

**Export to CSV:**
```bash
python3 scripts/data_tools.py export clinics.js clinics.csv
```

**Merge multiple sources:**
```bash
python3 scripts/data_tools.py merge source1.json source2.json output.json
```

## Quick Start Recommendations

1. **Quick test:** Use sample data (already in app)
2. **Add a few clinics:** Use manual entry (`manual_data_entry.py`)
3. **Bulk import:** Use CSV import
4. **Best quality:** Use Google Places API
5. **Custom scraping:** Improve NHS scraper with correct selectors

## All Scripts Summary

| Script | Purpose | Best For |
|--------|---------|----------|
| `manual_data_entry.py` | Interactive data entry | Adding clinics manually |
| `import_from_csv.py` | Import from CSV | Bulk data import |
| `improve_nhs_scraper.py` | Custom NHS scraper | After inspecting site |
| `fetch_private_clinics.py` | Google Places API | Best quality data |
| `extract_from_pdf.py` | PDF extraction | PDF directories |
| `scrape_yelp.py` | Yelp scraping | Real data with ratings |
| `scrape_yellow_pages.py` | Yellow Pages scraping | Alternative directory |
| `scrape_with_selenium.py` | Automated scraping | When selectors work |
| `data_tools.py` | Data management | Clean, export, merge |

## Current Data Status

- ✅ Sample data: 50 clinics (working in app)
- ⚠️ Scraped data: Needs refinement
- ✅ All tools: Ready to use

Choose the option that best fits your needs!

