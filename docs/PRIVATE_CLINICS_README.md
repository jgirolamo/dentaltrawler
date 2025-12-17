# ✅ Private Clinic Data Fetcher - Ready to Use!

I've created a complete solution to fetch **real private dental clinic data** for London.

## 📦 What's Been Created

1. **`fetch_private_clinics.py`** - Main script to fetch private clinics
   - Uses Google Places API (best results)
   - Falls back to NHS directory scraping
   - Extracts services, languages, ratings
   - Deduplicates and enriches data

2. **`GET_PRIVATE_CLINICS.md`** - Detailed documentation
3. **`QUICK_START_PRIVATE.md`** - Quick start guide

## 🚀 How to Use (3 Steps)

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- `googlemaps` - For Google Places API
- `beautifulsoup4` - For web scraping
- `requests` - For HTTP requests
- `python-dotenv` - For environment variables

### 2. Get Google Places API Key (Recommended)

**Why?** Google Places gives the best, most complete data for private clinics.

**How:**
1. Go to https://console.cloud.google.com/
2. Create a project (or use existing)
3. Enable "Places API" and "Places API (New)"
4. Create credentials → API Key
5. Copy your key

**Set it up:**
```bash
# Create .env file
echo "GOOGLE_PLACES_API_KEY=your_key_here" > .env
```

**Cost:** Free tier gives $200/month credit (≈1,000 requests/day) - more than enough!

### 3. Run the Script
```bash
python fetch_private_clinics.py
```

The script will:
- ✅ Search Google Places for private clinics
- ✅ Search NHS directory
- ✅ Ask if you want to enrich with website data
- ✅ Save results to JSON and frontend format

## 📊 What You'll Get

**Output Files:**
- `private_dental_clinics_london.json` - Full data (for backend/API)
- `dentaltrawler/src/clinics.js` - Frontend format (auto-updated)

**Data Fields:**
```json
{
  "name": "Harley Street Dental Studio",
  "address": "78 Harley Street, London W1G 7HJ",
  "phone": "020 7935 1234",
  "link": "https://clinic-website.com",
  "rating": 4.8,
  "postcode": "W1G 7HJ",
  "area": "Westminster",
  "services": ["Cosmetic Dentistry", "Dental Implants", "Teeth Whitening"],
  "languages": ["English", "Arabic", "French"],
  "source": "Google Places",
  "private": true,
  "nhs": false,
  "opening_hours": "Mon-Fri: 9am-6pm"
}
```

## 🎯 Example Workflow

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up API key (if you have one)
echo "GOOGLE_PLACES_API_KEY=AIza..." > .env

# 3. Run the fetcher
python fetch_private_clinics.py

# 4. Review the data
cat private_dental_clinics_london.json | jq '.[0]'

# 5. Test in frontend
cd dentaltrawler
npm run dev
```

## ⚡ Without Google Places API

The script still works without an API key, but with limited results:
- Uses NHS directory only
- Fewer clinics found
- Less detailed information

Just run:
```bash
python fetch_private_clinics.py
```

## 🔍 How It Works

1. **Google Places Search** (if API key available):
   - Searches: "private dental clinic London", "cosmetic dentist London", "Harley Street dentist"
   - Gets detailed info: phone, website, hours, ratings
   - Extracts services/languages from reviews

2. **NHS Directory Search**:
   - Searches NHS Service Finder
   - Filters for private clinics (keywords: private, cosmetic, Harley Street)
   - Extracts basic information

3. **Website Enrichment** (optional):
   - Scrapes clinic websites
   - Extracts services and languages
   - More complete but slower

4. **Deduplication**:
   - Removes duplicates based on name/phone

5. **Output**:
   - Saves to JSON
   - Updates frontend file

## 📈 Expected Results

**With Google Places API:**
- 30-50+ private clinics
- Complete data (phone, address, ratings, services)
- High quality, verified information

**Without API (NHS only):**
- 10-20 clinics
- Basic information
- May need manual verification

## 🛠️ Troubleshooting

**"ModuleNotFoundError: No module named 'bs4'"**
```bash
pip install beautifulsoup4 googlemaps requests python-dotenv
```

**"GOOGLE_PLACES_API_KEY not found"**
- Create `.env` file: `echo "GOOGLE_PLACES_API_KEY=your_key" > .env`
- Or the script will work with NHS directory only

**"No clinics found"**
- Check internet connection
- Verify API key is valid (if using Google Places)
- Try running again (NHS site can be slow)

**Rate limiting (Google Places)**
- Free tier: 1,000 requests/day
- Script includes delays to respect limits
- If you hit limits, wait 24 hours

## 📝 Next Steps After Fetching

1. **Review the data:**
   ```bash
   # View first clinic
   cat private_dental_clinics_london.json | python3 -m json.tool | head -30
   ```

2. **Test in frontend:**
   ```bash
   cd dentaltrawler
   npm run dev
   # Visit http://localhost:5173
   ```

3. **Update API (if using backend):**
   ```bash
   cp private_dental_clinics_london.json dental_clinics_london.json
   ```

4. **Deploy:**
   - Commit updated `clinics.js`
   - Deploy frontend and backend

## 💡 Tips for Best Results

1. **Use Google Places API** - Much better data quality
2. **Enable website enrichment** - Gets detailed services/languages (slower but worth it)
3. **Run during off-peak hours** - Better API response times
4. **Review and clean data** - Some clinics may need manual verification
5. **Update regularly** - Clinic information changes over time

## 📚 More Information

- **Detailed guide:** See `GET_PRIVATE_CLINICS.md`
- **Quick start:** See `QUICK_START_PRIVATE.md`
- **Google Places API:** https://developers.google.com/maps/documentation/places
- **NHS Service Finder:** https://www.nhs.uk/service-search/find-a-dentist

## ✅ Summary

**Yes, it's possible to get real private clinic data!**

The script is ready to use. Just:
1. Install dependencies
2. (Optional) Get Google Places API key
3. Run the script

You'll get real private dental clinic data with services, languages, ratings, and more!

