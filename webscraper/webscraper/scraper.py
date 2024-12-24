from playwright.sync_api import sync_playwright
import logging
import time

class WebScraper:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        # Add console handler if not already present
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
        self._setup_browser()

    def _setup_browser(self):
        """Initialize browser with optimized settings"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-gpu',
                '--disable-dev-shm-usage',
                '--disable-setuid-sandbox',
                '--no-first-run',
                '--no-zygote',
                '--deterministic-fetch',
                '--disable-features=IsolateOrigins',
                '--disable-site-isolation-trials',
                '--disable-web-security',
                '--disable-features=IsolateOrigins,site-per-process',
                '--enable-features=NetworkService,NetworkServiceInProcess',
                '--force-color-profile=srgb',
                '--disable-accelerated-2d-canvas',
                '--disable-background-networking',
                '--metrics-recording-only',
                '--disable-default-apps',
                '--mute-audio'
            ]
        )
        
        # Enhanced browser context with modern Chrome properties
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            bypass_csp=True,
            ignore_https_errors=True,
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"'
            }
        )

    def scrape_url(self, url):
        """Scrape a URL and return the content"""
        page = None
        start_time = time.time()
        self.logger.debug(f"Starting scrape of {url}")
        
        try:
            page = self.context.new_page()
            self.logger.debug(f"Created new page for {url}")
            
            # Optimized initial load with shorter timeout
            self.logger.debug("Attempting page navigation...")
            response = page.goto(url, wait_until='commit', timeout=2000)
            if response is None:
                self.logger.error("Failed to get response from page")
                return None
            
            self.logger.debug(f"Initial page load took {time.time() - start_time:.2f} seconds")
            
            # Enhanced protection bypass with multiple verification steps
            def wait_for_real_content():
                try:
                    # Wait for Cloudflare challenge to disappear
                    page.wait_for_selector('body:not(:has-text("Just a moment"))', timeout=10000)
                    page.wait_for_selector('body:not(:has-text("Please wait"))', timeout=5000)
                    page.wait_for_selector('body:not(:has-text("DDoS protection"))', timeout=5000)
                    
                    # Wait for actual content indicators
                    content_selectors = [
                        '.container',
                        'main',
                        '#content',
                        '.content',
                        'article'
                    ]
                    
                    for selector in content_selectors:
                        try:
                            page.wait_for_selector(selector, timeout=2000)
                            self.logger.debug(f"Found content with selector: {selector}")
                            return True
                        except:
                            continue
                    
                    return False
                except Exception as e:
                    self.logger.debug(f"Error waiting for content: {str(e)}")
                    return False

            # Initial page load check
            content = page.content()
            if any(text in content for text in ["Just a moment", "Please wait", "DDoS protection"]):
                self.logger.debug("Protection detected, implementing advanced bypass...")
                
                # Multiple retry attempts
                for attempt in range(3):
                    self.logger.debug(f"Bypass attempt {attempt + 1}")
                    
                    # Wait for challenge to complete and content to load
                    if wait_for_real_content():
                        self.logger.debug("Successfully bypassed protection")
                        break
                    
                    # If still on challenge page, try refreshing
                    if attempt < 2:  # Don't refresh on last attempt
                        self.logger.debug("Refreshing page...")
                        page.reload(wait_until='networkidle')
                
                # Final verification
                page.wait_for_load_state('networkidle', timeout=5000)
                content = page.content()
            
            # Debug: Log page content
            self.logger.debug("Page HTML structure:")
            self.logger.debug(page.content())
            
            # Enhanced facility data extraction with exact selectors from page analysis
            data = page.evaluate("""() => {
                console.log('Starting facility extraction...');
                
                // Get all facility containers
                const facilityContainers = document.querySelectorAll('.list-item-container');
                console.log(`Found ${facilityContainers.length} facility containers`);
                
                const facilities = Array.from(facilityContainers).map(container => {
                    // Extract facility name from list-title
                    const nameElement = container.querySelector('a.list-title');
                    const name = nameElement ? nameElement.textContent.trim() : '';
                    console.log('Found facility:', name);
                    
                    // Get all attribute texts
                    const attributeElements = container.querySelectorAll('.list-attribute-text');
                    const attributes = Array.from(attributeElements).map(el => el.textContent.trim());
                    
                    // Find products (contains Bulk, Goods, etc.)
                    const products = attributes.find(text => 
                        text.includes('Bulk') || 
                        text.includes('Goods') || 
                        text.includes('Liquids') || 
                        text.includes('Oversized')
                    );
                    
                    // Find railroads (contains CSX, NS, etc.)
                    const railroads = attributes.find(text => 
                        text.includes('CSX') || 
                        text.includes('NS') || 
                        text.includes('rail')
                    );
                    
                    // Find hazmat capabilities
                    const hazmat = attributes.find(text => text.includes('HazMat'));
                    
                    // Check if facility is verified
                    const isVerified = container.querySelector('.icon-transload-verified-sm') !== null;
                    
                    return {
                        name,
                        products: products ? products.split(', ').filter(p => p) : [],
                        railroads: railroads ? railroads.split(', ').filter(r => r !== 'not served by rail') : [],
                        hazmat_capable: hazmat ? hazmat.includes('Capable of HazMat') : false,
                        type: isVerified ? 'verified' : 'unverified'
                    };
                });
                
                console.log(`Processed ${facilities.length} facilities`);
                return {
                    title: document.title,
                    facilities: facilities
                };
            }""")
            
            if not data or 'facilities' not in data:
                self.logger.error("No facilities data found in page")
                raise ValueError("No facilities data found in page")

            self.logger.debug(f"Found {len(data.get('facilities', []))} facilities")
            return {
                'url': url,
                'title': data.get('title', ''),
                'facilities': data.get('facilities', [])
            }
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {str(e)}")
            return None
        finally:
            if page:
                try:
                    page.close()
                except:
                    pass

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
