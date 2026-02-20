# Return Policy Analysis Feature

## 🎯 Overview

Enhanced the Trusted Shopper skill to analyze and compare return policies across products, helping users understand the **real value** beyond just price and reviews.

---

## ✅ What's Analyzed

### **1. Return Window (Days)**
- Extracts: 7, 10, 15, 30+ days
- Scoring:
  - 30+ days: +25 points (🏆 excellent)
  - 15-29 days: +15 points (✅ good)
  - 10-14 days: +10 points
  - 7-9 days: +5 points (⚠️ short)
  - <7 days or unclear: warning

**Example:**
```
"10 days replacement" → 10-day window detected
"30-day money back guarantee" → 30-day window detected
```

---

### **2. Return Type**
- **Refund:** Full money back (+15 points)
- **Replacement:** Product exchange (+10 points)
- **Non-returnable:** Final sale (flexibility score drops to 10)

**Example:**
```
"Full refund available" → Refund type detected
"Replacement only" → Replacement type detected
"No returns" → Non-returnable item warning
```

---

### **3. Return Method**
- **Free doorstep pickup:** Best option (+20 points, ✅)
- **Pickup (paid):** Good (+10 points)
- **Drop-off/Self-return:** Customer responsibility (-5 points)

**Example:**
```
"Free pickup at doorstep" → +20 points, excellent!
"Return via courier" → Drop-off required
```

---

### **4. Additional Conditions**
- **Hassle-free returns:** "No questions asked", "Easy return" (+10 points)
- **Strict conditions:** "Original packaging", "Tags attached", "Unopened" (-5 points)

---

## 📊 Flexibility Score (0-100)

**Base Score:** 50/100

**Scoring Breakdown:**
| Feature | Points | Example |
|---------|--------|---------|
| **30+ day window** | +25 | "30-day return policy" |
| **15-29 day window** | +15 | "15-day replacement" |
| **10-14 day window** | +10 | "10-day return" |
| **7-9 day window** | +5 | "7-day return window" |
| **Refund available** | +15 | "Full refund" |
| **Replacement available** | +10 | "Exchange allowed" |
| **Free pickup** | +20 | "Free doorstep pickup" |
| **Paid pickup** | +10 | "Pickup arranged" |
| **Hassle-free** | +10 | "No questions asked" |
| **Strict conditions** | -5 | "Tags must be attached" |
| **Drop-off required** | -5 | "Self-return via courier" |
| **Non-returnable** | Score drops to 10 | "Final sale" |

**Maximum Score:** 100  
**Minimum Score:** 0

---

## 🎯 Real-World Examples

### **Example 1: Amazon (Excellent)**
```json
{
  "return_window_days": 30,
  "type": ["refund", "replacement"],
  "method": ["free-pickup"],
  "flexibility_score": 95,
  "highlights": [
    "🏆 30-day return window (excellent)",
    "✅ Free doorstep pickup",
    "Full refund available"
  ]
}
```
**Why 95/100:** Long window + refund + free pickup = best flexibility

---

### **Example 2: Budget Site (Average)**
```json
{
  "return_window_days": 7,
  "type": ["replacement"],
  "method": ["drop-off"],
  "flexibility_score": 55,
  "highlights": [
    "⚠️ Only 7-day return window (short)",
    "Replacement offered",
    "Conditions apply (packaging/tags required)"
  ]
}
```
**Why 55/100:** Short window + no refund + conditions = limited flexibility

---

### **Example 3: Final Sale (Poor)**
```json
{
  "return_window_days": null,
  "type": ["non-returnable"],
  "method": [],
  "flexibility_score": 10,
  "highlights": [
    "⚠️ Non-returnable item",
    "⚠️ Return window not clearly stated"
  ]
}
```
**Why 10/100:** No returns allowed = very risky purchase

---

## 🔧 How It Works

### **Step 1: Extract Return Window**
Regex patterns detect days mentioned near return keywords:
```python
r"(\d+)\s*days?\s*(return|replacement|refund)"
r"(return|refund)\s*within\s*(\d+)\s*days?"
```

### **Step 2: Identify Return Type**
Keywords: "refund", "money back", "replacement", "exchange", "no return"

### **Step 3: Detect Return Method**
Keywords: "free pickup", "doorstep", "drop off", "self return", "courier"

### **Step 4: Check Conditions**
- Positive: "hassle free", "no questions asked", "easy return"
- Negative: "original packaging", "tags attached", "unopened"

### **Step 5: Calculate Flexibility Score**
Base (50) + bonuses - penalties = 0-100 score

---

## 💡 Usage in Product Comparison

When comparing products, the return policy is included in results:

```json
{
  "site": "Amazon.in",
  "price": "₹500",
  "scores": {
    "deal_truth": 70,
    "review_integrity": 75,
    "store_safety": 80
  },
  "return_policy": {
    "window_days": 10,
    "type": ["replacement"],
    "method": ["pickup"],
    "flexibility_score": 70,
    "highlights": [
      "10-day return window",
      "Replacement offered"
    ]
  }
}
```

---

## 📈 Impact on Recommendations

### **Before (Without Return Policy):**
- Product A: ₹500, Trust: 75/100
- Product B: ₹550, Trust: 80/100
- **Recommendation:** Product A (cheaper)

### **After (With Return Policy):**
- Product A: ₹500, Trust: 75/100, Returns: 55/100 (7-day, drop-off)
- Product B: ₹550, Trust: 80/100, Returns: 95/100 (30-day, free pickup, refund)
- **Recommendation:** Product B (better overall value despite higher price)

**Why:** A flexible return policy adds **real value** by reducing purchase risk!

---

## 🎯 Benefits for Users

1. **Risk Reduction:** Easy returns = safer purchase
2. **Better Comparison:** Beyond just price, consider flexibility
3. **Value Recognition:** 30-day free pickup > 7-day drop-off
4. **Informed Decisions:** Know what you're getting before buying

---

## 🚀 Future Enhancements

Consider adding:
1. **Warranty analysis:** Manufacturer vs seller warranty
2. **Shipping cost comparison:** Free vs paid delivery
3. **Restocking fees:** Hidden costs on returns
4. **Return success rates:** How often returns are accepted
5. **Customer service ratings:** Response time, helpfulness

---

## ✅ Testing

Test the return policy analyzer:

```bash
# Analyze a single product page
python3 analyze_from_html.py --url "https://amazon.in/dp/..." --html_file "page.html"

# Compare across sites (includes return policy)
python3 compare_across_sites.py --product "headphones"
```

The output will now include:
- Return window (days)
- Return type (refund/replacement)
- Return method (pickup/drop-off)
- Flexibility score (0-100)
- Key highlights

---

**Updated:** 2026-02-20  
**Version:** 2.1 (Return Policy Analysis Added)

**Bottom Line:** Users can now make smarter buying decisions by comparing not just price and reviews, but also **return flexibility**! 🎯
