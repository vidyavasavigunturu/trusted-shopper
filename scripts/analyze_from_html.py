import re
import json
import argparse
from urllib.parse import urlparse

def strip_html(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", " ", html)
    html = re.sub(r"(?s)<.*?>", " ", html)
    html = re.sub(r"\s+", " ", html).strip()
    return html

def extract_title(text: str) -> str:
    # Heuristic: first meaningful chunk
    return text[:140].strip()

def extract_price(text: str):
    patterns = [
        r"(₹\s?\d[\d,]*(?:\.\d{1,2})?)",
        r"(\$\s?\d[\d,]*(?:\.\d{1,2})?)",
        r"(€\s?\d[\d,]*(?:\.\d{1,2})?)",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(1)
    return None

def extract_snippet(text: str, keywords):
    lower = text.lower()
    hits = [lower.find(k) for k in keywords if lower.find(k) != -1]
    if not hits:
        return ""
    idx = min(hits)
    start = max(0, idx - 140)
    end = min(len(text), idx + 260)
    return text[start:end].strip()

def analyze_return_policy(text: str):
    """
    Analyze return policy and extract key details:
    - Return window (7, 10, 15, 30 days, etc.)
    - Type (replacement, refund, exchange)
    - Method (pickup, drop-off, self-return)
    """
    lower = text.lower()
    
    policy = {
        "return_window_days": None,
        "type": [],
        "method": [],
        "flexibility_score": 50,  # Base score out of 100
        "highlights": []
    }
    
    # Extract return window (days)
    day_patterns = [
        r"(\d+)\s*days?\s*(return|replacement|refund|exchange)",
        r"(return|replacement|refund|exchange)\s*within\s*(\d+)\s*days?",
        r"(\d+)[-\s]day\s*(return|replacement|refund)"
    ]
    
    days_found = []
    for pattern in day_patterns:
        matches = re.findall(pattern, lower)
        for match in matches:
            for part in match:
                if part.isdigit():
                    days_found.append(int(part))
    
    if days_found:
        policy["return_window_days"] = max(days_found)  # Take the longest window mentioned
    
    # Return types
    if "refund" in lower or "money back" in lower:
        policy["type"].append("refund")
        policy["flexibility_score"] += 15
        policy["highlights"].append("Full refund available")
    
    if "replacement" in lower or "exchange" in lower:
        policy["type"].append("replacement")
        policy["flexibility_score"] += 10
        policy["highlights"].append("Replacement offered")
    
    if "no return" in lower or "non-returnable" in lower or "final sale" in lower:
        policy["type"] = ["non-returnable"]
        policy["flexibility_score"] = 10
        policy["highlights"].append("⚠️ Non-returnable item")
    
    # Return methods
    if any(k in lower for k in ["free pickup", "free return pickup", "pickup at doorstep"]):
        policy["method"].append("free-pickup")
        policy["flexibility_score"] += 20
        policy["highlights"].append("✅ Free doorstep pickup")
    elif "pickup" in lower:
        policy["method"].append("pickup")
        policy["flexibility_score"] += 10
    
    if any(k in lower for k in ["drop off", "dropoff", "self return", "courier"]):
        policy["method"].append("drop-off")
        if "free" not in lower:
            policy["flexibility_score"] -= 5
    
    # Bonus for generous windows
    if policy["return_window_days"]:
        days = policy["return_window_days"]
        if days >= 30:
            policy["flexibility_score"] += 25
            policy["highlights"].append(f"🏆 {days}-day return window (excellent)")
        elif days >= 15:
            policy["flexibility_score"] += 15
            policy["highlights"].append(f"✅ {days}-day return window (good)")
        elif days >= 10:
            policy["flexibility_score"] += 10
            policy["highlights"].append(f"{days}-day return window")
        elif days >= 7:
            policy["flexibility_score"] += 5
            policy["highlights"].append(f"⚠️ Only {days}-day return window (short)")
        else:
            policy["highlights"].append(f"⚠️ Very short {days}-day return window")
    else:
        policy["highlights"].append("⚠️ Return window not clearly stated")
    
    # Check for conditions
    if any(k in lower for k in ["no questions asked", "hassle free", "easy return"]):
        policy["flexibility_score"] += 10
        policy["highlights"].append("Hassle-free returns")
    
    if any(k in lower for k in ["original packaging", "unopened", "unused", "tags attached"]):
        policy["flexibility_score"] -= 5
        policy["highlights"].append("Conditions apply (packaging/tags required)")
    
    # Clamp score
    policy["flexibility_score"] = max(0, min(100, policy["flexibility_score"]))
    
    return policy

def analyze_warranty_support(text: str):
    """
    Analyze warranty and after-sales support:
    - Warranty duration (6 months, 1 year, 2 years, etc.)
    - Type (brand vs seller warranty)
    - Service center availability
    - Installation support
    """
    lower = text.lower()
    
    support = {
        "warranty_duration": None,
        "warranty_type": [],
        "service_centers": None,
        "installation": False,
        "support_score": 50,  # Base score out of 100
        "highlights": []
    }
    
    # Extract warranty duration
    warranty_patterns = [
        r"(\d+)\s*(year|yr|years|yrs)\s*(warranty|guarantee)",
        r"(\d+)\s*(month|months|mo|mos)\s*(warranty|guarantee)",
        r"(warranty|guarantee)\s*[:\-]?\s*(\d+)\s*(year|yr|month|mo)",
        r"(\d+)[-\s](year|month)\s*(warranty|guarantee)"
    ]
    
    durations_found = []
    for pattern in warranty_patterns:
        matches = re.findall(pattern, lower)
        for match in matches:
            for i, part in enumerate(match):
                if part.isdigit():
                    value = int(part)
                    # Check next part for unit
                    if i + 1 < len(match):
                        unit = match[i + 1]
                        if "year" in unit or "yr" in unit:
                            durations_found.append(value * 12)  # Convert to months
                        elif "month" in unit or "mo" in unit:
                            durations_found.append(value)
                    break
    
    if durations_found:
        max_duration = max(durations_found)
        support["warranty_duration"] = max_duration
        
        # Convert back to readable format
        if max_duration >= 12:
            years = max_duration // 12
            months = max_duration % 12
            if months > 0:
                readable = f"{years} year {months} month"
            else:
                readable = f"{years} year{'s' if years > 1 else ''}"
        else:
            readable = f"{max_duration} month{'s' if max_duration > 1 else ''}"
        
        # Score based on duration
        if max_duration >= 24:  # 2+ years
            support["support_score"] += 30
            support["highlights"].append(f"🏆 {readable} warranty (excellent)")
        elif max_duration >= 12:  # 1 year
            support["support_score"] += 20
            support["highlights"].append(f"✅ {readable} warranty (good)")
        elif max_duration >= 6:  # 6 months
            support["support_score"] += 10
            support["highlights"].append(f"{readable} warranty")
        else:
            support["support_score"] += 5
            support["highlights"].append(f"⚠️ Only {readable} warranty (short)")
    else:
        support["highlights"].append("⚠️ Warranty duration not clearly stated")
    
    # Warranty type
    if any(k in lower for k in ["brand warranty", "manufacturer warranty", "company warranty", "official warranty"]):
        support["warranty_type"].append("brand")
        support["support_score"] += 15
        support["highlights"].append("✅ Brand/Manufacturer warranty")
    
    if any(k in lower for k in ["seller warranty", "platform warranty", "amazon fulfilled", "flipkart assured"]):
        support["warranty_type"].append("seller")
        support["support_score"] += 8
        support["highlights"].append("Seller warranty included")
    
    if not support["warranty_type"]:
        support["warranty_type"].append("unknown")
        support["support_score"] -= 5
    
    # Service centers
    service_keywords = [
        "service center", "service centre", "authorized service", 
        "repair center", "customer service center", "after sales service",
        "service network", "nationwide service", "pan india service"
    ]
    
    if any(k in lower for k in service_keywords):
        support["service_centers"] = "available"
        support["support_score"] += 15
        support["highlights"].append("✅ Authorized service centers available")
        
        # Bonus for nationwide coverage
        if any(k in lower for k in ["nationwide", "pan india", "all cities", "across india"]):
            support["support_score"] += 5
            support["highlights"].append("Nationwide service network")
    else:
        support["service_centers"] = "not mentioned"
        support["highlights"].append("⚠️ Service center availability not mentioned")
    
    # Installation support
    installation_keywords = [
        "free installation", "installation service", "installation support",
        "installation included", "demo", "setup", "on-site installation"
    ]
    
    if any(k in lower for k in installation_keywords):
        support["installation"] = True
        support["support_score"] += 10
        support["highlights"].append("✅ Installation support available")
    
    # Official brand store bonus
    if any(k in lower for k in ["official store", "brand store", "authorized seller", "authorized dealer"]):
        support["support_score"] += 15
        support["highlights"].append("🏆 Official brand store/Authorized seller")
    
    # Extended warranty available
    if any(k in lower for k in ["extended warranty", "additional warranty", "warranty extension"]):
        support["support_score"] += 5
        support["highlights"].append("Extended warranty available")
    
    # Clamp score
    support["support_score"] = max(0, min(100, support["support_score"]))
    
    return support

def analyze_hidden_costs(text: str, base_price_str: str):
    """
    Detect hidden costs that increase final payable amount:
    - Delivery/shipping charges
    - Installation fees
    - Convenience/platform fees
    - GST inclusion/exclusion
    - Packaging charges
    """
    lower = text.lower()
    
    costs = {
        "delivery_charge": None,
        "installation_fee": None,
        "convenience_fee": None,
        "gst_included": None,
        "other_fees": [],
        "total_hidden_cost": 0,
        "transparency_score": 100,  # Start at perfect, deduct for hidden costs
        "warnings": []
    }
    
    # Extract base price numeric value for calculations
    base_price = 0
    if base_price_str:
        match = re.search(r'[\d,]+', base_price_str)
        if match:
            base_price = float(match.group().replace(",", ""))
    
    # Delivery charges
    delivery_patterns = [
        r"delivery\s*(?:charge|fee|cost)[:\s]*₹?\s*([\d,]+)",
        r"shipping\s*(?:charge|fee|cost)[:\s]*₹?\s*([\d,]+)",
        r"₹\s*([\d,]+)\s*(?:delivery|shipping)"
    ]
    
    if any(k in lower for k in ["free delivery", "free shipping", "no delivery charge"]):
        costs["delivery_charge"] = 0
        costs["warnings"].append("✅ Free delivery")
    else:
        for pattern in delivery_patterns:
            match = re.search(pattern, lower)
            if match:
                charge = float(match.group(1).replace(",", ""))
                costs["delivery_charge"] = charge
                costs["total_hidden_cost"] += charge
                costs["transparency_score"] -= 10
                costs["warnings"].append(f"⚠️ Delivery charge: ₹{charge:.0f}")
                break
        
        # If no specific charge found but delivery mentioned without "free"
        if costs["delivery_charge"] is None and any(k in lower for k in ["delivery", "shipping"]):
            costs["warnings"].append("⚠️ Delivery charges may apply (not clearly stated)")
            costs["transparency_score"] -= 5
    
    # Installation fees
    installation_patterns = [
        r"installation\s*(?:charge|fee|cost)[:\s]*₹?\s*([\d,]+)",
        r"₹\s*([\d,]+)\s*installation"
    ]
    
    if any(k in lower for k in ["free installation", "installation included", "no installation charge"]):
        costs["installation_fee"] = 0
        costs["warnings"].append("✅ Free installation")
    else:
        for pattern in installation_patterns:
            match = re.search(pattern, lower)
            if match:
                fee = float(match.group(1).replace(",", ""))
                costs["installation_fee"] = fee
                costs["total_hidden_cost"] += fee
                costs["transparency_score"] -= 15
                costs["warnings"].append(f"⚠️ Installation fee: ₹{fee:.0f}")
                break
    
    # Convenience/Platform fees
    convenience_patterns = [
        r"convenience\s*fee[:\s]*₹?\s*([\d,]+)",
        r"platform\s*fee[:\s]*₹?\s*([\d,]+)",
        r"service\s*fee[:\s]*₹?\s*([\d,]+)",
        r"handling\s*(?:charge|fee)[:\s]*₹?\s*([\d,]+)"
    ]
    
    for pattern in convenience_patterns:
        match = re.search(pattern, lower)
        if match:
            fee = float(match.group(1).replace(",", ""))
            costs["convenience_fee"] = fee
            costs["total_hidden_cost"] += fee
            costs["transparency_score"] -= 10
            costs["warnings"].append(f"⚠️ Convenience/platform fee: ₹{fee:.0f}")
            break
    
    # GST inclusion
    if any(k in lower for k in ["inclusive of all taxes", "inclusive of gst", "including tax", "tax included"]):
        costs["gst_included"] = True
        costs["warnings"].append("✅ GST included in price")
    elif any(k in lower for k in ["exclusive of tax", "excluding gst", "plus gst", "+ gst", "taxes extra"]):
        costs["gst_included"] = False
        costs["transparency_score"] -= 20
        # Estimate 18% GST if base price available
        if base_price > 0:
            gst_amount = base_price * 0.18
            costs["total_hidden_cost"] += gst_amount
            costs["warnings"].append(f"⚠️ GST extra: ~₹{gst_amount:.0f} (18% of base price)")
        else:
            costs["warnings"].append("⚠️ GST not included (typically 18% extra)")
    
    # Packaging charges
    packaging_patterns = [
        r"packaging\s*(?:charge|fee)[:\s]*₹?\s*([\d,]+)"
    ]
    
    for pattern in packaging_patterns:
        match = re.search(pattern, lower)
        if match:
            fee = float(match.group(1).replace(",", ""))
            costs["other_fees"].append(("packaging", fee))
            costs["total_hidden_cost"] += fee
            costs["transparency_score"] -= 5
            costs["warnings"].append(f"⚠️ Packaging charge: ₹{fee:.0f}")
    
    # COD charges
    if any(k in lower for k in ["cod charge", "cash on delivery charge", "cod fee"]):
        cod_pattern = r"cod\s*(?:charge|fee)[:\s]*₹?\s*([\d,]+)"
        match = re.search(cod_pattern, lower)
        if match:
            fee = float(match.group(1).replace(",", ""))
            costs["other_fees"].append(("cod", fee))
            costs["transparency_score"] -= 5
            costs["warnings"].append(f"⚠️ COD charge: ₹{fee:.0f} (choose prepaid to save)")
        else:
            costs["warnings"].append("⚠️ COD charges may apply")
            costs["transparency_score"] -= 3
    
    # Calculate final payable amount if base price available
    if base_price > 0 and costs["total_hidden_cost"] > 0:
        final_amount = base_price + costs["total_hidden_cost"]
        hidden_percentage = (costs["total_hidden_cost"] / base_price) * 100
        
        costs["warnings"].append(f"💰 Total hidden costs: ₹{costs['total_hidden_cost']:.0f} ({hidden_percentage:.1f}% extra)")
        costs["warnings"].append(f"💳 Final payable: ₹{final_amount:.0f}")
        
        # Extra penalty for high hidden costs
        if hidden_percentage > 20:
            costs["transparency_score"] -= 20
            costs["warnings"].append("🚨 HIGH hidden costs (>20% of base price)")
        elif hidden_percentage > 10:
            costs["transparency_score"] -= 10
            costs["warnings"].append("⚠️ Significant hidden costs (>10% of base price)")
    
    # Clamp score
    costs["transparency_score"] = max(0, min(100, costs["transparency_score"]))
    
    return costs

def score(signals):
    # Simple, hackathon-friendly scoring. Improve iteratively.
    deal = 70
    review = 70
    safety = 80
    reasons = {"deal": [], "review": [], "safety": []}

    text = signals["text"].lower()
    domain = signals["domain"]
    price = signals["price"]

    # Deal Truth
    if price is None:
        deal -= 15
        reasons["deal"].append("No clear price found on page (lower confidence).")
    
    if any(k in text for k in ["% off", "discount", "sale"]):
        if not any(k in text for k in ["mrp", "list price", "was", "previous price"]):
            deal -= 10
            reasons["deal"].append("Discount claim seen but no clear reference price detected.")
        else:
            reasons["deal"].append("Discount/reference pricing signals present.")
    else:
        reasons["deal"].append("No strong discount language detected.")

    # Review Integrity (Enhanced)
    review_points = 0
    review_signals = []
    
    # Basic check: Are reviews present?
    if not any(k in text for k in ["review", "rating", "stars"]):
        review -= 15
        reasons["review"].append("No obvious review/rating section detected.")
    else:
        review_signals.append("Review section detected")
    
    # Check 1: Recent reviews (last 1-3 months)
    recent_months = ["january", "february", "march", "april", "may", "june", 
                     "july", "august", "september", "october", "november", "december",
                     "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec",
                     "ago", "days ago", "weeks ago", "month ago", "months ago"]
    
    if any(month in text for month in recent_months):
        review_points += 5
        review_signals.append("Recent review timestamps detected")
    else:
        review -= 5
        reasons["review"].append("No recent review dates found (prefer reviews from last 1-3 months).")
    
    # Check 2: Defects, packaging, service mentions (authentic review signals)
    authentic_keywords = ["defect", "damage", "broken", "packaging", "delivery", "service", 
                         "customer care", "return", "refund", "issue", "problem", "complaint",
                         "shipped", "arrived", "received", "quality", "build quality"]
    
    authentic_hits = sum(1 for k in authentic_keywords if k in text)
    if authentic_hits >= 3:
        review_points += 10
        review_signals.append(f"Authentic review signals detected ({authentic_hits} mentions of defects/packaging/service)")
    elif authentic_hits >= 1:
        review_points += 5
        review_signals.append("Some authentic review content detected")
    else:
        review -= 5
        reasons["review"].append("Lack of detailed review content (defects, packaging, service mentions).")
    
    # Check 3: User photos in reviews
    photo_keywords = ["verified purchase", "customer image", "customer photo", "uploaded", 
                     "image from", "photo from", "review photo", "review image"]
    
    if any(k in text for k in photo_keywords):
        review_points += 10
        review_signals.append("User-uploaded photos/verified purchases detected (high authenticity)")
    else:
        review -= 5
        reasons["review"].append("No evidence of user-uploaded photos in reviews.")
    
    # Check 4: Generic 5-star review filter
    generic_praise = ["excellent product", "great product", "amazing product", "superb product",
                     "highly recommend", "worth buying", "must buy", "very good", "fantastic"]
    
    generic_hits = sum(1 for g in generic_praise if g in text)
    if generic_hits >= 4:
        review -= 10
        reasons["review"].append(f"Overly generic 5-star reviews detected ({generic_hits} generic praise phrases).")
    
    # Check 5: Excessive hype patterns
    hype = ["best ever", "100% recommended", "life changing", "miracle product", 
            "perfect in every way", "flawless", "zero complaints"]
    hype_hits = sum(1 for h in hype if h in text)
    if hype_hits >= 2:
        review -= 10
        reasons["review"].append("Overly promotional language patterns detected in page text.")
    
    # Apply bonus points and add positive signals to reasons
    review += review_points
    if review_signals:
        reasons["review"].extend(review_signals[:2])  # Add top 2 positive signals
    
    if not reasons["review"]:
        reasons["review"].append("Basic review integrity checks passed.")

    # Store/Seller Safety
    urgency = ["limited time", "act now", "only today", "hurry", "last chance"]
    urgency_hits = sum(1 for u in urgency if u in text)
    if urgency_hits >= 3:
        safety -= 10
        reasons["safety"].append("Heavy urgency messaging detected (common in risky storefronts).")
    else:
        reasons["safety"].append("No heavy urgency pattern detected in sampled text.")
    
    if domain.endswith((".xyz", ".top", ".click")):
        safety -= 10
        reasons["safety"].append(f"Domain ends with a higher-risk TLD pattern: {domain}")

    # Clamp + shorten reasons
    deal = max(0, min(100, deal))
    review = max(0, min(100, review))
    safety = max(0, min(100, safety))

    # Ensure at least 2 reasons each
    for k in ["deal", "review", "safety"]:
        if len(reasons[k]) < 2:
            reasons[k].append("Heuristic assessment; recommend verifying key details manually.")

    return {
        "scores": {
            "deal_truth": deal,
            "review_integrity": review,
            "store_safety": safety
        },
        "reasons": reasons
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", required=True)
    ap.add_argument("--html_file", required=True)
    args = ap.parse_args()

    with open(args.html_file, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    text = strip_html(html)
    domain = urlparse(args.url).netloc
    title = extract_title(text)
    price = extract_price(text)
    return_policy = extract_snippet(text, ["return", "refund", "replacement", "warranty", "cancel"])
    review_snip = extract_snippet(text, ["review", "rating", "stars"])
    
    # Analyze return policy
    return_analysis = analyze_return_policy(text)
    
    # Analyze warranty & support
    warranty_analysis = analyze_warranty_support(text)
    
    # Analyze hidden costs
    hidden_costs = analyze_hidden_costs(text, price)

    signals = {
        "url": args.url,
        "domain": domain,
        "title": title,
        "price": price,
        "return_policy_snippet": return_policy,
        "review_snippet": review_snip,
        "text": text[:4000]  # keep bounded for speed
    }

    scored = score(signals)

    out = {
        "url": args.url,
        "domain": domain,
        "title_guess": title,
        "price_guess": price,
        "snippets": {
            "return_policy": return_policy,
            "reviews": review_snip
        },
        "return_policy_analysis": return_analysis,
        "warranty_support_analysis": warranty_analysis,
        "hidden_costs_analysis": hidden_costs,
        **scored,
        "evidence_sample": text[:600]
    }

    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
