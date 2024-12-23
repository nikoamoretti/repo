import asyncio
import pandas as pd
import logging
import re
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from urllib.parse import urljoin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base URL
BASE_URL = "https://www.commtrex.com"
TARGET_URL = urljoin(BASE_URL, "/railcar-storage/us-central-region.html")

# Common browser headers
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0',
}

async def get_page_content(max_retries=3):
    """Fetch the page content using Playwright with retries"""
    logger.info(f"Attempting to fetch content from {TARGET_URL}")
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries}")
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                try:
                    context = await browser.new_context(
                        viewport={'width': 1920, 'height': 1080},
                        user_agent=HEADERS['User-Agent']
                    )
                    
                    # Set cookies for Cloudflare bypass
                    await context.add_cookies([
                        {
                            "name": "cf_clearance",
                            "value": "bj_nWJHPeUkSWDhgr.xGIFvfqWkGNVs2d1Zb28D1l78-1734926283-1.2.1.1-rdZjLFWNwA0H7SAY8V3.Yd2rnnU2K_pdCZ4jhGHJtMJYlNKem3N0H.jU11cajdMEwa8Wcj1fndLvKR2NskgjA2pv5vu5vEMzTieGkfcAs_3cnbTz_ZczbCnZJnEx2xyCEyAvqimX1iEjQTViggyJae9FmhBylGKOauQDBmHNeuYcHuFgotsbIHp3ulNM5CTHu4U82G22lju84Tze1We_PMpnPaLDpdT1ME.QVk8ExyurYB7dh5Ki4dcbHwaNpMUyWtaWZQeTvp6jeTQxWHXPSAjcKjIm1mBl_mxN9c0Q2OvKN246o8sDTAAM.JtfCn.gwo4uH9AZsIrinJv3ZoSZkF21PhDQBzvjBGjsRNzQ4nbZGtPmyj3_cp5hEbQWU6yeMLUt3XNvh2qwAd6Ly6q7RQ",
                            "domain": "commtrex.com",
                            "path": "/"
                        },
                        {
                            "name": "__cf_logged_in",
                            "value": "1",
                            "domain": "cloudflare.com",
                            "path": "/"
                        }
                    ])
                    
                    context.set_default_timeout(30000)
                    page = await context.new_page()
                    await page.set_extra_http_headers(HEADERS)
                    
                    response = await page.goto(TARGET_URL, wait_until='networkidle', timeout=30000)
                    
                    if response is None or not response.ok:
                        logger.error(f"Failed to load page: {response and response.status}")
                        continue
                    
                    await page.wait_for_load_state('networkidle', timeout=30000)
                    
                    content = await page.content()
                    if "Verify you are human" in content:
                        logger.warning("Cloudflare protection detected")
                        if attempt < max_retries - 1:
                            await asyncio.sleep(10)
                            continue
                        return None
                    
                    await page.wait_for_selector('.search-results-list', timeout=30000)
                    logger.info("Found search results list on the page")
                    
                    with open('central_page_content.html', 'w', encoding='utf-8') as f:
                        f.write(content)
                    logger.info("Successfully fetched page content and saved to central_page_content.html")
                    
                    return content
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} failed with error: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)
                continue
    
    logger.error("All attempts to fetch content failed")
    return None

async def scrape_railcar_storage():
    """Scrape railcar storage facility data from the webpage"""
    logger.info("Starting railcar storage data scraping...")
    
    content = await get_page_content()
    if content is None:
        logger.error("Failed to fetch page content")
        return pd.DataFrame()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    try:
        all_facility_data = []
        
        state_sections = soup.find_all('h2', class_='state-header')
        logger.info(f"Found {len(state_sections)} state sections")
        
        for state_section in state_sections:
            current_state = state_section.text.strip()
            logger.info(f"Processing state section: {current_state}")
            
            search_results = state_section.find_next('div', class_='search-results')
            if not search_results:
                logger.warning(f"No search results found for state {current_state}")
                continue
            
            facility_items = search_results.find_all('div', class_='list-item-container')
            logger.info(f"Found {len(facility_items)} facilities in {current_state}")
            
            for item in facility_items:
                facility_info = {
                    'State': '',
                    'Facility Name': '',
                    'Location': '',
                    'Railroad Connections': '',
                    'Total Spaces': None,
                    'Hazmat Suitable': 'No'
                }
                
                name_link = item.find('a', class_='list-title')
                if name_link:
                    facility_info['Facility Name'] = name_link.text.strip()
                
                list_attributes = item.find_all(['div', 'span'], class_=['list-attribute', 'facility-attribute'])
                
                for attr in list_attributes:
                    icon = attr.find('i')
                    text_div = attr.find(['div', 'span'], class_=['list-attribute-text', 'facility-attribute-text'])
                    
                    if not icon or not text_div:
                        continue
                        
                    text = text_div.text.strip()
                    icon_classes = icon.get('class', [])
                    
                    if any(marker in icon_classes for marker in ['fa-map-marker', 'fa-location-dot']):
                        facility_info['Location'] = text
                        if ',' in text:
                            state_abbrev = text.split(',')[-1].strip()
                            facility_info['State'] = state_abbrev
                    
                    elif 'ci-railroad' in ' '.join(icon_classes):
                        facility_info['Railroad Connections'] = text.strip()
                    
                    elif 'fa-cubes' in icon_classes:
                        try:
                            # First remove commas from the text to handle numbers like "3,000"
                            text_no_commas = text.replace(',', '')
                            # Then convert to lowercase for case-insensitive matching
                            cleaned_text = text_no_commas.lower()
                            # Search for the number pattern
                            spaces = re.search(r'(\d+)\s*total\s*spaces', cleaned_text)
                            if spaces:
                                facility_info['Total Spaces'] = int(spaces.group(1))
                            logger.info(f"Parsed spaces from text: {text} -> {spaces.group(1) if spaces else 'None'}")
                        except ValueError as e:
                            logger.warning(f"Could not parse Total Spaces from text: {text}. Error: {str(e)}")
                    
                    elif any(warning in icon_classes for warning in ['fa-warning', 'fa-triangle-exclamation']):
                        facility_info['Hazmat Suitable'] = 'Yes'
                
                all_facility_data.append(facility_info)
        
        df = pd.DataFrame(all_facility_data)
        df.to_csv('central_railcar_storage_data.csv', index=False)
        logger.info("Data successfully saved to central_railcar_storage_data.csv")
        return df
    
    except Exception as e:
        logger.error(f"Error processing facility data: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    asyncio.run(scrape_railcar_storage())
