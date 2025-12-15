# Getting Real NHS Dental Clinic Data

The current `clinics.js` file contains example data. To get REAL data:

## Option 1: Run the Scraper (Recommended)

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Run the scraper:
```bash
python dental_trawler.py
```

This will create `dental_clinics_london.json` with real NHS data.

3. Convert to frontend format:
```bash
python -c "
import json
with open('dental_clinics_london.json') as f:
    clinics = json.load(f)
js = 'export const clinicsData = ' + json.dumps(clinics, indent=2) + ';'
with open('dentaltrawler/src/clinics.js', 'w') as f:
    f.write(js)
"
```

## Option 2: Manual Data Entry

Visit https://www.nhs.uk/service-search/find-a-dentist and manually add real clinics to `clinics.js`

## Option 3: Use NHS API (if available)

Check if NHS provides a public API and integrate it in `fetchClinics.js`
