from scrapy import signals
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

class CloudflareChallengeMiddleware:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware
        
    def process_response(self, request, response, spider):
        if response.status == 403 or response.status == 503:
            self.logger.info("Detected Cloudflare challenge, attempting to solve...")
            
            # Setup Chrome options for enhanced fingerprinting
            chrome_options = Options()
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--disable-software-rasterizer')
            chrome_options.add_argument('--lang=en-US,en')
            chrome_options.add_argument(f'user-agent={request.headers["User-Agent"].decode()}')
            
            # Create driver and wait for challenge to complete
            driver = webdriver.Chrome(options=chrome_options)
            try:
                driver.get(request.url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Wait for potential challenge frame
                time.sleep(5)
                
                # Get the page source after challenge
                body = driver.page_source
                response = response.replace(body=body.encode())
                return response
                
            except Exception as e:
                self.logger.error(f"Error solving Cloudflare challenge: {str(e)}")
                return response
            finally:
                driver.quit()
                
        return response
        
    def spider_closed(self):
        self.logger.info("Spider closed, cleaning up resources...")
