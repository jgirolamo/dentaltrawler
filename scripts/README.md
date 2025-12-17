# Scripts Directory

Utility scripts for the Dental Trawler project.

## Data Fetching Scripts
- **fetch_private_clinics.py** - Fetch private dental clinic data (Google Places API + NHS)
- **fetch_real_data.py** - Fetch real NHS dental clinic data
- **get_nhs_data.py** - Get NHS dental clinic data using NHS Service Finder
- **enhanced_trawler.py** - Enhanced scraper with multiple data sources

## Utility Scripts
- **generate_results_html.py** - Generate HTML from clinic data
- **example_usage.py** - Example usage of the scraper
- **scheduler.py** - Scheduled data updates
- **run_local.sh** - Script to run the app locally

## Main Scripts (in root)
- **dental_trawler.py** - Main scraper script

## Usage

### Fetch Private Clinics
```bash
python scripts/fetch_private_clinics.py
```

### Fetch Real NHS Data
```bash
python scripts/fetch_real_data.py
```

### Run Locally
```bash
./scripts/run_local.sh
```

