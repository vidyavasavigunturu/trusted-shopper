---
name: trusted-shopper
description: Comprehensive product analysis across e-commerce sites with review integrity checks, return policy analysis, warranty evaluation, and hidden cost detection. Use when user says "compare", "find best deal", or wants product recommendations. Analyzes trust, returns, warranty, and total cost to find genuinely best value.
---

# Trusted Shopper v2.3 - Complete Intelligence System

## Overview

Advanced product comparison tool that analyzes **4 critical dimensions** to find the best overall value, not just the cheapest price:
1. **Review Integrity** - Fake detection, authenticity scoring
2. **Return Policy** - Flexibility, window, refund vs replacement
3. **Warranty & Support** - Duration, service centers, installation
4. **Hidden Costs** - Delivery, installation, GST, final payable

---

## Trigger Conditions

- **Single URL analysis:** User provides a URL → deep analysis of that product
- **Multi-site comparison:** User says "compare X" or "find best deal for X" → search 8 sites and compare
- **Product recommendation:** "best water heater", "cheapest headphones" → intelligent recommendation

---

## Flow A: Single URL Analysis (Deep Dive)

### 1. Obtain the URL
- Extract from user message or browser extension

### 2. Fetch page content
- Use `web_fetch` for static pages
- Use `browser` tool for dynamic sites
- Save to: `trusted-shopper/tmp/page.html`

### 3. Run comprehensive analyzer

```bash
python3 trusted-shopper/scripts/analyze_from_html.py \
  --url "<URL>" \
  --html_file "trusted-shopper/tmp/page.html"
```

### 4. Parse complete analysis JSON

Returns:
- **Trust Scores:** deal_truth, review_integrity, store_safety (0-100 each)
- **Return Policy:** window_days, type (refund/replacement), method (pickup/dropoff), flexibility_score (0-100)
- **Warranty & Support:** duration_months, type (brand/seller), service_centers, installation, support_score (0-100)
- **Hidden Costs:** delivery_charge, installation_fee, gst_included, total_hidden_cost, transparency_score (0-100)
- **Final Payable:** display_price + hidden_costs

### 5. Format intelligent response

Structure:
```
🏆 Product Analysis: [Name]

💰 Price Breakdown:
- Display Price: ₹X
- Hidden Costs: ₹Y (delivery, install, GST)
- Final Payable: ₹Z

📊 Trust Analysis (73.3/100):
- Review Integrity: 75/100 ✅ (authentic reviews, recent, photos)
- Deal Truth: 70/100 (discount validation)
- Store Safety: 80/100 ✅

🔄 Return Policy (85/100) ✅:
- Window: 10 days
- Type: Refund + Replacement
- Method: Free pickup
- Highlights: [key points]

🔧 Warranty & Support (90/100) 🏆:
- Duration: 2 years (brand warranty)
- Service Centers: Nationwide ✅
- Installation: Free ✅
- Highlights: [key points]

💡 Recommendation: [BUY / AVOID / CONSIDER]
Reasoning: [Why this is good/bad value]
```

---

## Flow B: Multi-Site Comparison (Smart Shopping)

### 1. Extract product query
From: "compare water heaters" → query = "water heaters"

### 2. Run intelligent multi-site search

```bash
python3 trusted-shopper/scripts/compare_across_sites.py \
  --product "<PRODUCT_NAME>"
```

Searches 8 sites:
- Amazon.in
- Flipkart (with Playwright stealth)
- Firstcry, Chumbak, Vijay Sales
- Bajaj Electricals, Clovia, Campus Shoes

### 3. Parse comprehensive comparison data

Returns for each product:
- Price (display + hidden costs)
- Trust scores (3 dimensions)
- Return policy (flexibility scoring)
- Warranty & support (duration, coverage)
- Hidden costs (transparency scoring)

### 4. Generate holistic recommendation

**Scoring Formula:**
```
Value Score = (Price × 25%) 
            + (Trust × 20%)
            + (Delivery × 10%)
            + (Returns × 15%)
            + (Warranty × 15%)
            + (Freebies × 5%)
            + (Offers × 10%)
```

### 5. Format comprehensive comparison

Structure:
```
🏆 BEST OVERALL VALUE: [Product Name] (83.5/100)

📊 Complete Analysis:
- Display Price: ₹28,000
- Hidden Costs: ₹0 (free delivery + install)
- Cashback: -₹2,800
- Freebies: -₹3,500 (soundbar)
- EFFECTIVE PRICE: ₹21,700

✅ Why This is Best:
• Trust Score: 90/100 (official store, authentic reviews)
• Returns: 95/100 (30-day refund, free pickup)
• Warranty: 95/100 (2 years brand + service network)
• Transparency: 100/100 (no hidden costs)
• Delivery: Next day ✅

💰 Price Comparison:
1. Product A: ₹22,500 final (limited support)
2. Product B: ₹22,800 effective (good value)
3. Product C: ₹21,700 effective (BEST) 🏆

💡 Verdict: Worth the ₹8,000 higher sticker price?
YES! Product C is actually ₹800 CHEAPER after benefits
+ infinitely better quality/support!

📋 Detailed Comparison:
[Table with all products, scores, highlights]

⚠️ Products to Avoid:
[Items with poor trust, bad returns, or high hidden costs]
```

---

## Key Analysis Dimensions

### 1. Review Integrity (v2.0)
**Checks:**
- ✅ Recent reviews (1-3 months)
- ✅ Authentic content (defects, packaging, service mentions)
- ✅ User photos / verified purchases
- ❌ Generic 5-star spam ("excellent product", "must buy")
- ❌ Excessive hype ("best ever", "life changing")

**Score Range:** 25-95 (vs old 55-85 generic)

### 2. Return Policy (v2.1)
**Analyzes:**
- Window: 7, 10, 15, 30 days
- Type: Refund vs replacement vs non-returnable
- Method: Free pickup vs paid vs drop-off
- Conditions: Hassle-free vs strict

**Score:** 0-100 flexibility rating

### 3. Warranty & Support (v2.2)
**Evaluates:**
- Duration: 6 months to 10 years
- Type: Brand/manufacturer vs seller
- Service centers: Available vs not mentioned
- Installation: Free vs paid vs none
- Official store: Yes/no

**Score:** 0-100 support rating

### 4. Hidden Costs (v2.3)
**Detects:**
- Delivery charges
- Installation fees
- GST inclusion/exclusion (18% impact!)
- Convenience/platform fees
- COD charges
- Final payable amount

**Score:** 0-100 transparency rating

---

## Supported Sites (8 Total)

### ✅ Fully Working:
- **Amazon.in** - Browser method, excellent data
- **Flipkart** - Browser + stealth, good coverage
- **Firstcry** - Simple fetch, baby/kids products
- **Chumbak** - Simple fetch, lifestyle items
- **Vijay Sales** - Simple fetch, electronics
- **Bajaj Electricals** - Browser method, appliances
- **Clovia** - Browser method, fashion
- **Campus Shoes** - Browser method, footwear

### ⚠️ Not Working (Anti-Bot):
- Myntra (advanced fingerprinting)
- Snapdeal (Cloudflare WAF)

---

## Resources

### Scripts:
- `analyze_from_html.py` - Complete product analysis (trust, returns, warranty, costs)
- `compare_across_sites.py` - Multi-site search with holistic value scoring
- `browser_fetch.py` - Playwright stealth integration for anti-bot sites

### Documentation:
- `REVIEW_INTEGRITY_ENHANCEMENTS.md` - v2.0 fake detection
- `RETURN_POLICY_FEATURE.md` - v2.1 flexibility analysis
- `WARRANTY_SUPPORT_FEATURE.md` - v2.2 coverage evaluation
- `HIDDEN_COSTS_FEATURE.md` - v2.3 transparency scoring
- `HOLISTIC_VALUE_SCORING.md` - Recommendation engine
- `FINAL_SYSTEM_OVERVIEW.md` - Complete v2.3 guide

---

## Example Queries

### Single Product Analysis:
> "Analyze this product: https://www.amazon.in/dp/B0D78XSMSM"
> "Is this a good deal? [URL]"
> "Check if this is trustworthy: [URL]"

### Multi-Site Comparison:
> "Compare water heaters"
> "Find the best deal for wireless earbuds"
> "Show me cheap and good headphones"
> "Best cooler under 5000"

### Smart Shopping:
> "Find cheapest smart TV with good warranty"
> "Water heater with free installation"
> "Headphones with 4+ star reviews"

---

## Output Highlights

**What Makes This Different:**
- ❌ Old: "Product A is ₹20,000, Product B is ₹28,000 → Buy A (cheaper)"
- ✅ New: "Product A is ₹22,500 final (+ hidden costs), Product B is ₹21,700 effective (- cashback - freebies) + better warranty + easy returns → Buy B (better value)"

**Key Principles:**
1. **Effective Price** ≠ Display Price
2. **Quality Has Value** (trust, warranty, returns)
3. **Total Cost of Ownership** matters
4. **Sometimes Higher Price** = Better Value

---

## Version

**Current:** v2.3 (Complete Intelligence System)
**Status:** Production-ready
**Last Updated:** 2026-02-20

**Achievement:** From simple price comparison to comprehensive purchasing intelligence! 🎯🏆

