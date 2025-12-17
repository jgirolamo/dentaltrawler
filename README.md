# Dental Service Trawler for London, UK

A web scraper that collects information about dental clinics in London, UK, including:
- Services provided
- Languages spoken at the clinic

## Features

- Scrapes dental clinic information from NHS directory
- Extracts services offered (general dentistry, orthodontics, cosmetic, etc.)
- Identifies languages spoken by clinic staff
- Exports data to JSON and CSV formats
- Respectful scraping with delays between requests

## Installation

1. Install Python 3.8 or higher

2. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Run the scraper with default settings:
```bash
python dental_trawler.py
```

This will:
- Search for dental clinics in London
- Scrape their websites for services and languages
- Save results to `dental_clinics_london.json` and `dental_clinics_london.csv`

### Custom Usage

You can modify the script to:
- Change the location (currently set to "London")
- Adjust the number of clinics to scrape
- Add additional data sources

Example:
```python
from dental_trawler import DentalServiceTrawler

trawler = DentalServiceTrawler()
clinics = trawler.run(location="London", max_clinics=50)
trawler.save_to_json("data/my_results.json")
trawler.save_to_csv("data/my_results.csv")
```

## Output Format

### JSON Output
```json
[
  {
    "name": "Clinic Name",
    "address": "123 Street, London",
    "phone": "020 1234 5678",
    "services": ["General Dentistry", "Orthodontics", "Teeth Whitening"],
    "languages": ["English", "Spanish", "Polish"],
    "link": "https://clinic-website.com",
    "source": "NHS Directory"
  }
]
```

### CSV Output
The CSV file contains columns:
- name
- address
- phone
- services (comma-separated)
- languages (comma-separated)
- link
- source

## Data Sources

Currently scrapes from:
- **NHS Service Finder**: Official NHS directory of dental practices

Future enhancements could include:
- Google Places API
- Yelp
- Other dental directory websites

## Important Notes

1. **Rate Limiting**: The scraper includes delays between requests to be respectful to websites
2. **Website Changes**: Web scraping is sensitive to website structure changes
3. **Legal Compliance**: Ensure you comply with websites' terms of service and robots.txt
4. **API Alternatives**: For production use, consider using official APIs (e.g., Google Places API, NHS API)

## Quick Start

### Frontend (React)
```bash
cd dentaltrawler
npm install
npm run dev
# Visit http://localhost:5173
```

### Fetch Private Clinic Data
```bash
python scripts/fetch_private_clinics.py
```

## Documentation

See the `docs/` directory for detailed guides:
- **docs/DEPLOYMENT.md** - Deployment instructions
- **docs/GET_PRIVATE_CLINICS.md** - Getting private clinic data
- **docs/LOCAL_DEBUG.md** - Local debugging guide

## Troubleshooting

- If scraping fails, websites may have changed their structure
- Some websites may block automated requests
- Consider using official APIs for more reliable data access
- See `docs/` for troubleshooting guides

## License

This project is for educational purposes. Please respect websites' terms of service and robots.txt files.

