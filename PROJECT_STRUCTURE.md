# Project Structure

## Overview

The project has been reorganized for better maintainability and clarity.

## Directory Structure

```
dentaltrawler/
├── api/                          # Backend API (FastAPI)
│   ├── index.py                  # Main API serverless function
│   ├── requirements.txt          # API dependencies
│   └── vercel.json               # Vercel API configuration
│
├── dentaltrawler/                # Frontend (React + Vite)
│   ├── src/
│   │   ├── pages/                # React pages
│   │   ├── api.js                 # API client
│   │   └── clinics.js             # Embedded clinic data
│   ├── package.json
│   └── vite.config.js
│
├── docs/                         # Documentation (15 files)
│   ├── DEPLOYMENT.md
│   ├── GET_PRIVATE_CLINICS.md
│   ├── LOCAL_DEBUG.md
│   └── ... (see docs/README.md)
│
├── scripts/                      # Utility scripts (8 files)
│   ├── fetch_private_clinics.py  # Fetch private clinic data
│   ├── fetch_real_data.py        # Fetch real NHS data
│   ├── enhanced_trawler.py        # Enhanced scraper
│   └── ... (see scripts/README.md)
│
├── data/                         # Generated data files
│   ├── private_dental_clinics_london.json
│   ├── dental_clinics_london.json
│   ├── dental_clinics_london.csv
│   └── all_clinics_results.html
│
├── api.py                        # Standalone API (alternative)
├── config.py                     # Configuration
├── dental_trawler.py             # Main scraper
├── run_api.py                    # API server runner
├── requirements.txt              # Python dependencies
├── README.md                     # Main documentation
└── vercel.json                   # Root Vercel config
```

## Root Files (Essential Only)

- **README.md** - Main project documentation
- **dental_trawler.py** - Main scraper script
- **run_api.py** - Run FastAPI backend
- **api.py** - Standalone API (alternative)
- **config.py** - Configuration settings
- **requirements.txt** - Python dependencies
- **vercel.json** - Vercel deployment config

## Key Directories

### `docs/` - Documentation
All markdown documentation files organized by topic:
- Deployment guides
- Setup instructions
- Troubleshooting guides
- API documentation

### `scripts/` - Utility Scripts
Reusable scripts for:
- Data fetching
- Data processing
- Testing
- Development tools

### `data/` - Data Files
Generated data files (JSON, CSV, HTML):
- Clinic data exports
- Generated reports
- Processed datasets

## File Paths Updated

All scripts and APIs have been updated to use the new structure:
- Data files: `data/` directory
- Scripts: `scripts/` directory
- Documentation: `docs/` directory

## Quick Reference

### Run Main Scraper
```bash
python dental_trawler.py
# Outputs to: data/dental_clinics_london.json
```

### Fetch Private Clinics
```bash
python scripts/fetch_private_clinics.py
# Outputs to: data/private_dental_clinics_london.json
```

### Run API
```bash
python run_api.py
# Reads from: data/private_dental_clinics_london.json
```

### Run Frontend
```bash
cd dentaltrawler
npm run dev
```

## Benefits of New Structure

✅ **Cleaner root** - Only essential files
✅ **Better organization** - Logical grouping
✅ **Easier navigation** - Clear directory structure
✅ **Maintainable** - Easy to find and update files
✅ **Scalable** - Easy to add new files in right places

