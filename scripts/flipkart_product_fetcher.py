#!/usr/bin/env python3
"""
Enhanced browser fetcher for Flipkart product pages
Uses extended stealth, cookies, and realistic behavior
"""

import sys
import json
import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def fetch_product_page_html(url, max_wait=20):
    """
    Fetch Flipkart product page with enhanced stealth
    
    Args:
        url: Product page URL
        max_wait: Maximum seconds to wait for page load
    
    Returns:
        HTML content string
    """
    try:
        with sync_playwright() as p:
            # Launch with extra stealth args
            browser = p.chromium.launch(
                headless=True,  # Keep headless for server
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                    '--window-size=1920,1080'
                ]
            )
            
            # Create context with realistic viewport and geolocation
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-IN',
                timezone_id='Asia/Kolkata',
                geolocation={'latitude': 28.6139, 'longitude': 77.2090},  # Delhi
                permissions=['geolocation']
            )
            
            page = context.new_page()
            
            # Apply stealth
            stealth_config = Stealth()
            stealth_config.apply_stealth_sync(page)
            
            print(f"Navigating to {url}...", file=sys.stderr)
            
            # Navigate with longer timeout
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Simulate human behavior
            page.wait_for_timeout(2000)  # Wait 2 seconds
            page.mouse.move(100, 100)  # Move mouse
            page.mouse.wheel(0, 300)   # Scroll down
            page.wait_for_timeout(1000)
            page.mouse.wheel(0, -100)  # Scroll up a bit
            page.wait_for_timeout(2000)
            
            # Wait for key elements
            try:
                page.wait_for_selector('div.CEmiEU, div._3eAQiD, span.B_NuCI', timeout=10000)
            except:
                print("Warning: Product elements not found, continuing anyway...", file=sys.stderr)
            
            # Get HTML content
            html = page.content()
            
            browser.close()
            
            print(f"Fetched {len(html)} bytes", file=sys.stderr)
            return html
            
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Fetch Flipkart product page HTML')
    parser.add_argument('--url', required=True, help='Product URL')
    parser.add_argument('--output', help='Output file (optional, prints to stdout by default)')
    
    args = parser.parse_args()
    
    html = fetch_product_page_html(args.url)
    
    if html:
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"Saved to {args.output}", file=sys.stderr)
        else:
            print(html)
        sys.exit(0)
    else:
        print("Failed to fetch page", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
