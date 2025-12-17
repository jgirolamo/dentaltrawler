# Setup Scraping with Selenium

## Step 1: Install Chromium

Run this command (requires sudo password):

```bash
sudo apt-get update
sudo apt-get install -y chromium-browser
```

**Alternative:** Install Google Chrome instead:
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

## Step 2: Setup Python Environment

Run the setup script:

```bash
./setup_scraping.sh
```

Or manually:
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install selenium webdriver-manager
```

## Step 3: Run the Scraper

```bash
source venv/bin/activate
python3 scripts/scrape_with_selenium.py
```

This will:
- Scrape NHS directory using Selenium
- Extract real private dental clinic data
- Save to `data/private_dental_clinics_london.json`
- Update `dentaltrawler/src/clinics.js` automatically

## Troubleshooting

### "Chrome/Chromium not found"
- Make sure Chromium is installed: `chromium-browser --version`
- Or install it: `sudo apt-get install chromium-browser`

### "Selenium not installed"
- Activate venv: `source venv/bin/activate`
- Install: `pip install selenium webdriver-manager`

### "ChromeDriver error"
- The script uses webdriver-manager which auto-downloads ChromeDriver
- Make sure you have internet connection

## What the Scraper Does

1. Opens NHS directory website in headless Chrome
2. Searches for dental clinics in London
3. Extracts clinic information (name, address, phone, etc.)
4. Filters for private clinics
5. Saves results to JSON and frontend format

## Note

The scraper runs in headless mode (no browser window), so it's fast and doesn't require a display.

