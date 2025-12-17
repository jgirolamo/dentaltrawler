# Yelp Scraping Status

## Current Issue

Yelp is using **DataDome CAPTCHA protection** which blocks automated scraping. The page shows a CAPTCHA instead of actual content.

## Solutions

### Option 1: Use Yelp Fusion API (Recommended)

Yelp provides an official API that doesn't require scraping:

1. **Get API Key:**
   - Go to https://www.yelp.com/developers
   - Create an app
   - Get your API key

2. **Use the API:**
   ```python
   import requests
   
   headers = {'Authorization': f'Bearer YOUR_API_KEY'}
   url = 'https://api.yelp.com/v3/businesses/search'
   params = {
       'term': 'dentist',
       'location': 'London',
       'limit': 50
   }
   response = requests.get(url, headers=headers, params=params)
   ```

3. **Benefits:**
   - Official, reliable
   - No CAPTCHA issues
   - Better data quality
   - Includes ratings, reviews, photos

### Option 2: Manual Data Entry

Use the manual entry tool to add Yelp data:
```bash
python3 scripts/manual_data_entry.py
```

### Option 3: Non-Headless Mode (May Help)

Try running the scraper in non-headless mode (visible browser):
- Modify `scrape_yelp.py` to remove `--headless` flag
- You may be able to manually solve CAPTCHA
- Not practical for automation

### Option 4: Use Alternative Sources

- **Google Places API** (best quality)
- **NHS Directory** (after fixing selectors)
- **PDF directories** (if available)
- **Manual research**

## Current Status

- ✅ Scraper code: **Created and ready**
- ❌ Yelp access: **Blocked by CAPTCHA**
- ✅ Alternative: **Yelp Fusion API available**

## Recommendation

For Yelp data, use the **Yelp Fusion API** instead of scraping. It's more reliable and provides better data.


