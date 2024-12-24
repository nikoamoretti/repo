import logging
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from playwright.sync_api import sync_playwright
import time
import threading

class PlaywrightMiddleware(UserAgentMiddleware):
    _instance = None
    _lock = threading.Lock()
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        if not hasattr(self, '_browser_initialized'):
            with self._lock:
                if not hasattr(self, '_browser_initialized'):
                    self._setup_browser()
                    self._browser_initialized = True
    
    def _setup_browser(self):
        """Initialize browser in a thread-safe way"""
        if not hasattr(self, 'context'):
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox']
            )
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            )

    def _handle_page(self, url):
        """Handle page navigation and protection bypass using Playwright"""
        page = None
        try:
            with self._lock:
                if not hasattr(self, 'context'):
                    self._setup_browser()
                    
                page = self.context.new_page()
                self.logger.debug(f"Navigating to {url} with Playwright")
                
                # Set shorter timeout for faster initial validation
                response = page.goto(url, wait_until='domcontentloaded', timeout=3000)
                if response is None:
                    self.logger.error("Failed to get response from page")
                    return None, None
                
                # Quick check for common protection patterns
                content = page.content()
                if any(text in content for text in ["Just a moment", "Please wait", "DDoS protection"]):
                    self.logger.debug("Protection detected, waiting for resolution...")
                    time.sleep(1)  # Reduced wait time for faster response
                    content = page.content()  # Get updated content
                
                cookies = page.context.cookies()
                return content, cookies
                
        except Exception as e:
            self.logger.error(f"Playwright navigation failed: {str(e)}")
            return None, None
        finally:
            if page:
                try:
                    page.close()
                except:
                    pass

    def process_request(self, request, spider):
        # Skip if already processed
        if request.meta.get('playwright_processed'):
            return None

        self.logger.info(f"Processing request through Playwright: {request.url}")
        try:
            content, cookies = self._handle_page(request.url)
            
            if content is None:
                self.logger.error("Failed to get content through Playwright")
                return None
            
            # Mark as processed to avoid loops
            request.meta['playwright_processed'] = True
            
            # Convert cookies to header format if needed
            if cookies:
                cookie_header = '; '.join([f"{c['name']}={c['value']}" for c in cookies])
                request.headers['Cookie'] = cookie_header
            
            return HtmlResponse(
                url=request.url,
                body=content.encode('utf-8'),
                encoding='utf-8',
                request=request
            )
        except Exception as e:
            self.logger.error(f"Middleware error: {str(e)}")
            return None

    def spider_opened(self, spider):
        spider.logger.info('Playwright middleware initialized for: %s' % spider.name)

    def spider_closed(self, spider):
        self.logger.info("Closing Playwright browser")
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
