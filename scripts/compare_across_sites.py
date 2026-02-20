#!/usr/bin/env python3
"""
Multi-site product comparison script for Trusted Shopper
Searches across bot-friendly e-commerce sites and returns comparison data
"""

import json
import sys
import argparse
import subprocess
import tempfile
import os
import re
from urllib.parse import quote_plus
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Bot-friendly and browser-automation sites
SEARCH_SITES = [
    {
        "name": "Amazon.in",
        "search_url": "https://www.amazon.in/s?k={query}",
        "domain": "amazon.in",
        "pattern": r'href="(/[^"]*?/dp/[A-Z0-9]{10})',
        "method": "browser",  # Use browser for better reliability
        "enabled": True
    },
    {
        "name": "Flipkart",
        "search_url": "https://www.flipkart.com/search?q={query}",
        "domain": "flipkart.com",
        "pattern": None,  # Use browser
        "method": "browser",  # Requires Playwright
        "enabled": True
    },
    {
        "name": "Myntra",
        "search_url": "https://www.myntra.com/{query}",
        "domain": "myntra.com",
        "pattern": None,
        "method": "browser",
        "enabled": False  # Blocks headless browsers aggressively
    },
    {
        "name": "Snapdeal",
        "search_url": "https://www.snapdeal.com/search?keyword={query}",
        "domain": "snapdeal.com",
        "pattern": None,
        "method": "browser",
        "enabled": False  # Cloudflare blocking
    },
    {
        "name": "Firstcry",
        "search_url": "https://www.firstcry.com/search?searchstring={query}",
        "domain": "firstcry.com",
        "pattern": r'href="(/[^"]+?/product-detail[^"]*)"',
        "method": "fetch",
        "enabled": True
    },
    {
        "name": "Chumbak",
        "search_url": "https://www.chumbak.com/search?q={query}",
        "domain": "chumbak.com",
        "pattern": r'href="(/products/[^"]+?)"',
        "method": "fetch",
        "enabled": True
    },
    {
        "name": "Vijay Sales",
        "search_url": "https://www.vijaysales.com/search/{query}",
        "domain": "vijaysales.com",
        "pattern": r'href="(/[^"]+?-\d+)"',
        "method": "fetch",
        "enabled": True
    },
    {
        "name": "Bajaj Electricals",
        "search_url": "https://www.bajajelectricals.com/search?q={query}",
        "domain": "bajajelectricals.com",
        "pattern": r'href="(/products/[^"]+)"',
        "method": "browser",
        "enabled": True
    },
    {
        "name": "Clovia",
        "search_url": "https://www.clovia.com/search?q={query}",
        "domain": "clovia.com",
        "pattern": r'href="(/product/[^"]+)"',
        "method": "browser",
        "enabled": True
    },
    {
        "name": "Campus Shoes",
        "search_url": "https://www.campusshoes.com/search?q={query}",
        "domain": "campusshoes.com",
        "pattern": r'href="(https://www\.campusshoes\.com/products/[^"]+)"',
        "method": "browser",
        "enabled": True
    },
]

def fetch_with_browser(domain, query, max_results=3):
    """Fetch product URLs using Playwright (for anti-bot sites)"""
    try:
        # Call the browser_fetch.py script
        import subprocess
        script_path = os.path.join(os.path.dirname(__file__), "browser_fetch.py")
        
        result = subprocess.run(
            ["python3", script_path, "--domain", domain, "--query", query, "--max-results", str(max_results)],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return data.get("urls", [])
        else:
            print(f"Browser fetch error for {domain}: {result.stderr}", file=sys.stderr)
            return []
    except Exception as e:
        print(f"Browser fetch exception for {domain}: {e}", file=sys.stderr)
        return []

def fetch_url(url):
    """Fetch URL using curl with user agent and gzip support"""
    try:
        result = subprocess.run(
            ["curl", "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64)", "-s", "-L", "--compressed", "--max-time", "10", url],
            capture_output=True,
            text=True,
            timeout=15,
            errors='replace'  # Handle encoding issues gracefully
        )
        return result.stdout if result.returncode == 0 else None
    except Exception as e:
        print(f"Error fetching {url}: {e}", file=sys.stderr)
        return None

def extract_product_urls(html, domain, pattern, max_results=3):
    """Extract multiple product URLs from search results"""
    import re
    
    matches = re.findall(pattern, html, re.DOTALL)
    
    # Build full URLs and deduplicate
    urls = []
    seen = set()
    
    for match in matches:
        # Clean up URL based on domain
        if domain == "amazon.in":
            url = f"https://www.amazon.in{match.split('?')[0]}"
        elif domain == "ebay.in":
            url = match.split('?')[0] if match.startswith('http') else f"https://www.ebay.in{match}"
        elif domain == "shopclues.com":
            # ShopClues uses seoname from JSON
            url = f"https://www.shopclues.com/{match}.html"
        elif domain == "firstcry.com":
            url = f"https://www.firstcry.com{match}"
        elif domain == "bewakoof.com":
            url = f"https://www.bewakoof.com{match}"
        elif domain == "chumbak.com":
            url = f"https://www.chumbak.com{match}"
        elif domain == "croma.com":
            url = f"https://www.croma.com{match}"
        elif domain == "vijaysales.com":
            url = f"https://www.vijaysales.com{match}"
        elif domain == "poorvika.com":
            url = f"https://www.poorvika.com{match}"
        else:
            continue
        
        # Remove query params for cleaner URLs
        clean_url = url.split('?')[0] if '?' in url else url
        
        if clean_url not in seen:
            urls.append(clean_url)
            seen.add(clean_url)
            if len(urls) >= max_results:
                break
    
    return urls

def analyze_product_page(url, tmp_dir):
    """Fetch and analyze a single product page"""
    
    # Special handling for Flipkart product pages
    if 'flipkart.com' in url and '/p/' in url:
        return analyze_flipkart_product_page(url, tmp_dir)
    
    # Standard fetch for other sites
    html = fetch_url(url)
    if not html:
        return None
    
    # Save to temp file
    tmp_file = os.path.join(tmp_dir, f"page_{hash(url)}.html")
    with open(tmp_file, "w", encoding="utf-8", errors="ignore") as f:
        f.write(html)
    
    # Run analyzer
    try:
        analyzer_path = os.path.join(
            os.path.dirname(__file__),
            "analyze_from_html.py"
        )
        result = subprocess.run(
            ["python3", analyzer_path, "--url", url, "--html_file", tmp_file],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
    except Exception as e:
        print(f"Error analyzing {url}: {e}", file=sys.stderr)
    
    return None

def analyze_flipkart_product_page(url, tmp_dir):
    """Special handler for Flipkart product pages with enhanced stealth"""
    try:
        # Call the specialized Flipkart analyzer
        analyzer_script = os.path.join(os.path.dirname(__file__), "analyze_flipkart.py")
        result = subprocess.run(
            ["python3", analyzer_script, "--url", url],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        else:
            print(f"Flipkart analyzer error: {result.stderr}", file=sys.stderr)
            return None
            
    except Exception as e:
        print(f"Error analyzing Flipkart product {url}: {e}", file=sys.stderr)
        return None

def search_site(site, product_name, max_products, tmp_dir):
    """Search a single site and return results - designed for parallel execution"""
    query = quote_plus(product_name)
    search_url = site["search_url"].format(query=query)
    site_results = []
    
    print(f"⏳ Searching {site['name']}...", file=sys.stderr, flush=True)
    
    try:
        # Fetch product URLs with timeout handling
        if site.get('method') == 'browser':
            product_urls = fetch_with_browser(site["domain"], product_name, max_products)
        else:
            html = fetch_url(search_url)
            if not html:
                print(f"⚠️  {site['name']}: Failed to fetch", file=sys.stderr, flush=True)
                return site_results
            product_urls = extract_product_urls(html, site["domain"], site["pattern"], max_products)
        
        if not product_urls:
            print(f"⚠️  {site['name']}: No products found", file=sys.stderr, flush=True)
            return site_results
            
        print(f"✅ {site['name']}: Found {len(product_urls)} products", file=sys.stderr, flush=True)
        
        # Analyze each product
        for idx, url in enumerate(product_urls, 1):
            try:
                analysis = analyze_product_page(url, tmp_dir)
                if analysis:
                    return_policy = analysis.get("return_policy_analysis", {})
                    warranty = analysis.get("warranty_support_analysis", {})
                    hidden_costs = analysis.get("hidden_costs_analysis", {})
                    
                    site_results.append({
                        "site": site["name"],
                        "url": url,
                        "price": analysis.get("price_guess"),
                        "scores": analysis.get("scores", {}),
                        "title": analysis.get("title_guess", "")[:80],
                        "return_policy": {
                            "window_days": return_policy.get("return_window_days"),
                            "type": return_policy.get("type", []),
                            "method": return_policy.get("method", []),
                            "flexibility_score": return_policy.get("flexibility_score", 50),
                            "highlights": return_policy.get("highlights", [])[:2]
                        },
                        "warranty": {
                            "duration_months": warranty.get("warranty_duration"),
                            "type": warranty.get("warranty_type", []),
                            "service_centers": warranty.get("service_centers"),
                            "installation": warranty.get("installation", False),
                            "support_score": warranty.get("support_score", 50),
                            "highlights": warranty.get("highlights", [])[:2]
                        },
                        "hidden_costs": {
                            "delivery": hidden_costs.get("delivery_charge"),
                            "installation": hidden_costs.get("installation_fee"),
                            "total_extra": hidden_costs.get("total_hidden_cost", 0),
                            "transparency_score": hidden_costs.get("transparency_score", 100),
                            "warnings": hidden_costs.get("warnings", [])[:3]
                        }
                    })
            except Exception as e:
                print(f"⚠️  {site['name']}: Error analyzing product {idx} - {e}", file=sys.stderr, flush=True)
                continue
                
    except Exception as e:
        print(f"❌ {site['name']}: Site error - {e}", file=sys.stderr, flush=True)
    
    return site_results

def search_and_analyze(product_name, max_products=2):
    """Search across all sites IN PARALLEL and analyze top results - OPTIMIZED FOR SPEED"""
    results = []
    
    # Prioritize fast, reliable sites
    enabled_sites = [s for s in SEARCH_SITES if s.get("enabled", True)]
    priority_sites = ["Amazon.in", "Flipkart", "Vijay Sales"]
    fast_sites = [s for s in enabled_sites if s["name"] in priority_sites][:3]
    
    total_sites = len(fast_sites)
    
    print(f"🔍 Searching {total_sites} sites in parallel for '{product_name}'...", file=sys.stderr, flush=True)
    start_time = time.time()
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Search all sites in parallel using ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=3) as executor:
            # Submit all site searches simultaneously
            future_to_site = {
                executor.submit(search_site, site, product_name, max_products, tmp_dir): site 
                for site in fast_sites
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_site):
                site = future_to_site[future]
                try:
                    site_results = future.result()
                    results.extend(site_results)
                except Exception as e:
                    print(f"❌ {site['name']}: Error - {e}", file=sys.stderr, flush=True)
    
    elapsed = time.time() - start_time
    print(f"✨ Analysis complete in {elapsed:.1f}s! Found {len(results)} products total.", file=sys.stderr, flush=True)
    return results

def extract_price_numeric(price_str):
    """Extract numeric value from price string"""
    if not price_str:
        return None
    match = re.search(r'[\d,]+', price_str)
    if match:
        return float(match.group().replace(",", ""))
    return None

def pick_best_deal(results):
    """Pick the best deal based on price and trustworthiness"""
    if not results:
        return None
    
    scored = []
    prices = []
    
    # First pass: extract all numeric prices
    for r in results:
        price_num = extract_price_numeric(r.get("price"))
        if price_num:
            prices.append(price_num)
    
    if not prices:
        return None
    
    max_price = max(prices)
    
    # Second pass: calculate combined scores
    for r in results:
        price_num = extract_price_numeric(r.get("price"))
        if not price_num:
            continue
        
        scores = r.get("scores", {})
        avg_trust = (
            scores.get("deal_truth", 0) +
            scores.get("review_integrity", 0) +
            scores.get("store_safety", 0)
        ) / 3
        
        # Price score: lower is better (invert)
        price_score = (1 - (price_num / max_price)) * 100 if max_price > 0 else 50
        
        # Combined: 60% trust, 40% price
        combined = (avg_trust * 0.6) + (price_score * 0.4)
        
        scored.append({
            **r,
            "combined_score": round(combined, 2),
            "price_numeric": price_num,
            "avg_trust_score": round(avg_trust, 1)
        })
    
    # Sort by combined score (descending)
    scored.sort(key=lambda x: x["combined_score"], reverse=True)
    return scored[0] if scored else None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--product", required=True, help="Product name to search")
    parser.add_argument("--max-results", type=int, default=3, help="Max products per site")
    args = parser.parse_args()
    
    start_time = time.time()
    results = search_and_analyze(args.product, args.max_results)
    elapsed_time = time.time() - start_time
    
    if not results:
        print(json.dumps({
            "error": "No results found across any sites",
            "results": [],
            "product": args.product,
            "elapsed_time": round(elapsed_time, 1)
        }))
        return
    
    best = pick_best_deal(results)
    
    # Sort results by price
    sorted_results = sorted(
        [r for r in results if extract_price_numeric(r.get("price"))],
        key=lambda x: extract_price_numeric(x.get("price"))
    )
    
    output = {
        "product": args.product,
        "results": sorted_results,
        "best_deal": best,
        "sites_checked": len([s for s in SEARCH_SITES if s.get("enabled", True)]),
        "sites_found": len(set(r["site"] for r in results)),
        "total_products": len(results),
        "elapsed_time": round(elapsed_time, 1),
        "search_status": {
            "total_sites": 3,
            "successful_sites": len(set(r["site"] for r in results)),
            "products_found": len(results),
            "duration_seconds": round(elapsed_time, 1)
        }
    }
    
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
