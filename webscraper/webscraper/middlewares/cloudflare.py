import logging
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
                'desktop': True
            },
            debug=True
        )

    def process_request(self, request, spider):
        # Skip if already processed
        if request.meta.get('cloudflare_processed'):
            return None

        self.logger.debug(f"Processing request through Cloudscraper: {request.url}")
        try:
            response = self.scraper.get(
                request.url,
                headers=dict(request.headers),
                cookies=request.cookies,
                timeout=30
            )
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
