# Quick Start: Get Private Clinic Data

## 🚀 Fastest Way (3 Steps)

### Step 1: Get Google Places API Key (Optional but Recommended)
1. Visit: https://console.cloud.google.com/
2. Create project → Enable "Places API" → Create API Key
3. Create `.env` file:
   ```bash
   echo "GOOGLE_PLACES_API_KEY=your_key_here" > .env
   ```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Script
```bash
python fetch_private_clinics.py
```

That's it! The script will:
- ✅ Find private dental clinics in London
- ✅ Get detailed information (phone, address, ratings)
- ✅ Extract services and languages
- ✅ Save to JSON and update frontend

## 📋 What You'll Get

**Output Files:**
- `private_dental_clinics_london.json` - Full data for backend
- `dentaltrawler/src/clinics.js` - Updated frontend data

**Data Includes:**
- Clinic name, address, phone
- Services offered (cosmetic, implants, etc.)
- Languages spoken
- Ratings and reviews
- Website links
- Opening hours

## ⚡ Without API Key

If you don't have a Google Places API key, the script will still work but with fewer results:
- Uses NHS directory only
- Less detailed information
- Still gets basic clinic data

Just run:
```bash
python fetch_private_clinics.py
```

## 🎯 Next Steps

1. **Test the data:**
   ```bash
   cat private_dental_clinics_london.json | head -50
   ```

2. **View in frontend:**
   ```bash
   cd dentaltrawler
   npm run dev
   ```

3. **Update API (if needed):**
   ```bash
   cp private_dental_clinics_london.json dental_clinics_london.json
   ```

## 💡 Tips

- **Best results**: Use Google Places API key
- **More details**: Say "yes" to website enrichment (slower but more complete)
- **Free tier**: Google gives $200/month credit (plenty for this use case)

## ❓ Troubleshooting

**"ModuleNotFoundError: No module named 'googlemaps'"**
```bash
pip install googlemaps
```

**"No clinics found"**
- Check internet connection
- Verify API key is correct
- Try running again (NHS site can be slow)

**Need help?** See `GET_PRIVATE_CLINICS.md` for detailed guide.

