#!/usr/bin/env python3
"""
Flipkart product page analyzer with enhanced stealth
Fetches product page HTML and runs trustworthiness analysis
"""

import sys
import os
import json
import subprocess
import tempfile
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def fetch_flipkart_product(url):
    """Fetch Flipkart product page with enhanced stealth"""
    try:
        with sync_playwright() as p:
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
            
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-IN',
                timezone_id='Asia/Kolkata'
            )
            
            page = context.new_page()
            
            # Apply stealth
            stealth_config = Stealth()
            stealth_config.apply_stealth_sync(page)
            
            # Navigate
            page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            # Simulate human behavior
            page.wait_for_timeout(2000)
            page.mouse.wheel(0, 300)
            page.wait_for_timeout(1000)
            
            html = page.content()
            browser.close()
            
            return html
            
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def analyze_flipkart_product(url):
    """Fetch and analyze a Flipkart product page"""
    
    # Fetch HTML
    html = fetch_flipkart_product(url)
    if not html:
        return None
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html)
        tmp_file = f.name
    
    try:
        # Run analyzer
        analyzer_path = os.path.join(os.path.dirname(__file__), "analyze_from_html.py")
        result = subprocess.run(
            ["python3", analyzer_path, "--url", url, "--html_file", tmp_file],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Analyzer error: {result.stderr}", file=sys.stderr)
            return None
            
    finally:
        # Cleanup
        try:
            os.unlink(tmp_file)
        except:
            pass

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze Flipkart product page')
    parser.add_argument('--url', required=True, help='Product URL')
    
    args = parser.parse_args()
    
    result = analyze_flipkart_product(args.url)
    
    if result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    else:
        print(json.dumps({"error": "Failed to analyze product"}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
