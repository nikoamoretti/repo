import logging
import json
import time
import argparse
from webscraper.scraper import WebScraper
from convert_to_csv import convert_json_to_csv

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_url(url, output_base='output', test_mode=False, retry_count=3, protection_strategy='auto'):
    """
    Scrape a single URL and save the results to JSON and CSV files.
    
    Args:
        url (str): URL to scrape
        output_base (str): Base name for output files (without extension)
    """
    start_time = time.time()
    logger.info(f"Processing URL: {url}")
    
    try:
        scraper = WebScraper(protection_strategy=protection_strategy)
        result = None
        
        for attempt in range(retry_count):
            try:
                logger.info(f"Attempt {attempt + 1}/{retry_count}")
                result = scraper.scrape_url(url, test_mode=test_mode)
                if result:
                    break
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < retry_count - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                continue
        
        if result:
            # Save results to JSON
            json_output = f"{output_base}.json"
            with open(json_output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
            
            # Convert to CSV
            csv_output = f"{output_base}.csv"
            convert_json_to_csv(json_output, csv_output)
            
            logger.info(f"Data saved to {json_output}")
            logger.info(f"Data converted and saved to {csv_output}")
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
            
            return True
        else:
            logger.error("Failed to scrape URL")
            return False
            
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {str(e)}")
        return False
    finally:
        scraper.close()
        logger.info(f"Total test time: {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web scraper with protection bypass capabilities')
    parser.add_argument('--url', type=str, nargs='+', required=True,
                      help='One or more URLs to scrape (space separated)')
    parser.add_argument('--output', type=str, default='output',
                      help='Base name for output files (without extension)')
    parser.add_argument('--test-mode', action='store_true',
                      help='Run in test mode (only scrape one facility)')
    parser.add_argument('--retry-count', type=int, default=3,
                      help='Number of retries for failed requests')
    parser.add_argument('--protection-strategy', type=str, choices=['auto', 'cloudscraper', 'playwright'],
                      default='auto', help='Protection bypass strategy to use')
    args = parser.parse_args()
    
    success_count = 0
    for idx, url in enumerate(args.url, 1):
        output_base = f"{args.output}_{idx}" if len(args.url) > 1 else args.output
        if scrape_url(url, output_base, args.test_mode, args.retry_count, args.protection_strategy):
            success_count += 1
    
    logger.info(f"Completed scraping {success_count}/{len(args.url)} URLs successfully")
