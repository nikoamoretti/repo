from scrapy import signals
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import requests
import logging
import os
from urllib.parse import urlencode

class CloudflareMiddleware(UserAgentMiddleware):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scraper_api_key = os.getenv('Scraper_API_Key')
        
    def process_request(self, request, spider):
        if not self.scraper_api_key:
            self.logger.error("No Scraper API key found!")
            return None
            
        # Skip if already processed (using meta flag)
        if request.meta.get('scraperapi_processed'):
            return None
            
        # Mark as processed
        request.meta['scraperapi_processed'] = True
        
        # Use urlencode for proper URL encoding
        params = {
            'api_key': self.scraper_api_key,
            'url': request.url,
            'render_js': '1',
            'keep_headers': 'true'
        }
        
        api_url = f"http://api.scraperapi.com/?{urlencode(params)}"
        self.logger.debug(f"Processing URL: {request.url}")
        request._set_url(api_url)
        
        # Set standard headers
        request.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
        })
        return None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
        
    def spider_opened(self, spider):
        spider.logger.info('Scraper API middleware initialized for: %s' % spider.name)
