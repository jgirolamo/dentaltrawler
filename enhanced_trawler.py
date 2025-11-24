"""
Enhanced Dental Service Trawler with multiple data sources
Includes NHS, Google Places API, and CQC integration
"""

import requests
from bs4 import BeautifulSoup
import json
import csv
import time
import re
from typing import List, Dict, Optional
from urllib.parse import urljoin, quote
import logging
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Try to import Google Maps client
try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    logging.warning("googlemaps not available. Install with: pip install googlemaps")

from config import (
    SERVICE_KEYWORDS, LANGUAGE_KEYWORDS, REQUEST_DELAY,
    REQUEST_TIMEOUT, OUTPUT_JSON, OUTPUT_CSV
)

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedDentalTrawler:
    """Enhanced trawler with multiple data sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.clinics = []
        self.metadata = {
            'last_updated': None,
            'sources': {},
            'total_clinics': 0,
            'duplicates_removed': 0
        }
        
        # Initialize Google Maps client if API key is available
        self.gmaps = None
        google_api_key = os.getenv('GOOGLE_PLACES_API_KEY')
        if GOOGLEMAPS_AVAILABLE and google_api_key:
            try:
                self.gmaps = googlemaps.Client(key=google_api_key)
                logger.info("Google Places API initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Maps: {e}")
    
    def search_nhs_directory(self, location: str = "London", max_results: int = 50) -> List[Dict]:
        """Search NHS directory with improved scraping"""
        logger.info(f"Searching NHS directory for dental practices in {location}")
        clinics = []
        
        try:
            # NHS Service Finder uses a search form
            search_url = "https://www.nhs.uk/service-search/find-a-dentist/results"
            
            # Try to submit search form
            params = {
                'Location': location,
                'ServiceType': 'Dental',
                'PageSize': '50'
            }
            
            response = self.session.get(search_url, params=params, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for results in various formats
            results = []
            
            # Try finding result cards/items
            result_selectors = [
                ('div', {'class': re.compile(r'result|listing|card', re.I)}),
                ('article', {'class': re.compile(r'result|listing|card', re.I)}),
                ('li', {'class': re.compile(r'result|listing|item', re.I)}),
                ('div', {'data-testid': re.compile(r'result|listing', re.I)}),
            ]
            
            for tag, attrs in result_selectors:
                found = soup.find_all(tag, attrs)
                if found:
                    results = found
                    logger.info(f"Found {len(found)} results using {tag} selector")
                    break
            
            # If no structured results, try to find links to practice pages
            if not results:
                practice_links = soup.find_all('a', href=re.compile(r'dentist|dental|practice|service', re.I))
                logger.info(f"Found {len(practice_links)} practice links")
                results = practice_links[:max_results]
            
            # Extract clinic information
            for i, result in enumerate(results[:max_results]):
                try:
                    clinic_data = self._extract_nhs_clinic_info(result)
                    if clinic_data:
                        clinic_data['source'] = 'NHS Directory'
                        clinics.append(clinic_data)
                        time.sleep(REQUEST_DELAY)
                except Exception as e:
                    logger.warning(f"Error extracting clinic {i+1}: {e}")
                    continue
            
            # If still no results, try alternative approach
            if not clinics:
                logger.info("Trying alternative NHS search approach...")
                clinics = self._search_nhs_alternative(location, max_results)
            
        except Exception as e:
            logger.error(f"Error searching NHS directory: {e}")
        
        self.metadata['sources']['nhs'] = len(clinics)
        return clinics
    
    def _search_nhs_alternative(self, location: str, max_results: int) -> List[Dict]:
        """Alternative NHS search method"""
        clinics = []
        
        try:
            # Try direct API endpoint if available
            api_url = "https://www.nhs.uk/api/service-search/dentist"
            params = {
                'location': location,
                'limit': max_results
            }
            
            response = self.session.get(api_url, params=params, timeout=REQUEST_TIMEOUT)
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        clinics = data
                    elif isinstance(data, dict) and 'results' in data:
                        clinics = data['results']
                except:
                    pass
        except:
            pass
        
        return clinics
    
    def _extract_nhs_clinic_info(self, element) -> Optional[Dict]:
        """Extract information from NHS directory element"""
        try:
            # Try to find name
            name = None
            name_selectors = [
                ('h2', {}), ('h3', {}), ('h4', {}),
                ('a', {'class': re.compile(r'name|title|link', re.I)}),
                ('span', {'class': re.compile(r'name|title', re.I)}),
                ('div', {'class': re.compile(r'name|title', re.I)})
            ]
            
            for tag, attrs in name_selectors:
                name_elem = element.find(tag, attrs) if attrs else element.find(tag)
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    break
            
            if not name:
                # Try getting text from link
                link = element.find('a', href=True)
                if link:
                    name = link.get_text(strip=True)
            
            if not name:
                return None
            
            # Extract address
            address = None
            address_elem = element.find(['p', 'div', 'span'], 
                                       class_=re.compile(r'address|location', re.I))
            if address_elem:
                address = address_elem.get_text(strip=True)
            
            # Extract phone
            phone = None
            phone_elem = element.find(['a', 'span'], href=re.compile(r'tel:', re.I))
            if phone_elem:
                phone = phone_elem.get_text(strip=True).replace('tel:', '').strip()
            else:
                # Try finding phone in text
                phone_match = re.search(r'(\+44|0)[\d\s-]{10,}', element.get_text())
                if phone_match:
                    phone = phone_match.group(0).strip()
            
            # Extract link
            link = None
            link_elem = element.find('a', href=True)
            if link_elem:
                link = link_elem['href']
                if link and not link.startswith('http'):
                    link = urljoin("https://www.nhs.uk", link)
            
            return {
                'name': name,
                'address': address or '',
                'phone': phone or '',
                'link': link or '',
                'services': [],
                'languages': []
            }
        except Exception as e:
            logger.warning(f"Error parsing clinic element: {e}")
            return None
    
    def search_google_places(self, query: str = "dental clinic London", max_results: int = 20) -> List[Dict]:
        """Search Google Places API for dental clinics"""
        if not self.gmaps:
            logger.warning("Google Places API not available")
            return []
        
        logger.info(f"Searching Google Places for: {query}")
        clinics = []
        
        try:
            # Search for places
            places_result = self.gmaps.places(query=query, type='dentist')
            
            if 'results' in places_result:
                for place in places_result['results'][:max_results]:
                    try:
                        clinic = self._extract_google_place(place)
                        if clinic:
                            clinics.append(clinic)
                            time.sleep(REQUEST_DELAY)
                    except Exception as e:
                        logger.warning(f"Error extracting Google Place: {e}")
                        continue
            
            # Get more details for each place
            for clinic in clinics:
                if clinic.get('place_id'):
                    try:
                        details = self.gmaps.place(place_id=clinic['place_id'])
                        self._enrich_google_place(clinic, details)
                        time.sleep(REQUEST_DELAY)
                    except Exception as e:
                        logger.warning(f"Error getting place details: {e}")
        
        except Exception as e:
            logger.error(f"Error searching Google Places: {e}")
        
        self.metadata['sources']['google_places'] = len(clinics)
        return clinics
    
    def _extract_google_place(self, place: Dict) -> Optional[Dict]:
        """Extract clinic information from Google Place result"""
        try:
            name = place.get('name', '')
            if not name:
                return None
            
            address = place.get('formatted_address', '')
            phone = place.get('formatted_phone_number', '')
            rating = place.get('rating')
            place_id = place.get('place_id')
            
            # Extract postcode from address
            postcode = None
            postcode_match = re.search(r'\b([A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2})\b', address.upper())
            if postcode_match:
                postcode = postcode_match.group(1)
            
            # Extract area/borough
            area = None
            address_parts = address.split(',')
            if len(address_parts) > 1:
                area = address_parts[-2].strip()
            
            # Get website
            website = place.get('website', '')
            
            # Get opening hours
            opening_hours = None
            if 'opening_hours' in place and 'weekday_text' in place['opening_hours']:
                opening_hours = '; '.join(place['opening_hours']['weekday_text'])
            
            clinic = {
                'name': name,
                'address': address,
                'phone': phone,
                'link': website,
                'rating': rating,
                'postcode': postcode,
                'area': area,
                'opening_hours': opening_hours,
                'place_id': place_id,
                'services': [],
                'languages': [],
                'source': 'Google Places'
            }
            
            return clinic
        except Exception as e:
            logger.warning(f"Error extracting Google Place: {e}")
            return None
    
    def _enrich_google_place(self, clinic: Dict, details: Dict):
        """Enrich clinic with detailed information"""
        try:
            result = details.get('result', {})
            
            # Update with more detailed info
            if 'formatted_phone_number' in result:
                clinic['phone'] = result['formatted_phone_number']
            if 'website' in result:
                clinic['link'] = result['website']
            if 'opening_hours' in result and 'weekday_text' in result['opening_hours']:
                clinic['opening_hours'] = '; '.join(result['opening_hours']['weekday_text'])
            
            # Try to extract services and languages from reviews/description
            text_content = ' '.join([
                result.get('name', ''),
                result.get('formatted_address', ''),
                ' '.join(result.get('reviews', [])[:3]) if 'reviews' in result else ''
            ]).lower()
            
            # Extract services
            services = []
            for keyword in SERVICE_KEYWORDS:
                if keyword in text_content:
                    services.append(keyword.title())
            clinic['services'] = list(set(services))
            
            # Extract languages
            languages = []
            for keyword in LANGUAGE_KEYWORDS:
                if keyword in text_content:
                    languages.append(keyword.title())
            if 'english' in text_content and 'English' not in languages:
                languages.append('English')
            clinic['languages'] = list(set(languages))
            
        except Exception as e:
            logger.warning(f"Error enriching Google Place: {e}")
    
    def search_cqc(self, location: str = "London", max_results: int = 20) -> List[Dict]:
        """Search CQC (Care Quality Commission) for dental practices"""
        logger.info(f"Searching CQC for dental practices in {location}")
        clinics = []
        
        try:
            # CQC API endpoint
            cqc_url = "https://api.cqc.org.uk/public/v1/locations"
            params = {
                'careHome': 'false',
                'query': 'dental',
                'localAuthority': location,
                'perPage': min(max_results, 100)
            }
            
            response = self.session.get(cqc_url, params=params, timeout=REQUEST_TIMEOUT)
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'locations' in data:
                        for location_data in data['locations'][:max_results]:
                            clinic = self._extract_cqc_location(location_data)
                            if clinic:
                                clinics.append(clinic)
                                time.sleep(REQUEST_DELAY)
                except json.JSONDecodeError:
                    logger.warning("CQC API returned non-JSON response")
        except Exception as e:
            logger.warning(f"Error searching CQC: {e}")
        
        self.metadata['sources']['cqc'] = len(clinics)
        return clinics
    
    def _extract_cqc_location(self, location_data: Dict) -> Optional[Dict]:
        """Extract clinic information from CQC location data"""
        try:
            name = location_data.get('name', '')
            if not name:
                return None
            
            address_parts = location_data.get('address', {})
            address = ', '.join([
                address_parts.get('addressLine1', ''),
                address_parts.get('addressLine2', ''),
                address_parts.get('city', ''),
                address_parts.get('postalCode', '')
            ]).strip(', ')
            
            phone = location_data.get('phone', '')
            website = location_data.get('website', '')
            rating = location_data.get('overallRating', {}).get('rating', None)
            
            return {
                'name': name,
                'address': address,
                'phone': phone,
                'link': website,
                'rating': rating,
                'postcode': address_parts.get('postalCode', ''),
                'services': [],
                'languages': [],
                'source': 'CQC'
            }
        except Exception as e:
            logger.warning(f"Error extracting CQC location: {e}")
            return None
    
    def deduplicate_clinics(self, clinics: List[Dict]) -> List[Dict]:
        """Remove duplicate clinics based on name, phone, or address"""
        seen = set()
        unique_clinics = []
        duplicates = 0
        
        for clinic in clinics:
            # Create unique identifier
            name = clinic.get('name', '').lower().strip()
            phone = clinic.get('phone', '').replace(' ', '').replace('-', '')
            address = clinic.get('address', '').lower().strip()
            
            # Try multiple matching strategies
            identifiers = []
            if name:
                identifiers.append(f"name:{name}")
            if phone:
                identifiers.append(f"phone:{phone}")
            if address:
                # Use first part of address (street name)
                address_parts = address.split(',')
                if address_parts:
                    identifiers.append(f"addr:{address_parts[0]}")
            
            # Check if we've seen this clinic
            is_duplicate = False
            for identifier in identifiers:
                if identifier in seen:
                    is_duplicate = True
                    duplicates += 1
                    break
            
            if not is_duplicate:
                # Add all identifiers to seen set
                for identifier in identifiers:
                    seen.add(identifier)
                unique_clinics.append(clinic)
        
        self.metadata['duplicates_removed'] = duplicates
        logger.info(f"Removed {duplicates} duplicate clinics")
        return unique_clinics
    
    def enrich_clinic_website(self, clinic: Dict) -> Dict:
        """Enrich clinic data by scraping its website"""
        if not clinic.get('link'):
            return clinic
        
        existing_services = clinic.get('services', [])
        existing_languages = clinic.get('languages', [])
        
        try:
            response = self.session.get(clinic['link'], timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            text_content = soup.get_text().lower()
            
            # Extract services
            services = []
            for keyword in SERVICE_KEYWORDS:
                if keyword in text_content and keyword.title() not in services:
                    services.append(keyword.title())
            
            # Extract languages
            languages = []
            for keyword in LANGUAGE_KEYWORDS:
                if keyword in text_content and keyword.title() not in languages:
                    languages.append(keyword.title())
            
            if 'english' in text_content and 'English' not in languages:
                languages.append('English')
            
            # Use scraped data if available, otherwise keep existing
            clinic['services'] = services or existing_services
            clinic['languages'] = languages or existing_languages
            
        except Exception as e:
            logger.debug(f"Error scraping {clinic['link']}: {e}")
        
        time.sleep(REQUEST_DELAY)
        return clinic
    
    def run(self, location: str = "London", max_clinics: int = 50, 
            use_google: bool = True, use_cqc: bool = True):
        """Main method to run the enhanced trawler"""
        logger.info(f"Starting enhanced dental service trawler for {location}")
        
        all_clinics = []
        
        # Search NHS directory
        logger.info("Searching NHS directory...")
        nhs_clinics = self.search_nhs_directory(location, max_results=max_clinics)
        all_clinics.extend(nhs_clinics)
        
        # Search Google Places if enabled
        if use_google and self.gmaps:
            logger.info("Searching Google Places...")
            google_clinics = self.search_google_places(
                f"dental clinic {location}", 
                max_results=min(20, max_clinics - len(all_clinics))
            )
            all_clinics.extend(google_clinics)
        
        # Search CQC if enabled
        if use_cqc:
            logger.info("Searching CQC...")
            cqc_clinics = self.search_cqc(location, max_results=min(20, max_clinics - len(all_clinics)))
            all_clinics.extend(cqc_clinics)
        
        # Deduplicate
        logger.info("Deduplicating clinics...")
        self.clinics = self.deduplicate_clinics(all_clinics)
        
        # Enrich with website data
        logger.info(f"Enriching {len(self.clinics)} clinics with website data...")
        for i, clinic in enumerate(self.clinics):
            logger.info(f"Processing clinic {i+1}/{len(self.clinics)}: {clinic.get('name', 'Unknown')}")
            self.clinics[i] = self.enrich_clinic_website(clinic)
            time.sleep(REQUEST_DELAY)
        
        # Update metadata
        self.metadata['last_updated'] = datetime.now().isoformat()
        self.metadata['total_clinics'] = len(self.clinics)
        
        logger.info(f"Completed scraping {len(self.clinics)} unique clinics")
        return self.clinics
    
    def save_to_json(self, filename: str = OUTPUT_JSON):
        """Save results to JSON file"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.clinics, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved {len(self.clinics)} clinics to {filename}")
        
        # Save metadata
        metadata_file = Path(filename).parent / "metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved metadata to {metadata_file}")
    
    def save_to_csv(self, filename: str = OUTPUT_CSV):
        """Save results to CSV file"""
        if not self.clinics:
            logger.warning("No clinics to save")
            return
        
        fieldnames = ['name', 'address', 'phone', 'services', 'languages', 'link', 
                     'source', 'area', 'postcode', 'rating', 'opening_hours',
                     'nhs', 'private', 'emergency', 'children', 'wheelchair_access', 'parking']
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for clinic in self.clinics:
                row = {
                    'name': clinic.get('name', ''),
                    'address': clinic.get('address', ''),
                    'phone': clinic.get('phone', ''),
                    'services': ', '.join(clinic.get('services', [])),
                    'languages': ', '.join(clinic.get('languages', [])),
                    'link': clinic.get('link', ''),
                    'source': clinic.get('source', ''),
                    'area': clinic.get('area', ''),
                    'postcode': clinic.get('postcode', ''),
                    'rating': clinic.get('rating', ''),
                    'opening_hours': clinic.get('opening_hours', ''),
                    'nhs': clinic.get('nhs', ''),
                    'private': clinic.get('private', ''),
                    'emergency': clinic.get('emergency', ''),
                    'children': clinic.get('children', ''),
                    'wheelchair_access': clinic.get('wheelchair_access', ''),
                    'parking': clinic.get('parking', '')
                }
                writer.writerow(row)
        
        logger.info(f"Saved results to {filename}")


def main():
    """Main entry point"""
    from config import SEARCH_LOCATION, MAX_CLINICS
    
    trawler = EnhancedDentalTrawler()
    
    # Check for Google API key
    use_google = bool(os.getenv('GOOGLE_PLACES_API_KEY'))
    if not use_google:
        logger.info("Google Places API key not found. Skipping Google Places search.")
    
    # Run the trawler
    clinics = trawler.run(
        location=SEARCH_LOCATION, 
        max_clinics=MAX_CLINICS,
        use_google=use_google,
        use_cqc=True
    )
    
    # Save results
    trawler.save_to_json()
    trawler.save_to_csv()
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"Scraping Complete!")
    print(f"{'='*60}")
    print(f"Total clinics found: {len(clinics)}")
    print(f"Sources: {trawler.metadata['sources']}")
    print(f"Duplicates removed: {trawler.metadata['duplicates_removed']}")
    print(f"Last updated: {trawler.metadata['last_updated']}")
    print(f"\nSample results:")
    for i, clinic in enumerate(clinics[:3], 1):
        print(f"\n{i}. {clinic.get('name', 'Unknown')}")
        print(f"   Address: {clinic.get('address', 'N/A')}")
        print(f"   Source: {clinic.get('source', 'N/A')}")
        print(f"   Services: {', '.join(clinic.get('services', ['N/A']))}")
        print(f"   Languages: {', '.join(clinic.get('languages', ['N/A']))}")


if __name__ == "__main__":
    main()

