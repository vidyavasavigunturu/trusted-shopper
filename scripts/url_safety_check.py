#!/usr/bin/env python3
"""
URL Safety Checker for Trusted Shopper
Validates URLs before analysis to detect potential scams
"""

import re
from urllib.parse import urlparse

# Known e-commerce domains (trusted)
TRUSTED_DOMAINS = [
    "amazon.in", "amazon.com",
    "flipkart.com",
    "snapdeal.com",
    "myntra.com",
    "ebay.in", "ebay.com",
    "firstcry.com",
    "chumbak.com",
    "vijaysales.com",
    "bajajelectricals.com",
    "clovia.com",
    "campusshoes.com",
    "croma.com",
    "reliancedigital.in",
    "tatacliq.com",
    "shopclues.com"
]

# Suspicious TLDs commonly used for scams
SUSPICIOUS_TLDS = [
    ".xyz", ".tk", ".ml", ".ga", ".cf", ".gq",
    ".top", ".click", ".link", ".work", ".date",
    ".download", ".stream", ".trade", ".win"
]

def check_url_safety(url):
    """
    Check if a URL is potentially a scam
    Returns: (is_safe: bool, risk_level: str, warnings: list)
    """
    warnings = []
    risk_level = "low"  # low, medium, high
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        scheme = parsed.scheme.lower()
        
        # Check 1: Must be HTTP/HTTPS
        if scheme not in ['http', 'https']:
            warnings.append(f"⚠️ Suspicious protocol: {scheme} (expected http/https)")
            risk_level = "high"
        
        # Check 2: Prefer HTTPS for e-commerce
        if scheme == 'http' and domain not in ['localhost', '127.0.0.1']:
            warnings.append("⚠️ Non-secure connection (HTTP instead of HTTPS)")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 3: IP address instead of domain (suspicious)
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$'
        if re.match(ip_pattern, domain.split(':')[0]):
            warnings.append(f"🚨 IP address used instead of domain: {domain}")
            risk_level = "high"
        
        # Check 4: Known trusted domain (pass immediately)
        base_domain = '.'.join(domain.split('.')[-2:]) if '.' in domain else domain
        if base_domain in TRUSTED_DOMAINS or domain in TRUSTED_DOMAINS:
            return (True, "low", ["✅ Trusted e-commerce domain"])
        
        # Check 5: Suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                warnings.append(f"🚨 Suspicious domain extension: {tld}")
                risk_level = "high"
                break
        
        # Check 6: Too many subdomains (e.g., shop.deals.amazon-india.xyz)
        subdomain_count = domain.count('.')
        if subdomain_count > 3:
            warnings.append(f"⚠️ Unusual domain structure ({subdomain_count} dots)")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 7: Domain contains "amazon", "flipkart" etc but isn't the real site
        for trusted in ['amazon', 'flipkart', 'myntra', 'snapdeal']:
            if trusted in domain.lower() and base_domain not in TRUSTED_DOMAINS:
                warnings.append(f"🚨 Impersonating {trusted}: {domain} (not official site)")
                risk_level = "high"
                break
        
        # Check 8: Very short or very long domains (suspicious)
        if len(base_domain) < 4:
            warnings.append(f"⚠️ Unusually short domain: {base_domain}")
            if risk_level == "low":
                risk_level = "medium"
        elif len(domain) > 50:
            warnings.append(f"⚠️ Unusually long domain: {len(domain)} characters")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 9: Domain has numbers (often used in phishing)
        if re.search(r'\d{3,}', domain):  # 3+ consecutive digits
            warnings.append(f"⚠️ Domain contains number sequence: {domain}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Check 10: Multiple dashes (suspicious pattern)
        if domain.count('-') >= 3:
            warnings.append(f"⚠️ Multiple dashes in domain: {domain}")
            if risk_level == "low":
                risk_level = "medium"
        
        # Determine if safe based on risk level
        is_safe = risk_level == "low" or (risk_level == "medium" and len(warnings) <= 2)
        
        if not warnings:
            warnings = ["⚠️ Unknown domain - proceed with caution"]
            risk_level = "medium"
        
        return (is_safe, risk_level, warnings)
        
    except Exception as e:
        return (False, "high", [f"🚨 Invalid URL format: {e}"])

def format_safety_report(url, is_safe, risk_level, warnings):
    """Format a user-friendly safety report"""
    
    if is_safe and risk_level == "low":
        return f"✅ URL appears safe: {url}\n" + "\n".join(warnings)
    
    risk_emoji = {
        "low": "⚠️",
        "medium": "⚠️",
        "high": "🚨"
    }
    
    risk_label = {
        "low": "Low Risk",
        "medium": "⚠️ MEDIUM RISK",
        "high": "🚨 HIGH RISK - LIKELY SCAM"
    }
    
    report = f"{risk_emoji.get(risk_level, '⚠️')} {risk_label.get(risk_level, 'Unknown Risk')}\n"
    report += f"URL: {url}\n\n"
    report += "Issues detected:\n"
    report += "\n".join(warnings)
    
    if risk_level == "high":
        report += "\n\n🛑 RECOMMENDATION: Do NOT proceed with this URL."
        report += "\n💡 Stick to known e-commerce sites like Amazon.in, Flipkart.com, etc."
    elif risk_level == "medium":
        report += "\n\n⚠️ RECOMMENDATION: Proceed with caution. Verify this is the correct website."
    
    return report

if __name__ == "__main__":
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python3 url_safety_check.py <url>")
        sys.exit(1)
    
    url = sys.argv[1]
    is_safe, risk_level, warnings = check_url_safety(url)
    
    # JSON output for script integration
    result = {
        "url": url,
        "is_safe": is_safe,
        "risk_level": risk_level,
        "warnings": warnings,
        "report": format_safety_report(url, is_safe, risk_level, warnings)
    }
    
    print(json.dumps(result, indent=2))
