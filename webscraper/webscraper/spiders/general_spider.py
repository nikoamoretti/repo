import scrapy
import logging


class GeneralSpiderSpider(scrapy.Spider):
    name = "general_spider"
    
    def __init__(self, url=None, *args, **kwargs):
        super(GeneralSpiderSpider, self).__init__(*args, **kwargs)
        self.start_urls = ["http://example.com"] if not url else [url]
        self.logger = logging.getLogger(__name__)
    
    def start_requests(self):
        for url in self.start_urls:
            self.logger.info(f"Starting request for URL: {url}")
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                errback=self.errback,
                dont_filter=True,
                meta={'original_url': url}
            )
    
    def parse(self, response):
        self.logger.info(f"Received response from: {response.url}")
        
        try:
            # Basic content extraction
            title = response.css('title::text').get()
            text_content = ' '.join(response.css('body ::text').getall()).strip()
            links = response.css('a::attr(href)').getall()
            
            # Log successful extraction
            self.logger.info(f"Successfully extracted content from {response.meta.get('original_url')}")
            
            yield {
                'url': response.meta.get('original_url'),
                'title': title,
                'text_content': text_content[:1000],  # First 1000 chars for testing
                'links': links[:10]  # First 10 links for testing
            }
            
        except Exception as e:
            self.logger.error(f"Error processing {response.url}: {str(e)}")
    
    def errback(self, failure):
        self.logger.error(f"Request failed: {failure.value}")
