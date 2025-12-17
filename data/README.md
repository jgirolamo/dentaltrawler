# Data Directory

This directory contains generated data files.

## Files

- **private_dental_clinics_london.json** - Private dental clinic data (50 clinics)
- **dental_clinics_london.json** - General dental clinic data
- **dental_clinics_london.csv** - CSV export of clinic data
- **all_clinics_results.html** - HTML export of results

## Generating Data

To generate/update data files:

```bash
# Fetch private clinics
python scripts/fetch_private_clinics.py

# Or use main scraper
python dental_trawler.py
```

Files are automatically saved to this directory.
