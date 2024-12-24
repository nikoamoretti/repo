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

def scrape_url(url, output_base='output'):
    """
    Scrape URL and save results in both JSON and CSV formats
    
    Args:
        url (str): URL to scrape
        output_base (str): Base name for output files (without extension)
    """
    start_time = time.time()
    logger.info(f"Starting scraper for URL: {url}")
    
    try:
        scraper = WebScraper()
        
        logger.info(f"Testing URL: {url}")
        result = scraper.scrape_url(url)
        
        if result:
            # Save results to JSON file
            json_file = f"{output_base}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            logger.info(f"Data saved to {json_file}")
            
            # Convert to CSV
            csv_file = f"{output_base}.csv"
            from convert_to_csv import convert_to_csv
            convert_to_csv(result, csv_file)
            logger.info(f"Data converted and saved to {csv_file}")
            
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
    import argparse
    
    parser = argparse.ArgumentParser(description='Web scraper with protection bypass capabilities')
    parser.add_argument('--url', type=str, required=True, help='URL to scrape')
    parser.add_argument('--output', type=str, default='output', help='Base name for output files (without extension)')
    args = parser.parse_args()
    
    scrape_url(args.url, args.output)
