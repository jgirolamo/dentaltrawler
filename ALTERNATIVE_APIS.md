# Alternative APIs & Services Similar to Yelp

## Directory APIs Similar to Yelp

### 1. Google Places API ⭐ Best Option
- **Official Google API**
- **Free tier:** $200/month credit
- **Quality:** Excellent
- **Status:** ✅ Already implemented in `fetch_private_clinics.py`
- **Get key:** https://console.cloud.google.com/

### 2. Yelp Fusion API ⭐ Great Alternative
- **Official Yelp API**
- **Free tier:** 5,000 calls/day
- **Quality:** Excellent (ratings, reviews)
- **Status:** ✅ Implemented in `fetch_yelp_api.py`
- **Get key:** https://www.yelp.com/developers

### 3. Foursquare Places API
- **Official Foursquare API**
- **Free tier:** Limited
- **Quality:** Good
- **Get key:** https://developer.foursquare.com/

### 4. TripAdvisor Content API
- **Official TripAdvisor API**
- **Free tier:** Limited
- **Quality:** Good (reviews, ratings)
- **Get key:** https://developer.tripadvisor.com/

### 5. Facebook Places API
- **Official Facebook API**
- **Free tier:** Available
- **Quality:** Good
- **Get key:** https://developers.facebook.com/

### 6. OpenStreetMap Nominatim API
- **Free, open-source**
- **No API key needed**
- **Quality:** Basic (addresses, coordinates)
- **Rate limit:** 1 request/second
- **Status:** Can be implemented

### 7. Here Places API
- **Official HERE API**
- **Free tier:** 250,000 transactions/month
- **Quality:** Excellent
- **Get key:** https://developer.here.com/

## UK-Specific APIs

### 8. CQC (Care Quality Commission) API
- **Official UK health regulator**
- **Free, public data**
- **Quality:** Official, verified
- **Status:** May need investigation
- **Link:** https://www.cqc.org.uk/

### 9. NHS Open Data
- **Official NHS data**
- **Free, public**
- **Quality:** Official
- **Status:** May need investigation

## Comparison Table

| API | Free Tier | Quality | Ratings | UK Coverage | Status |
|-----|-----------|---------|---------|--------------|--------|
| **Google Places** | $200/month | ⭐⭐⭐⭐⭐ | ✅ | ✅ Excellent | ✅ Ready |
| **Yelp Fusion** | 5K/day | ⭐⭐⭐⭐⭐ | ✅ | ✅ Good | ✅ Ready |
| **Foursquare** | Limited | ⭐⭐⭐⭐ | ✅ | ✅ Good | ⚠️ Can add |
| **TripAdvisor** | Limited | ⭐⭐⭐⭐ | ✅ | ✅ Good | ⚠️ Can add |
| **Facebook** | Available | ⭐⭐⭐ | ✅ | ✅ Good | ⚠️ Can add |
| **OpenStreetMap** | Unlimited* | ⭐⭐⭐ | ❌ | ✅ Good | ⚠️ Can add |
| **HERE** | 250K/month | ⭐⭐⭐⭐⭐ | ✅ | ✅ Excellent | ⚠️ Can add |
| **CQC** | Free | ⭐⭐⭐⭐ | ❌ | ✅ Official | ⚠️ Can add |

*Rate limited to 1 req/sec

## Recommendations

1. **Best Overall:** Google Places API (already implemented)
2. **Best for Reviews:** Yelp Fusion API (already implemented)
3. **Best Free:** OpenStreetMap (no key needed)
4. **Best UK-Specific:** CQC API (official regulator data)

## Quick Start

### Google Places (Recommended)
```bash
# Already implemented!
echo "GOOGLE_PLACES_API_KEY=your_key" > .env
python3 scripts/fetch_private_clinics.py
```

### Yelp Fusion
```bash
# Already implemented!
echo "YELP_API_KEY=your_key" > .env
python3 scripts/fetch_yelp_api.py
```

### OpenStreetMap (Free, No Key)
```bash
# Can be implemented - no API key needed!
```

## Which to Use?

- **For best quality:** Google Places API
- **For reviews/ratings:** Yelp Fusion API
- **For free option:** OpenStreetMap
- **For UK official data:** CQC API

You can use multiple APIs and merge the results for the best coverage!


