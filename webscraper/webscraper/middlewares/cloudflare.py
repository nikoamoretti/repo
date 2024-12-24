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
            
        # Skip if already processed or if it's a ScraperAPI URL
        if 'api.scraperapi.com' in request.url:
            return None
            
        original_url = request.url
        self.logger.debug(f"Processing URL: {original_url}")
        
        # Build the API URL securely
        params = {
            'api_key': self.scraper_api_key,
            'url': original_url,
            'render_js': '1'
        }
        
        # Create new request to ScraperAPI
        api_url = f"http://api.scraperapi.com/?{urlencode(params)}"
        
        # Update the request
        request._set_url(api_url)
        request.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Store original URL for reference
        request.meta['original_url'] = original_url
        
        return None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware
        
    def spider_opened(self, spider):
        spider.logger.info('Scraper API middleware initialized for: %s' % spider.name)
