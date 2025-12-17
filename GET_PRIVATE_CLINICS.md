# Getting Real Private Dental Clinic Data

This guide explains how to fetch real private dental clinic data for London.

## Quick Start

### Option 1: Using Google Places API (Recommended - Best Results)

1. **Get a Google Places API Key:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or use existing)
   - Enable "Places API" and "Places API (New)"
   - Create credentials (API Key)
   - Copy your API key

2. **Set up environment variable:**
   ```bash
   # Create .env file in project root
   echo "GOOGLE_PLACES_API_KEY=your_api_key_here" > .env
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the script:**
   ```bash
   python fetch_private_clinics.py
   ```

   The script will:
   - Search Google Places for private dental clinics
   - Search NHS directory for private practices
   - Deduplicate results
   - Optionally enrich with website data
   - Save to JSON and frontend format

### Option 2: Without Google Places API (Limited Results)

If you don't have a Google Places API key, the script will still work but with limited results:

```bash
python fetch_private_clinics.py
```

It will:
- Search NHS directory for private clinics
- Extract basic information
- Save results (fewer clinics, less detailed)

## What the Script Does

1. **Google Places Search** (if API key available):
   - Searches for "private dental clinic London"
   - Searches for "cosmetic dentist London"
   - Searches for "Harley Street dentist"
   - Gets detailed information (phone, website, hours, ratings)
   - Extracts services and languages from reviews

2. **NHS Directory Search**:
   - Searches NHS Service Finder
   - Filters for private clinics (keywords: private, cosmetic, Harley Street, implant)
   - Extracts basic clinic information

3. **Website Enrichment** (optional):
   - Scrapes clinic websites for services and languages
   - Can be slow but provides more detailed data

4. **Deduplication**:
   - Removes duplicate clinics based on name and phone

5. **Output**:
   - Saves to `private_dental_clinics_london.json`
   - Updates `dentaltrawler/src/clinics.js` for frontend

## Output Files

- **`private_dental_clinics_london.json`**: Full JSON data for backend/API
- **`dentaltrawler/src/clinics.js`**: JavaScript format for frontend

## Example Output

```json
[
  {
    "name": "Harley Street Dental Studio",
    "address": "78 Harley Street, London W1G 7HJ",
    "phone": "020 7935 1234",
    "link": "https://example.com",
    "rating": 4.8,
    "postcode": "W1G 7HJ",
    "area": "Westminster",
    "services": ["Cosmetic Dentistry", "Dental Implants", "Teeth Whitening"],
    "languages": ["English", "Arabic", "French"],
    "source": "Google Places",
    "private": true,
    "nhs": false
  }
]
```

## Troubleshooting

### "googlemaps not available"
```bash
pip install googlemaps
```

### "GOOGLE_PLACES_API_KEY not found"
- Create a `.env` file in the project root
- Add: `GOOGLE_PLACES_API_KEY=your_key_here`
- Or export: `export GOOGLE_PLACES_API_KEY=your_key_here`

### "No clinics found"
- Check your internet connection
- Verify Google Places API key is valid
- Try running with `use_nhs=True` to get NHS directory results
- NHS website structure may have changed (scraping is fragile)

### Rate Limiting (Google Places API)
- Free tier: 1,000 requests/day
- The script includes delays to respect rate limits
- If you hit limits, wait 24 hours or upgrade your plan

## Cost Considerations

### Google Places API
- **Free tier**: $200/month credit (≈1,000 requests/day)
- **Per request**: ~$0.02-0.03
- For 50 clinics: ~$1-2 (well within free tier)

### Alternative: Free Options
- NHS directory scraping (free but limited)
- Manual data entry
- Public datasets (if available)

## Next Steps

1. **Review the data:**
   ```bash
   cat private_dental_clinics_london.json | jq '.[0]'  # View first clinic
   ```

2. **Test the frontend:**
   ```bash
   cd dentaltrawler
   npm run dev
   ```

3. **Update the API:**
   - Copy `private_dental_clinics_london.json` to `dental_clinics_london.json`
   - Or update API to use the new file

4. **Deploy:**
   - Commit the updated `clinics.js` file
   - Deploy frontend and backend

## Tips for Best Results

1. **Use Google Places API** - Much better data quality
2. **Enable website enrichment** - Gets detailed services/languages
3. **Run during off-peak hours** - Better API response times
4. **Review and clean data** - Some clinics may need manual verification
5. **Update regularly** - Clinic information changes over time

## Manual Verification

After fetching, you may want to:
- Verify phone numbers are correct
- Check websites are accessible
- Confirm services are accurate
- Update languages if needed
- Add missing information

## Questions?

- Check `fetch_private_clinics.py` for implementation details
- Google Places API docs: https://developers.google.com/maps/documentation/places
- NHS Service Finder: https://www.nhs.uk/service-search/find-a-dentist

