import logging
import json
import time
from webscraper.scraper import WebScraper

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_scraper():
    start_time = time.time()
    logger.info("Starting scraper test")
    
    try:
        scraper = WebScraper()
        url = 'https://www.commtrex.com/transloading/ga/atlanta.html'
        
        logger.info(f"Testing URL: {url}")
        result = scraper.scrape_url(url)
        
        if result:
            # Save results to file
            with open('test_result.json', 'w') as f:
                json.dump(result, f, indent=2)
            
            logger.info(f"Successfully scraped data in {time.time() - start_time:.2f} seconds")
            logger.info(f"Title: {result.get('title', 'N/A')}")
            facilities = result.get('facilities', [])
            verified = [f for f in facilities if f['type'] == 'verified']
            unverified = [f for f in facilities if f['type'] == 'unverified']
            
            logger.info(f"Number of verified facilities: {len(verified)}")
            logger.info(f"Number of unverified facilities: {len(unverified)}")
            
            if verified:
                logger.info("\nSample Verified Facility:")
                logger.info(json.dumps(verified[0], indent=2))
            if unverified:
                logger.info("\nSample Unverified Facility:")
                logger.info(json.dumps(unverified[0], indent=2))
        else:
            logger.error("Failed to scrape URL")
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
    finally:
        scraper.close()
        logger.info(f"Total test time: {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    test_scraper()
