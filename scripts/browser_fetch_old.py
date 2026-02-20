#!/usr/bin/env python3
"""
Browser automation helper using Playwright with stealth mode
Handles anti-bot sites like Flipkart, Myntra, Snapdeal
"""

import sys
import json
import re
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from playwright_stealth import Stealth

# Site-specific configurations
SITE_CONFIGS = {
    "flipkart.com": {
        "search_url": "https://www.flipkart.com/search?q={query}",
        "product_selector": "a[href*='/p/']",
        "wait_for": "div[data-id]",
        "max_wait": 10000
    },
    "myntra.com": {
        "search_url": "https://www.myntra.com/{query}",
        "product_selector": "a[href*='/product/']",
        "wait_for": "div.search-searchProductsContainer",
        "max_wait": 20000,
        "stealth": True  # Needs extra stealth
    },
    "snapdeal.com": {
        "search_url": "https://www.snapdeal.com/search?keyword={query}",
        "product_selector": "div.product-tuple-listing a.dp-widget-link",
        "wait_for": "div.product-tuple-listing",
        "max_wait": 15000
    },
    "amazon.in": {
        "search_url": "https://www.amazon.in/s?k={query}",
        "product_selector": "a[href*='/dp/']",
        "wait_for": "div[data-component-type='s-search-results']",
        "max_wait": 10000
    }
}

def fetch_with_playwright(domain, query, max_results=3):
    """
    Fetch search results using Playwright (headless browser)
    
    Args:
        domain: Site domain (e.g., 'flipkart.com')
        query: Search query
        max_results: Maximum number of product URLs to return
    
    Returns:
        List of product URLs
    """
    if domain not in SITE_CONFIGS:
        print(f"Error: Unknown domain {domain}", file=sys.stderr)
        return []
    
    config = SITE_CONFIGS[domain]
    
    # URL encode the query properly
    from urllib.parse import quote_plus
    encoded_query = quote_plus(query)
    search_url = config["search_url"].format(query=encoded_query)
    
    print(f"Launching browser for {domain}...", file=sys.stderr)
    
    try:
        with sync_playwright() as p:
            # Launch headless Chromium
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-blink-features=AutomationControlled'
                ]
            )
            
            # Create context with realistic user agent
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # Apply stealth mode to avoid bot detection
            stealth_config = Stealth()
            stealth_config.apply_stealth_sync(page)
            
            print(f"Navigating to {search_url}...", file=sys.stderr)
            page.goto(search_url, wait_until='domcontentloaded', timeout=30000)
            
            # Wait for product results to load
            try:
                page.wait_for_selector(config["wait_for"], timeout=config["max_wait"])
            except PlaywrightTimeout:
                print(f"Warning: Timeout waiting for {config['wait_for']}", file=sys.stderr)
            
            # Extract product URLs
            print(f"Extracting product links...", file=sys.stderr)
            elements = page.query_selector_all(config["product_selector"])
            
            urls = []
            seen = set()
            
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
                
                if clean_url not in seen:
                    urls.append(clean_url)
                    seen.add(clean_url)
                    
                    if len(urls) >= max_results:
                        break
            
            browser.close()
            
            print(f"Found {len(urls)} product URLs", file=sys.stderr)
            return urls
            
    except Exception as e:
        print(f"Error fetching {domain}: {e}", file=sys.stderr)
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
