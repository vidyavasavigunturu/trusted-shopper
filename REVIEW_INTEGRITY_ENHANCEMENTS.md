# Review Integrity Enhancements

## 🎯 Overview

Enhanced the `analyze_from_html.py` script with advanced review integrity checks to better detect authentic vs. fake/generic reviews.

---

## ✅ New Checks Added

### **1. Recent Reviews Detection (+5 points)**
- **What:** Looks for review timestamps from last 1-3 months
- **Keywords:** Month names (January, Feb, etc.), "ago", "days ago", "weeks ago"
- **Why:** Recent reviews are more relevant and harder to fake in bulk
- **Penalty:** -5 if no recent dates found

### **2. Authentic Content Analysis (+10 points)**
- **What:** Detects detailed reviews mentioning real issues
- **Keywords:** 
  - Defects: "defect", "damage", "broken", "issue", "problem"
  - Packaging: "packaging", "shipped", "arrived", "received"
  - Service: "delivery", "customer care", "return", "refund"
  - Quality: "build quality", "quality"
- **Scoring:**
  - 3+ mentions: +10 points (authentic detailed reviews)
  - 1-2 mentions: +5 points (some authenticity)
  - 0 mentions: -5 penalty (suspiciously vague)
- **Why:** Real users discuss problems, shipping, and service—not just "great product!"

### **3. User Photos Detection (+10 points)**
- **What:** Looks for evidence of user-uploaded photos
- **Keywords:** "verified purchase", "customer image", "customer photo", "uploaded", "review photo"
- **Why:** Photos from real users are strong authenticity signals
- **Penalty:** -5 if no photo evidence found

### **4. Generic 5-Star Filter (-10 points)**
- **What:** Detects overly generic praise phrases
- **Keywords:** "excellent product", "great product", "amazing product", "highly recommend", "must buy"
- **Trigger:** 4+ generic phrases detected
- **Why:** Fake reviews often use templated positive language
- **Example fake pattern:** "Excellent product! Highly recommend! Must buy! Great product!"

### **5. Enhanced Hype Detection (-10 points)**
- **What:** Expanded detection of extreme promotional language
- **Keywords:** "best ever", "100% recommended", "life changing", "miracle product", "perfect in every way", "flawless", "zero complaints"
- **Trigger:** 2+ hype phrases detected
- **Why:** Real reviews mention pros AND cons; fake reviews are unrealistically positive

---

## 📊 Scoring Summary

### **Base Score:** 70/100

### **Positive Signals (can gain up to +25 points):**
- Recent reviews: +5
- Authentic content (3+ mentions): +10
- User photos: +10

### **Negative Signals (can lose up to -45 points):**
- No reviews section: -15
- No recent dates: -5
- No detailed content: -5
- No user photos: -5
- Generic 5-star spam (4+ phrases): -10
- Excessive hype (2+ phrases): -10

### **Max Possible Score:** 95/100 (70 + 25)
### **Min Possible Score:** 25/100 (70 - 45)

---

## 🎯 Real-World Examples

### **High Score Example (85/100):**
✅ Reviews from "2 months ago", "January 2026"  
✅ Mentions "packaging was good", "delivery on time", "minor defect in button"  
✅ "Verified purchase" badges visible  
✅ No excessive hype  
**Result:** Authentic, trustworthy reviews

### **Low Score Example (40/100):**
❌ No review dates visible  
❌ Only says "excellent product", "must buy", "amazing"  
❌ No mention of delivery, packaging, or issues  
❌ No customer photos  
❌ Generic 5-star praise everywhere  
**Result:** Suspicious, likely fake/paid reviews

---

## 🔧 Technical Implementation

### **Code Location:**
`/home/ubuntu/.openclaw/workspace/trusted-shopper/scripts/analyze_from_html.py`

### **Function Modified:**
`score(signals)` - Enhanced review integrity section

### **Algorithm:**
1. Start with baseline: 70/100
2. Check for review presence (-15 if none)
3. Scan for recent dates (+5 or -5)
4. Count authentic keywords (+10/+5/-5)
5. Look for photo evidence (+10 or -5)
6. Filter generic praise (-10 if 4+)
7. Detect excessive hype (-10 if 2+)
8. Clamp final score to 0-100 range

---

## 🚀 Usage

The enhanced checks automatically apply when running:

```bash
python3 trusted-shopper/scripts/analyze_from_html.py \
  --url "https://example.com/product" \
  --html_file "page.html"
```

Or via multi-site comparison:

```bash
python3 trusted-shopper/scripts/compare_across_sites.py \
  --product "wireless earbuds"
```

---

## 📈 Expected Impact

### **Before Enhancement:**
- Generic reviews scored 70/100 (neutral)
- Hard to distinguish fake vs. real
- No recency consideration

### **After Enhancement:**
- Authentic reviews score 80-95/100
- Generic/fake reviews score 30-50/100
- Recent, detailed reviews prioritized
- User photos add credibility

**Net Result:** Better deal recommendations, fewer scams suggested

---

## 🔄 Future Improvements

Consider adding:
1. **Star distribution analysis** - Check if ratings are suspiciously skewed
2. **Review velocity** - Flag products with sudden review spikes
3. **Reviewer history** - Detect serial 5-star reviewers
4. **Sentiment analysis** - Use NLP to detect fake positive sentiment
5. **Cross-site comparison** - Flag if same reviews appear on multiple sites

---

## ✅ Testing

To test the enhancements:

```bash
# Test with a known good product (Amazon with verified purchases)
python3 analyze_from_html.py --url "https://amazon.in/dp/..." --html_file good.html

# Test with a known sketchy product
python3 analyze_from_html.py --url "https://sketchy-site.com/..." --html_file bad.html
```

Compare the review_integrity scores and reasons output.

---

**Updated:** 2026-02-20  
**Version:** 2.0 (Enhanced Review Integrity)
