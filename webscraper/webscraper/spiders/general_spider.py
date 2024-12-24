import scrapy
import logging
from ..scraper import WebScraper


class GeneralSpiderSpider(scrapy.Spider):
    name = "general_spider"
    
    def __init__(self, url=None, *args, **kwargs):
        super(GeneralSpiderSpider, self).__init__(*args, **kwargs)
        self.start_urls = ["http://example.com"] if not url else [url]
        self.scraper = WebScraper()
        self.logger = logging.getLogger(__name__)
    
    def start_requests(self):
        for url in self.start_urls: 
            self.logger.info(f"Starting scrape for URL: {url}")
            try:
                # Use our custom scraper
                data = self.scraper.scrape_url(url)
                if data:
                    self.logger.info(f"Successfully scraped {url}")
                    # Create a fake request/response cycle to maintain Scrapy's flow
                    yield scrapy.Request(
                        url=url,
                        callback=self.parse,
                        errback=self.errback,
                        dont_filter=True,
                        meta={'playwright_data': data}
                    )
                else:
                    self.logger.error(f"Failed to scrape {url}")
            except Exception as e:
                self.logger.error(f"Error scraping {url}: {str(e)}")
    
    def parse(self, response):
        try:
            # Use the data from our custom scraper
            data = response.meta.get('playwright_data')
            if data:
                self.logger.info(f"Processing scraped data from {response.url}")
                yield data
            else:
                self.logger.error(f"No data available for {response.url}")
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {str(e)}")
    
    def errback(self, failure):
        self.logger.error(f"Request failed: {failure.value}")
    
    def closed(self, reason):
        # Clean up resources
        if hasattr(self, 'scraper'):
            self.scraper.close()
