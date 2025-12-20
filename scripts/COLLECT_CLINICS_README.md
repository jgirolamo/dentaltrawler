# Automated London Zone 1 & 2 Clinic Collection

This script automatically collects dental clinics from London Underground Zones 1 and 2 until 500 are found.

## Features

- **Focused on Zones 1 & 2**: Searches all Zone 1 and Zone 2 postcodes and areas
- **Automatic Deduplication**: Prevents duplicate clinics
- **Progress Tracking**: Saves state between runs
- **Continuous Mode**: Runs every 3 hours automatically
- **Smart Filtering**: Only includes clinics in Zones 1 & 2

## Usage

### Run Once
```bash
cd /Users/g/Projects/dentaltrawler
python3 scripts/collect_central_london_clinics.py
```

### Run Continuously (Every 3 Hours)
```bash
cd /Users/g/Projects/dentaltrawler
python3 scripts/collect_central_london_clinics.py --continuous
```

### Run in Background (macOS/Linux)
```bash
cd /Users/g/Projects/dentaltrawler
nohup python3 scripts/collect_central_london_clinics.py --continuous > collection.log 2>&1 &
```

### Check Progress
```bash
cat data/collection_state.json
```

## How It Works

1. **Searches OpenStreetMap** (free, no API key needed)
2. **Focuses on London Zones 1 & 2**:
   - Zone 1: W1, W2, WC1, WC2, EC1-4, SW1, SW3, SW5, SW7, SW10, N1, N7, E1, E2, SE1, SE11
   - Zone 2: W3-6, W8-12, W14, SW2, SW4, SW6, SW8-19, NW1-3, NW5-6, NW8, NW10, 
     N2-6, N8-22, E3, E5-18, SE2-28
   - Areas: Westminster, Camden, Islington, Hackney, Tower Hamlets, Southwark, 
     Lambeth, Kensington, Chelsea, Hammersmith, Fulham, Battersea, Brixton, 
     Clapham, Greenwich, Lewisham, Peckham, Putney, Wandsworth, Wimbledon, etc.
3. **Deduplicates** based on name + phone or name + address
4. **Saves progress** to `data/collection_state.json`
5. **Updates** `dentaltrawler/src/clinics.js` automatically
6. **Stops** when 500 Zone 1 & 2 clinics are found

## Files Created

- `data/collection_state.json` - Progress tracking
- `data/private_dental_clinics_london.json` - All clinics (JSON)
- `dentaltrawler/src/clinics.js` - Frontend format (auto-updated)

## Rate Limiting

OpenStreetMap requires max 1 request per second. The script automatically handles this.

## Monitoring

Check the log file if running in background:
```bash
tail -f collection.log
```

## Stopping

Press `Ctrl+C` to stop continuous collection. Progress is saved automatically.

