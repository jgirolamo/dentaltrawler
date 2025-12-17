# Google Places API - Complete Guide

## Yes! Google Has an Official Places API

Google Places API (also called Places API) is Google's official API for accessing place data, including business listings, reviews, photos, and more.

## Quick Start

### Step 1: Get API Key

1. **Go to Google Cloud Console:**
   - https://console.cloud.google.com/

2. **Create or Select Project:**
   - Click "Select a project" → "New Project"
   - Give it a name (e.g., "Dental Trawler")

3. **Enable Places API:**
   - Go to "APIs & Services" → "Library"
   - Search for "Places API"
   - Click "Enable"
   - Also enable "Places API (New)" if available

4. **Create API Key:**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

5. **(Optional) Restrict API Key:**
   - Click on your API key
   - Under "API restrictions", select "Restrict key"
   - Choose "Places API" only (for security)

### Step 2: Set Up in Project

Create `.env` file in project root:
```bash
GOOGLE_PLACES_API_KEY=your_api_key_here
```

### Step 3: Install Dependencies

```bash
pip install googlemaps python-dotenv
```

### Step 4: Run the Fetcher

```bash
python3 scripts/fetch_private_clinics.py
```

## Cost & Limits

### Free Tier
- **$200/month free credit**
- **≈1,000 requests/day** (depending on request type)
- More than enough for this project!

### Pricing (After Free Tier)
- **Places Search (Text Search):** $32 per 1,000 requests
- **Place Details:** $17 per 1,000 requests
- **Place Photos:** $7 per 1,000 requests

### Request Types Used
- Text Search: ~$0.032 per search
- Place Details: ~$0.017 per place
- With free tier: ~6,000 searches or ~11,000 details per month

## What Data You Get

The Google Places API provides:

✅ **Business Information:**
- Name, address, phone
- Website URL
- Opening hours
- Rating and review count
- Photos

✅ **Location Data:**
- Coordinates (lat/lng)
- Postcode
- Area/neighborhood

✅ **Additional:**
- Business status
- Price level
- Types/categories
- Reviews (with API)

## API Features

### 1. Text Search
Search for places by text query:
```python
places_result = gmaps.places(query="private dental clinic London")
```

### 2. Place Details
Get detailed information:
```python
place_details = gmaps.place(place_id=place_id)
```

### 3. Nearby Search
Find places near a location:
```python
nearby = gmaps.places_nearby(location="51.5074,-0.1278", radius=5000, type="dentist")
```

## Our Implementation

The `scripts/fetch_private_clinics.py` script already uses Google Places API:

- ✅ Searches for "private dental clinic London"
- ✅ Searches for "cosmetic dentist London"
- ✅ Searches for "Harley Street dentist"
- ✅ Gets place details (phone, website, hours, rating)
- ✅ Extracts services and languages from reviews/descriptions
- ✅ Saves to JSON and frontend format

## Comparison: API vs Scraping

| Feature | Google Places API | Web Scraping |
|---------|------------------|--------------|
| **Reliability** | ✅ Official, stable | ⚠️ Breaks when site changes |
| **Data Quality** | ✅ High quality, verified | ⚠️ Varies |
| **Legal** | ✅ Official terms | ⚠️ May violate ToS |
| **Cost** | 💰 Free tier available | ✅ Free |
| **Rate Limits** | ✅ Clear limits | ⚠️ May get blocked |
| **CAPTCHA** | ✅ None | ❌ Often blocked |
| **Maintenance** | ✅ Low | ⚠️ High (selectors break) |

## Getting Started

1. **Get API Key** (5 minutes)
   - https://console.cloud.google.com/

2. **Add to .env:**
   ```bash
   echo "GOOGLE_PLACES_API_KEY=your_key" > .env
   ```

3. **Run:**
   ```bash
   python3 scripts/fetch_private_clinics.py
   ```

That's it! The script will automatically use the API key and fetch real clinic data.

## Documentation

- **Official Docs:** https://developers.google.com/maps/documentation/places
- **API Reference:** https://developers.google.com/maps/documentation/places/web-service
- **Python Client:** https://github.com/googlemaps/google-maps-services-python

## Why Use the API?

1. **Reliable:** Won't break when websites change
2. **Legal:** Official terms of service
3. **Quality:** Verified business data
4. **Complete:** Ratings, reviews, photos, hours
5. **Free Tier:** $200/month credit is plenty
6. **No CAPTCHA:** Unlike scraping

The API is the **best option** for getting real, high-quality clinic data!


