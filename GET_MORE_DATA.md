# How to Get More Real Data for Search

## Current Status
- ✅ **48 real clinics** from OpenStreetMap
- ✅ Search is working with this data
- ⚠️  Limited to OpenStreetMap (free but rate-limited)

## 🆓 FREE Options (No API Key Required)

### 1. OpenStreetMap (Currently Using) ✅
**Status:** Working, FREE, no key needed

**Get more data:**
```bash
# Get 200 clinics from London
python3 scripts/fetch_openstreetmap.py London 200

# Get from specific areas
python3 scripts/fetch_openstreetmap.py "Westminster, London" 50
python3 scripts/fetch_openstreetmap.py "Camden, London" 50
python3 scripts/fetch_openstreetmap.py "Kensington, London" 50
```

**Limitations:**
- Rate limited to 1 request/second
- Basic data (name, address, postcode)
- Limited phone numbers
- No ratings/reviews

### 2. Comprehensive Free Search
**Run the comprehensive fetcher:**
```bash
python3 scripts/fetch_all_free_sources.py
```

This will:
- Search OpenStreetMap with multiple terms
- Cover 20+ London areas
- Use 10+ different search queries
- Deduplicate results
- Save all real data

## 💰 FREE Tier Options (Require API Key, but FREE tier available)

### 3. Google Places API ⭐ BEST QUALITY
**Free tier:** $200/month credit (≈1,000 searches)

**Setup:**
1. Get key: https://console.cloud.google.com/
2. Add to `.env`: `GOOGLE_PLACES_API_KEY=your_key`
3. Run: `python3 scripts/fetch_private_clinics.py`

**What you get:**
- ✅ High-quality data
- ✅ Phone numbers
- ✅ Ratings & reviews
- ✅ Opening hours
- ✅ Website links
- ✅ Photos

### 4. Yelp Fusion API ⭐ GREAT REVIEWS
**Free tier:** 5,000 calls/day

**Setup:**
1. Get key: https://www.yelp.com/developers
2. Add to `.env`: `YELP_API_KEY=your_key`
3. Run: `python3 scripts/fetch_yelp_api.py`

**What you get:**
- ✅ Reviews & ratings
- ✅ Phone numbers
- ✅ Photos
- ✅ Business hours

### 5. Foursquare Places API
**Free tier:** Limited

**Setup:**
1. Get key: https://developer.foursquare.com/
2. Add to `.env`: `FOURSQUARE_API_KEY=your_key`
3. Run: `python3 scripts/fetch_foursquare.py`

## 🔍 Quick Actions

### Get More Data RIGHT NOW (Free):
```bash
# Option 1: Run comprehensive free search
python3 scripts/fetch_all_free_sources.py

# Option 2: Get more from OpenStreetMap
python3 scripts/fetch_openstreetmap.py London 300

# Option 3: Search multiple areas
for area in "Westminster" "Camden" "Kensington" "Chelsea" "Islington"; do
  python3 scripts/fetch_openstreetmap.py "$area, London" 50
  sleep 2
done
```

### Get BEST Quality Data (Requires API Key):
```bash
# Google Places (best quality)
echo "GOOGLE_PLACES_API_KEY=your_key" >> .env
python3 scripts/fetch_private_clinics.py

# Yelp (best reviews)
echo "YELP_API_KEY=your_key" >> .env
python3 scripts/fetch_yelp_api.py
```

## 📊 Expected Results

**OpenStreetMap (Free):**
- Can get 100-300+ clinics
- Basic info (name, address, postcode)
- Some phone numbers

**Google Places (Free tier):**
- Can get 50-100+ clinics
- Complete info (phone, hours, ratings, reviews)
- Best quality

**Yelp (Free tier):**
- Can get 50-100+ clinics
- Reviews & ratings
- Good quality

**Combined:**
- 200-500+ real clinics possible
- Mix of free and API data
- Comprehensive coverage

## 🚀 Recommended Approach

1. **Start with free sources:**
   ```bash
   python3 scripts/fetch_all_free_sources.py
   ```

2. **Add Google Places (if you have key):**
   ```bash
   python3 scripts/fetch_private_clinics.py
   ```

3. **Add Yelp (if you have key):**
   ```bash
   python3 scripts/fetch_yelp_api.py
   ```

All scripts automatically merge and deduplicate results!

## ❓ Why Search Might Not Show Results

If search isn't working:
1. **Check data exists:**
   ```bash
   python3 -c "import json; f=open('dentaltrawler/src/clinics.js'); print(len(json.loads(f.read().split('[')[1].split(']')[0])))"
   ```

2. **Check for errors:**
   - Open browser console (F12)
   - Look for error messages
   - Check `/error-logs` page

3. **Verify file format:**
   - `clinics.js` should export `clinicsData`
   - Should be valid JSON array

## 💡 Tips

- **OpenStreetMap is slow** (1 req/sec) but completely free
- **Google Places is fast** and high quality (free tier available)
- **Combine sources** for best coverage
- **All scripts auto-merge** - run multiple times safely

