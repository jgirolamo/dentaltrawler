# Getting Real Private Clinic Data

## Option 1: Google Places API (Recommended - Best Quality)

### Step 1: Get a Google Places API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Places API**:
   - Go to "APIs & Services" > "Library"
   - Search for "Places API"
   - Click "Enable"
4. Create an API Key:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - Copy your API key
5. (Optional) Restrict the API key to Places API only for security

### Step 2: Add API Key to Project

Create a `.env` file in the project root:

```bash
GOOGLE_PLACES_API_KEY=your_api_key_here
```

### Step 3: Run the Fetcher

```bash
python3 scripts/fetch_private_clinics.py
```

This will fetch real private clinic data from Google Places and save it to:
- `data/private_dental_clinics_london.json`
- `dentaltrawler/src/clinics.js`

## Option 2: Manual Data Entry

If you have a list of real clinics, you can manually add them to `dentaltrawler/src/clinics.js`

## Option 3: Use Public APIs

Some alternatives:
- NHS Open Data (if available)
- CQC (Care Quality Commission) API
- Other dental directory APIs

## Current Status

The current data in `dentaltrawler/src/clinics.js` is **sample/fallback data** because:
- No Google Places API key configured
- NHS website scraping is not working (website structure changed)

To get real data, you need a Google Places API key.

