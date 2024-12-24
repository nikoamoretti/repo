import logging
import time
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import cloudscraper
from twisted.internet.error import TimeoutError

class CloudflareMiddleware(UserAgentMiddleware):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True,
                'mobile': False
            },
            debug=True,
            delay=2,  # Reduced delay for faster initial response
            interpreter='nodejs'
        )
        
    def _handle_cloudflare_challenge(self, url, headers, cookies):
        """Handle Cloudflare challenge with retries and proper delays"""
        max_retries = 3
        retry_delay = 2  # Reduced delay for faster testing
        
        for attempt in range(max_retries):
            try:
                self.logger.debug(f"Cloudflare bypass attempt {attempt + 1}/{max_retries}")
                response = self.scraper.get(
                    url,
                    headers=headers,
                    cookies=cookies,
                    allow_redirects=True,
                    timeout=30
                )
                
                if response.status_code == 403:
                    self.logger.debug("Cloudflare challenge detected, waiting...")
                    time.sleep(retry_delay)
                    continue
                    
                return response
                
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
                
        return None

    def process_request(self, request, spider):
        # Skip if already processed
        if request.meta.get('cloudflare_processed'):
            return None

        self.logger.info(f"Processing request through Cloudscraper: {request.url}")
        try:
            # Prepare headers with common browser-like values
            headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = self._handle_cloudflare_challenge(
                request.url,
                headers=headers,
                cookies=request.cookies
            )
            
            if response is None:
                self.logger.error("Failed to bypass Cloudflare protection after all retries")
                return None
                
            # Mark as processed to avoid loops
            request.meta['cloudflare_processed'] = True
            
            return HtmlResponse(
                url=request.url,
                status=response.status_code,
                headers=response.headers,
                body=response.content,
                encoding='utf-8',
                request=request
            )
        except Exception as e:
            self.logger.error(f"Cloudscraper error: {str(e)}")
            return None

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        return middleware

    def spider_opened(self, spider):
        spider.logger.info('Cloudscraper middleware initialized for: %s' % spider.name)
