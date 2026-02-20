# 🧪 Trusted Shopper - Test Case Prompts

## Overview
Comprehensive test cases covering all features: single URL analysis, multi-site comparison, review integrity, return policy, warranty support, and multi-category searches.

---

## 📋 Test Categories

### **1. Single URL Analysis**
### **2. Multi-Site Product Comparison**
### **3. Review Integrity Testing**
### **4. Return Policy Analysis**
### **5. Warranty & Support Analysis**
### **6. Category-Specific Searches**
### **7. Edge Cases & Error Handling**

---

## 1️⃣ Single URL Analysis Test Cases

### **TC-101: Basic Amazon Product Analysis**
```
Analyze this product: https://www.amazon.in/dp/B0D78XSMSM
```
**Expected Output:**
- Deal Truth Score (0-100)
- Review Integrity Score (25-95)
- Store Safety Score (0-100)
- Return Policy Analysis (window, type, method, flexibility 0-100)
- Warranty & Support Analysis (duration, type, service centers, support 0-100)
- Evidence snippets with reasons
- Suggested actions

---

### **TC-102: Product with Fake Reviews**
```
Check this deal: https://www.amazon.in/dp/B09XXXXXX (use any product with suspicious reviews)
```
**Expected Output:**
- Lower Review Integrity Score (25-55 range)
- Reasons highlighting:
  - Generic 5-star spam detected
  - Excessive hype language
  - Lack of recent reviews
  - No user photos
  - Templated content

---

### **TC-103: Product with Excellent Return Policy**
```
Analyze: https://www.amazon.in/dp/B0CXXXXXX (product with 30-day return)
```
**Expected Output:**
- Return Policy Flexibility: 70-95
- 30-day return window
- Refund available (not just replacement)
- Free pickup mentioned
- Reasons explaining policy benefits

---

### **TC-104: Product with Poor Warranty**
```
Check this: https://www.amazon.in/dp/B0DXXXXXX (product with 6-month seller warranty)
```
**Expected Output:**
- Warranty & Support Score: 30-50
- Only 6 months warranty
- Seller warranty (not brand)
- No service center info
- Warning about limited support

---

### **TC-105: Premium Product with Full Support**
```
Analyze this TV: https://www.amazon.in/dp/B0EXXXXXX (official brand store with 2-year warranty)
```
**Expected Output:**
- Warranty & Support Score: 80-95
- 2 years brand warranty
- Official brand store detected
- Service centers mentioned
- Installation support available
- High support score reasons

---

## 2️⃣ Multi-Site Product Comparison

### **TC-201: Electronics Comparison**
```
Compare Samsung Galaxy Book4 across sites
```
**Expected Output:**
- Search results from 4+ sites (Amazon, Vijay Sales, Firstcry if applicable, Chumbak)
- Price comparison table (sorted low to high)
- Trust scores for each listing
- Return policy comparison
- Warranty comparison
- Best deal recommendation with reasoning
- Warnings about poor deals

---

### **TC-202: General Product Search**
```
Find the best deal for laptop
```
**Expected Output:**
- Multiple products from Amazon, Vijay Sales, eBay (if working)
- Price range: ₹20,000 - ₹80,000+
- Comparison table with scores
- Best value recommendation (not just cheapest)
- Consider warranty + returns in recommendation

---

### **TC-203: Baby Products**
```
Compare baby toys across sites
```
**Expected Output:**
- Results from Amazon, Firstcry (relevant!)
- Possibly Chumbak (lifestyle items)
- Vijay Sales excluded (not their category)
- Category-appropriate recommendations

---

### **TC-204: Lifestyle Products**
```
Find best deal for home decor
```
**Expected Output:**
- Chumbak results (specialty store)
- Amazon results
- Comparison highlighting Chumbak's niche offerings
- Price vs specialty store value discussion

---

### **TC-205: Mobile Phones**
```
Compare iPhone 15 prices
```
**Expected Output:**
- Amazon, Vijay Sales, Poorvika (if working)
- Wide price range
- Focus on:
  - Official vs reseller
  - Warranty coverage (Apple vs seller)
  - Return policy differences
  - Price differences explained

---

### **TC-206: Large Appliances**
```
Find best deal for smart TV 43 inch
```
**Expected Output:**
- Multiple options from electronics stores
- Installation support comparison
- Warranty comparison critical (1 year vs 2 years)
- Service center availability
- Free installation value calculation
- Clear recommendation with total cost of ownership

---

## 3️⃣ Review Integrity Testing

### **TC-301: Recent Reviews Check**
```
Analyze product reviews: https://www.amazon.in/dp/B0D78XSMSM
Focus on review authenticity.
```
**Expected Output:**
- Recent review percentage (1-3 months)
- Authentic content detection (defects, packaging mentioned)
- User photo count
- Generic spam detection
- Review Integrity Score with detailed breakdown

---

### **TC-302: Fake Review Detection**
```
Check if this product has fake reviews: [URL with suspicious reviews]
```
**Expected Output:**
- Red flags identified:
  - Too many 5-star generic reviews
  - Excessive hype ("amazing", "excellent", "must buy")
  - No specific product details
  - All reviews too similar
  - No user photos
- Low Review Integrity Score (25-45)
- Warning to user

---

### **TC-303: Authentic Reviews Detection**
```
Analyze: [URL with genuine detailed reviews]
```
**Expected Output:**
- High Review Integrity Score (75-90)
- Reasons:
  - Recent reviews present
  - Detailed defect mentions
  - User photos included
  - Specific product details
  - Balanced (not all 5-star)

---

## 4️⃣ Return Policy Analysis

### **TC-401: 30-Day Refund Policy**
```
Check return policy: [product with 30-day full refund]
```
**Expected Output:**
- Return Flexibility: 85-95
- 30-day window detected
- Full refund available
- Free pickup mentioned
- High flexibility reasoning

---

### **TC-402: 7-Day Replacement Only**
```
Analyze returns: [product with 7-day replacement only]
```
**Expected Output:**
- Return Flexibility: 30-45
- Only 7 days
- Replacement only (no refund)
- Drop-off required (no pickup)
- Warning about limited flexibility

---

### **TC-403: Non-Returnable Product**
```
Check: [non-returnable item like innerwear]
```
**Expected Output:**
- Return Flexibility: 0-15
- Non-returnable detected
- Clear warning
- Reason (hygiene, category policy)

---

### **TC-404: Return Policy Comparison**
```
Compare return policies for: laptop
```
**Expected Output:**
- Table showing return windows (7, 10, 30 days)
- Refund vs replacement comparison
- Pickup vs drop-off comparison
- Best return policy highlighted
- Impact on purchasing decision

---

## 5️⃣ Warranty & Support Analysis

### **TC-501: Brand Warranty vs Seller Warranty**
```
Analyze warranty: [product with 2-year brand warranty]
vs
[product with 6-month seller warranty]
```
**Expected Output:**
- Support scores: 85 vs 35
- Brand warranty advantages explained
- Service center availability
- Warranty claim ease
- Clear recommendation

---

### **TC-502: Installation Support Detection**
```
Check support for: smart TV [with free installation]
```
**Expected Output:**
- Free installation detected
- Value calculated (₹1,500-2,000)
- Support score boosted (+15-20 points)
- Total cost comparison adjusted

---

### **TC-503: Service Center Availability**
```
Analyze warranty support: [product mentioning service centers]
```
**Expected Output:**
- Service center detection
- Nationwide vs limited availability
- Support score impact (+10-15 points)
- Repair ease assessment

---

### **TC-504: Official Brand Store**
```
Check: [product from official brand store]
```
**Expected Output:**
- Official store detected
- Genuine product guarantee
- Better warranty terms
- Support score boost
- Recommendation weight increased

---

## 6️⃣ Category-Specific Searches

### **TC-601: Fashion/Apparel**
```
Find best deal for men's t-shirt
```
**Expected Output:**
- Bewakoof.com (if working)
- Amazon
- Focus on return policies (important for clothing)
- Size exchange options

---

### **TC-602: Electronics - Mobile Accessories**
```
Compare wireless earbuds
```
**Expected Output:**
- Amazon, Vijay Sales, Poorvika
- Warranty critical (electronics)
- Brand vs generic comparison

---

### **TC-603: Baby Products**
```
Find baby stroller deals
```
**Expected Output:**
- Firstcry.com (specialty store)
- Amazon
- Safety certifications mentioned
- Return policy important for baby items

---

### **TC-604: Home Decor**
```
Compare wall art prices
```
**Expected Output:**
- Chumbak (specialty)
- Amazon
- Unique designs vs mass market
- Price vs quality discussion

---

### **TC-605: Large Appliances**
```
Find washing machine deals
```
**Expected Output:**
- Amazon, Vijay Sales, Croma (if working)
- Installation support critical
- Warranty comparison (2yr vs 5yr)
- Service network availability
- Total cost calculation

---

## 7️⃣ Edge Cases & Error Handling

### **TC-701: Invalid URL**
```
Analyze: https://invalid-site.com/product
```
**Expected Output:**
- Error message: "Unable to fetch product page"
- Suggested action: Check URL or try another product

---

### **TC-702: Blocked Site (Flipkart without extension)**
```
Analyze: https://www.flipkart.com/product/xyz
```
**Expected Output:**
- Warning: "Flipkart requires browser extension"
- Alternative: "Search product name for multi-site comparison"

---

### **TC-703: Product Not Found**
```
Compare: extremely_rare_product_xyz123
```
**Expected Output:**
- Message: "No products found for 'extremely_rare_product_xyz123'"
- Suggestions: "Try broader search terms"

---

### **TC-704: Ambiguous Product Name**
```
Find deals for "phone"
```
**Expected Output:**
- Results from multiple brands/models
- Price range very wide
- Suggestion: "Be more specific (e.g., 'iPhone 15' or 'Samsung Galaxy S24')"

---

### **TC-705: Mixed Category Search**
```
Compare laptop vs tablet
```
**Expected Output:**
- Separate results for each category
- Category-appropriate comparisons
- Clear separation in output

---

### **TC-706: No HTML Content**
```
Analyze: [page that loads via heavy JavaScript]
```
**Expected Output:**
- Fallback to browser tool
- Message: "Using browser to load dynamic page..."
- Analysis proceeds normally

---

### **TC-707: Partial Data**
```
Analyze: [product with missing return policy info]
```
**Expected Output:**
- Available scores shown
- Missing data noted: "Return policy not found on page"
- Recommendation adjusted accordingly

---

### **TC-708: Price Scraping Failure**
```
Compare: [product where price is hidden/dynamic]
```
**Expected Output:**
- Note: "Price not available on page"
- Other scores still provided
- Suggestion: "Check site directly for price"

---

## 🎯 Expected Output Format (All Tests)

### **Minimum Components:**
1. **Verdict** (1-2 lines summary)
2. **Trustworthiness Scores:**
   - Deal Truth (0-100) + reasons
   - Review Integrity (25-95) + reasons
   - Store Safety (0-100) + reasons
3. **Return Policy Analysis:**
   - Window, Type, Method
   - Flexibility Score (0-100)
   - Reasoning
4. **Warranty & Support Analysis:**
   - Duration, Type, Service Centers
   - Support Score (0-100)
   - Reasoning
5. **Evidence Snippets** (where applicable)
6. **Suggested Actions**
7. **Clear Recommendation**

---

## 🔧 How to Run Tests

### **Single URL Test:**
```bash
# In chat with the agent:
"Analyze this product: https://www.amazon.in/dp/B0D78XSMSM"

# Direct script execution:
python3 trusted-shopper/scripts/analyze_from_html.py \
  --url "https://www.amazon.in/dp/B0D78XSMSM" \
  --html_file "trusted-shopper/tmp/page.html"
```

### **Multi-Site Comparison Test:**
```bash
# In chat:
"Compare Samsung Galaxy Book4 across sites"

# Direct script:
python3 trusted-shopper/scripts/compare_across_sites.py \
  --product "Samsung Galaxy Book4"
```

---

## 📊 Success Criteria

### **Single URL Analysis:**
- ✅ All 5 scores calculated (deal, reviews, safety, returns, warranty)
- ✅ Reasons provided for each score
- ✅ Evidence snippets extracted
- ✅ Clear recommendation given
- ✅ Execution time < 30 seconds

### **Multi-Site Comparison:**
- ✅ At least 3 sites searched
- ✅ Price comparison table shown
- ✅ All scores calculated for each product
- ✅ Return policy comparison shown
- ✅ Warranty comparison shown
- ✅ Best deal identified with reasoning
- ✅ Warnings about poor deals
- ✅ Execution time < 60 seconds

---

## 🚀 Priority Test Order

### **Phase 1: Core Functionality**
1. TC-101 (Basic Amazon analysis)
2. TC-201 (Electronics comparison)
3. TC-206 (TV with warranty + returns)

### **Phase 2: Feature Testing**
4. TC-301 (Review integrity)
5. TC-401 (Return policy)
6. TC-501 (Warranty comparison)

### **Phase 3: Edge Cases**
7. TC-701 (Invalid URL)
8. TC-702 (Blocked site)
9. TC-707 (Partial data)

### **Phase 4: Category Coverage**
10. TC-203 (Baby products)
11. TC-204 (Lifestyle)
12. TC-605 (Large appliances)

---

## 📝 Test Documentation Template

For each test, document:

```markdown
### Test Case: [TC-XXX]

**Input:** [exact prompt]

**Expected Output:**
- [key components]

**Actual Output:**
- [paste results]

**Status:** ✅ Pass / ⚠️ Partial / ❌ Fail

**Notes:**
- [any observations]
- [edge cases discovered]
- [improvements needed]
```

---

## 💡 Quick Copy-Paste Prompts

### **Starter Pack (5 tests):**
```
1. Analyze this product: https://www.amazon.in/dp/B0D78XSMSM

2. Compare Samsung Galaxy Book4 across sites

3. Find the best deal for smart TV 43 inch

4. Compare baby toys across sites

5. Find best deal for wireless earbuds
```

### **Advanced Pack (5 tests):**
```
6. Check if this product has fake reviews: [suspicious URL]

7. Compare return policies for: laptop

8. Analyze warranty support: [TV with service centers]

9. Find washing machine deals (focus on installation)

10. Compare: extremely_rare_product_xyz123 (test error handling)
```

---

## 🎯 Performance Benchmarks

| Test Type | Expected Time | Max Time |
|-----------|---------------|----------|
| Single URL Analysis | 5-15s | 30s |
| Multi-Site Comparison (3 sites) | 20-40s | 60s |
| Multi-Site Comparison (5+ sites) | 40-60s | 90s |
| Error Handling | <5s | 10s |

---

## ✅ Checklist

Before marking skill as production-ready:

- [ ] All Phase 1 tests passing
- [ ] All Phase 2 tests passing
- [ ] At least 70% Phase 3 tests passing
- [ ] Category-specific tests (4/6 passing)
- [ ] No crashes on invalid input
- [ ] Clear error messages
- [ ] Performance within benchmarks
- [ ] Documentation complete
- [ ] User-friendly output format

---

**Version:** 1.0  
**Date:** 2026-02-01  
**Status:** Ready for Testing  
**Coverage:** 40+ test cases across 7 categories  

**Usage:** Copy any prompt from above and paste into OpenClaw chat to test the Trusted Shopper skill! 🧪🛍️
