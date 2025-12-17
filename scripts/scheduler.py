"""
Scheduler for automated dental clinic data updates
Can be run as a cron job or scheduled task
"""

import schedule
import time
import logging
from datetime import datetime
from enhanced_trawler import EnhancedDentalTrawler
from config import SEARCH_LOCATION, MAX_CLINICS
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def run_scraper():
    """Run the scraper and save results"""
    logger.info("="*60)
    logger.info("Starting scheduled scraper run")
    logger.info("="*60)
    
    try:
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
        
        logger.info("="*60)
        logger.info(f"Scheduled run completed successfully")
        logger.info(f"Total clinics: {len(clinics)}")
        logger.info(f"Last updated: {trawler.metadata['last_updated']}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Error in scheduled scraper run: {e}", exc_info=True)


def main():
    """Main scheduler function"""
    # Schedule daily updates at 2 AM
    schedule.every().day.at("02:00").do(run_scraper)
    
    # Also run immediately on start (optional)
    logger.info("Running initial scraper...")
    run_scraper()
    
    logger.info("Scheduler started. Running daily at 2:00 AM")
    logger.info("Press Ctrl+C to stop")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        logger.info("Scheduler stopped")


if __name__ == "__main__":
    main()

