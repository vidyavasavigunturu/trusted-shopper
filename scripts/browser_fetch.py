#!/usr/bin/env python3
"""
Enhanced browser fetcher with retry logic and better URL encoding
Fixes Amazon search and multi-word query issues
"""

import sys
import json
import re
import time
from urllib.parse import quote_plus
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth

# Site-specific configurations
SITE_CONFIGS = {
    "flipkart.com": {
        "search_url": "https://www.flipkart.com/search?q={query}",
        "product_selector": "a[href*='/p/']",
        "wait_for": "div[data-id]",
        "wait_for_backup": "div._75nlfW",  # Backup selector
        "max_wait": 10000,
        "retry_delay": 2
    },
    "amazon.in": {
        "search_url": "https://www.amazon.in/s?k={query}",
        "product_selector": "div[data-asin]",  # Get ASIN divs instead of links
        "wait_for": "div.s-result-list",
        "wait_for_backup": "div[data-asin]",
        "max_wait": 15000,
        "retry_delay": 10,  # Longer delay for Amazon rate limiting
        "use_asin": True  # Special flag to extract ASIN and build URLs
    },
    "myntra.com": {
        "search_url": "https://www.myntra.com/{query}",
        "product_selector": "a[href*='/product/']",
        "wait_for": "div.search-searchProductsContainer",
        "wait_for_backup": "li.product-base",
        "max_wait": 20000,
        "retry_delay": 2
    },
    "snapdeal.com": {
        "search_url": "https://www.snapdeal.com/search?keyword={query}",
        "product_selector": "div.product-tuple-listing a.dp-widget-link",
        "wait_for": "div.product-tuple-listing",
        "wait_for_backup": "section.js-products",
        "max_wait": 15000,
        "retry_delay": 2
    },
    "bajajelectricals.com": {
        "search_url": "https://www.bajajelectricals.com/search?q={query}",
        "product_selector": "a[href*='/products/']",
        "wait_for": "div.grid-product",
        "wait_for_backup": "a[href*='/products/']",
        "max_wait": 10000,
        "retry_delay": 2
    },
    "clovia.com": {
        "search_url": "https://www.clovia.com/search?q={query}",
        "product_selector": "a[href*='/product/']",
        "wait_for": "div.product-card",
        "wait_for_backup": "a[href*='/product/']",
        "max_wait": 10000,
        "retry_delay": 2
    },
    "campusshoes.com": {
        "search_url": "https://www.campusshoes.com/search?q={query}",
        "product_selector": "a[href*='/products/']",
        "wait_for": "div.product-item",
        "wait_for_backup": "a[href*='/products/']",
        "max_wait": 10000,
        "retry_delay": 2
    }
}

def fetch_with_playwright(domain, query, max_results=3, retry=True):
    """
    Fetch search results using Playwright with enhanced reliability
    
    Args:
        domain: Site domain (e.g., 'flipkart.com')
        query: Search query (will be properly URL-encoded)
        max_results: Maximum number of product URLs to return
        retry: Whether to retry on failure
    
    Returns:
        List of product URLs
    """
    if domain not in SITE_CONFIGS:
        print(f"Error: Unknown domain {domain}", file=sys.stderr)
        return []
    
    config = SITE_CONFIGS[domain]
    
    # Properly URL-encode the query
    encoded_query = quote_plus(query)
    search_url = config["search_url"].format(query=encoded_query)
    
    print(f"Searching {domain} for: {query}", file=sys.stderr)
    print(f"URL: {search_url}", file=sys.stderr)
    
    try:
        with sync_playwright() as p:
            # Launch with stealth args
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--window-size=1920,1080'
                ]
            )
            
            # Create context with realistic settings
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-IN',
                timezone_id='Asia/Kolkata'
            )
            
            page = context.new_page()
            
            # Apply stealth mode
            stealth_config = Stealth()
            stealth_config.apply_stealth_sync(page)
            
            # Add extra delay before navigation (helps with rate limiting)
            time.sleep(config.get('retry_delay', 2))
            
            print(f"Navigating to {search_url}...", file=sys.stderr)
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            
            # Simulate human behavior
            page.wait_for_timeout(2000)
            page.mouse.move(100, 100)
            page.mouse.wheel(0, 300)  # Scroll down
            page.wait_for_timeout(1500)
            
            # Wait for product results - try primary selector first
            try:
                page.wait_for_selector(config["wait_for"], timeout=config["max_wait"])
                print(f"✓ Found primary selector: {config['wait_for']}", file=sys.stderr)
            except PlaywrightTimeout:
                # Try backup selector
                if config.get("wait_for_backup"):
                    try:
                        page.wait_for_selector(config["wait_for_backup"], timeout=5000)
                        print(f"✓ Found backup selector: {config['wait_for_backup']}", file=sys.stderr)
                    except:
                        print(f"Warning: Neither selector found, continuing anyway...", file=sys.stderr)
                else:
                    print(f"Warning: Timeout waiting for {config['wait_for']}", file=sys.stderr)
            
            # Additional wait for JavaScript to render
            page.wait_for_timeout(2000)
            
            # Extract product URLs
            print(f"Extracting product links with selector: {config['product_selector']}", file=sys.stderr)
            elements = page.query_selector_all(config["product_selector"])
            
            print(f"Found {len(elements)} elements", file=sys.stderr)
            
            urls = []
            seen = set()
            
            # Special handling for Amazon ASIN extraction
            if config.get('use_asin') and domain == 'amazon.in':
                for elem in elements:
                    asin = elem.get_attribute('data-asin')
                    if asin and len(asin) == 10:  # Valid ASIN format
                        url = f"https://www.amazon.in/dp/{asin}"
                        if url not in seen:
                            urls.append(url)
                            seen.add(url)
                            if len(urls) >= max_results:
                                break
            else:
                # Standard link extraction for other sites
                for elem in elements:
                    href = elem.get_attribute('href')
                    if not href:
                        continue
                    
                    # Make absolute URL
                    if href.startswith('/'):
                        href = f"https://{domain}{href}"
                    elif not href.startswith('http'):
                        continue
                    
                    # Clean URL (remove query params for deduplication)
                    clean_url = href.split('?')[0]
                    
                    # Validate URL contains expected patterns
                    if domain == 'flipkart.com' and '/p/' not in clean_url:
                        continue
                    if domain == 'bajajelectricals.com' and '/products/' not in clean_url:
                        continue
                    if domain == 'clovia.com' and '/product/' not in clean_url:
                        continue
                    if domain == 'campusshoes.com' and '/products/' not in clean_url:
                        continue
                    
                    if clean_url not in seen:
                        urls.append(clean_url)
                        seen.add(clean_url)
                        
                        if len(urls) >= max_results:
                            break
            
            browser.close()
            
            print(f"Successfully extracted {len(urls)} product URLs", file=sys.stderr)
            return urls
            
    except Exception as e:
        print(f"Error fetching {domain}: {e}", file=sys.stderr)
        
        # Retry once if enabled and this is first attempt
        if retry:
            print(f"Retrying {domain} after {config.get('retry_delay', 3)} seconds...", file=sys.stderr)
            time.sleep(config.get('retry_delay', 3))
            return fetch_with_playwright(domain, query, max_results, retry=False)
        
        return []

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch product URLs using Playwright')
    parser.add_argument('--domain', required=True, help='Site domain (e.g., flipkart.com)')
    parser.add_argument('--query', required=True, help='Search query')
    parser.add_argument('--max-results', type=int, default=3, help='Max results to return')
    
    args = parser.parse_args()
    
    urls = fetch_with_playwright(args.domain, args.query, args.max_results)
    
    # Output as JSON
    print(json.dumps({
        "domain": args.domain,
        "query": args.query,
        "urls": urls,
        "count": len(urls)
    }))

if __name__ == "__main__":
    main()
