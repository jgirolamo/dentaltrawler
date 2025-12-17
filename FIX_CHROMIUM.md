# Fix Chromium Installation

## Current Issue

The `/usr/bin/chromium-browser` is a snap wrapper, but the actual Chromium snap is not installed.

## Solution

### Option 1: Install Chromium Snap (Recommended)
```bash
snap install chromium
```

### Option 2: Install Real Chromium via apt
```bash
sudo apt-get update
sudo apt-get install chromium-browser
```

### Option 3: Install Google Chrome
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

## After Installation

Run the scraper:
```bash
source venv/bin/activate
python3 scripts/scrape_with_selenium.py
```

## Verify Installation

Check if Chromium works:
```bash
chromium-browser --version
```

If it shows a version, it's installed correctly.

