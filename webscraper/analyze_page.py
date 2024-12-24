import logging
logging.basicConfig(level=logging.DEBUG)
from webscraper.scraper import WebScraper

def analyze_page_structure():
    scraper = WebScraper()
    try:
        page = scraper.context.new_page()
        page.goto('https://www.commtrex.com/transloading/ga/atlanta.html', wait_until='networkidle')
        
        # Wait for real content with enhanced checks
        page.wait_for_selector('body:not(:has-text("Just a moment"))', timeout=15000)
        page.wait_for_load_state('networkidle')
        page.wait_for_load_state('domcontentloaded')
        
        # Wait for main content sections and analyze structure
        print("\nWaiting for content to load...")
        
        # Wait for search results section
        search_results = page.wait_for_selector('section.search-results', timeout=10000)
        print("\nFound search results section")
        
        # Get the HTML structure for debugging
        html_structure = page.evaluate('''() => {
            const getStructure = (element, depth = 0) => {
                if (!element) return '';
                const indent = ' '.repeat(depth * 2);
                const classes = Array.from(element.classList).join('.');
                const id = element.id ? `#${element.id}` : '';
                const tag = element.tagName.toLowerCase();
                let structure = `${indent}${tag}${classes ? '.' + classes : ''}${id}\n`;
                
                for (const child of element.children) {
                    structure += getStructure(child, depth + 1);
                }
                return structure;
            };
            
            const searchResults = document.querySelector('section.search-results');
            return searchResults ? getStructure(searchResults) : 'Search results section not found';
        }''')
        
        print("\nHTML Structure of search results section:")
        print(html_structure)
        
        # Wait for and analyze a single facility
        print("\nAnalyzing first facility...")
        facility_data = page.evaluate('''() => {
            const searchResults = document.querySelector('section.search-results');
            if (!searchResults) return null;
            
            // Find all text nodes and their context
            function getAllTextNodes(element) {
                const texts = [];
                const walk = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, null, false);
                let node;
                while (node = walk.nextNode()) {
                    const text = node.textContent.trim();
                    if (text) {
                        const parentClasses = Array.from(node.parentElement.classList).join('.');
                        texts.push({
                            text: text,
                            parentTag: node.parentElement.tagName.toLowerCase(),
                            parentClasses: parentClasses,
                            fullPath: getElementPath(node.parentElement)
                        });
                    }
                }
                return texts;
            }
            
            // Get unique CSS path to element
            function getElementPath(element) {
                const path = [];
                while (element && element.nodeType === Node.ELEMENT_NODE) {
                    let selector = element.nodeName.toLowerCase();
                    if (element.id) {
                        selector += '#' + element.id;
                    } else {
                        const classes = Array.from(element.classList).join('.');
                        if (classes) {
                            selector += '.' + classes;
                        }
                    }
                    path.unshift(selector);
                    element = element.parentNode;
                }
                return path.join(' > ');
            }
            
            // Get all text content with context
            const textNodes = getAllTextNodes(searchResults);
            return {
                textNodes: textNodes.slice(0, 50), // Limit to first 50 text nodes for readability
                totalNodes: textNodes.length
            };
        }''')
        
        # Analyze page structure
        structure = page.evaluate('''() => {
            function analyzeElement(el, isParent = false) {
                function getTextContent(element) {
                    if (!element) return '';
                    // Remove any script tags to avoid getting script content
                    const clone = element.cloneNode(true);
                    const scripts = clone.getElementsByTagName('script');
                    while (scripts.length > 0) {
                        scripts[0].parentNode.removeChild(scripts[0]);
                    }
                    return clone.textContent.trim();
                }
                
                const details = {
                    tag: el.tagName.toLowerCase(),
                    id: el.id,
                    classes: Array.from(el.classList),
                    text: getTextContent(el).substring(0, 200)
                };
                
                if (isParent) {
                    // Look for specific data points within the element
                    details.facilityName = el.querySelector('h1, h2, h3, [class*="name"], [class*="title"]')?.textContent.trim() || '';
                    details.products = Array.from(el.querySelectorAll('[class*="product"], [class*="commodity"]')).map(e => e.textContent.trim());
                    details.railroads = Array.from(el.querySelectorAll('[class*="rail"], [class*="carrier"]')).map(e => e.textContent.trim());
                    details.hazmat = Array.from(el.querySelectorAll('[class*="hazmat"], [class*="capability"]')).map(e => e.textContent.trim());
                    details.isVerified = !!el.querySelector('.icon-transload-verified-sm');
                }
                
                return details;
            }
            
            // Find facility containers and their parent elements
            const facilityElements = document.querySelectorAll('.entity-flag.transload-location');
            const facilities = Array.from(facilityElements).map(el => {
                // Get the parent container that holds all facility info
                const parentContainer = el.closest('[class*="facility"], [class*="listing"], [class*="result"], .card, article');
                if (!parentContainer) return null;
                
                return {
                    container: analyzeElement(parentContainer, true),
                    flag: analyzeElement(el)
                };
            }).filter(Boolean);
            
            // Also look for sections that might contain facility groups
            const sections = Array.from(document.querySelectorAll('section')).map(section => ({
                section: analyzeElement(section),
                facilities: Array.from(section.querySelectorAll('.entity-flag.transload-location')).length
            }));
            
            return {
                facilities,
                sections
            };
        }''')
        
        print('\nDetailed Content Analysis:')
        if facility_data:
            print(f'\nTotal text nodes found: {facility_data["totalNodes"]}')
            print('\nFirst 50 text nodes with context:')
            for node in facility_data['textNodes']:
                print(f'\nText: {node["text"]}')
                print(f'Parent Tag: {node["parentTag"]}')
                print(f'Parent Classes: {node["parentClasses"]}')
                print(f'Full Path: {node["fullPath"]}')
                print('-' * 80)
        else:
            print('No facility data found')
            
    finally:
        scraper.close()

if __name__ == '__main__':
    analyze_page_structure()
