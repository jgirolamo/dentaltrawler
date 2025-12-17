# Installing Chromium for Selenium Scraping

## Option 1: Install Chromium with apt (requires sudo)

```bash
sudo apt-get update
sudo apt-get install -y chromium-browser chromium-chromedriver
```

## Option 2: Install Google Chrome (alternative)

```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb
```

## Option 3: Use Chromium from Snap (if snap is available)

```bash
sudo snap install chromium
```

## After Installation

1. **Install Python dependencies:**
```bash
source venv/bin/activate
pip install selenium webdriver-manager
```

2. **Run the scraper:**
```bash
python3 scripts/scrape_with_selenium.py
```

## Verify Installation

```bash
# Check if Chromium is installed
chromium-browser --version

# Or check Chrome
google-chrome --version
```

## Note

The Selenium script will automatically download ChromeDriver using webdriver-manager, so you mainly need the browser itself installed.

