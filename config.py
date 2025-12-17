"""
Configuration file for Dental Service Trawler
"""

# Search configuration
SEARCH_LOCATION = "London"
MAX_CLINICS = 50

# Scraping configuration
REQUEST_DELAY = 2  # seconds between requests
REQUEST_TIMEOUT = 10  # seconds

# Service keywords to look for
SERVICE_KEYWORDS = [
    'general dentistry', 'check-up', 'cleaning', 'scale and polish',
    'fillings', 'root canal', 'extraction', 'crown', 'bridge',
    'dentures', 'implants', 'orthodontics', 'braces', 'invisalign',
    'teeth whitening', 'cosmetic dentistry', 'veneers', 'gum treatment',
    'periodontics', 'oral surgery', 'emergency', 'children', 'pediatric',
    'wisdom teeth', 'dental hygiene', 'preventive', 'restorative',
    'endodontics', 'prosthodontics', 'oral health', 'dental x-ray'
]

# Language keywords to look for
LANGUAGE_KEYWORDS = [
    'english', 'spanish', 'french', 'german', 'italian', 'portuguese',
    'polish', 'romanian', 'arabic', 'urdu', 'hindi', 'punjabi',
    'bengali', 'turkish', 'greek', 'chinese', 'mandarin', 'cantonese',
    'japanese', 'korean', 'russian', 'dutch', 'swedish', 'norwegian',
    'farsi', 'persian', 'hebrew', 'thai', 'vietnamese', 'tagalog'
]

# Output file names (saved to data/ directory)
OUTPUT_JSON = "data/dental_clinics_london.json"
OUTPUT_CSV = "data/dental_clinics_london.csv"

