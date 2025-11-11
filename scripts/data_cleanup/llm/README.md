# LLM-Based Product Name Cleanup

> Automated product name cleanup using local Ollama LLM (Qwen 2.5 7B Instruct)

---

## 🎯 Purpose

Clean up verbose product names by removing marketing fluff while keeping essential information:

**Before:**
```
Sambhojanam Sugar free Diet flour wheat free for Manage Diabetes Gluten free
```

**After:**
```
Sugar Free Gluten Free Diet Flour
```

---

## 📊 Current Status

- **Total Products:** 11,302
- **Products with long names (>80 chars):** 4,508 (39.9%)
- **Processed:** 30 (0.7%)
- **Remaining:** 4,478
- **Estimated Time:** 2-3 hours

---

## 🚀 Quick Start

### Prerequisites

1. **Install Ollama:**
   ```bash
   # Visit: https://ollama.ai/
   # Download and install for your OS
   ```

2. **Pull the model:**
   ```bash
   ollama pull qwen2.5:7b-instruct
   ```

3. **Start Ollama server:**
   ```bash
   ollama serve
   ```

### Run Production Cleanup

```bash
# From project root
python scripts/data_cleanup/llm/run_production.py

# With custom parameters
python scripts/data_cleanup/llm/run_production.py --min-length 80 --batch-size 100 --delay 1.0
```

### Test on Small Batch

```bash
# Test on 10 products first
python scripts/data_cleanup/llm/run_trial.py
```

---

## 📁 Files

| File | Purpose |
|------|---------|
| `llm_classification_service.py` | Core LLM service, handles Ollama API calls |
| `product_classifier.py` | Classification logic, category validation |
| `run_production.py` | Production batch processor (main script) |
| `run_trial.py` | Test on small batches |
| `continue_production.py` | Resume interrupted processing |

---

## ⚙️ Configuration

### Parameters

```python
# In run_production.py
--min-length 80        # Minimum name length to process
--batch-size 100       # Checkpoint frequency
--delay 1.0           # Delay between API calls (seconds)
```

### LLM Settings

```python
# In llm_classification_service.py
model = "qwen2.5:7b-instruct"
timeout = 120  # seconds
temperature = 0.3
top_p = 0.9
max_tokens = 200
```

---

## 🔄 Workflow

1. **Load Products:** Reads from `data/products.csv`
2. **Filter:** Selects products with names >= 80 characters
3. **Process:** For each product:
   - Calls Ollama LLM with cleanup prompt
   - Parses response (new name, subcategory, confidence)
   - Updates product in DataFrame
4. **Checkpoint:** Saves every 100 products
5. **Backup:** Creates backup before final save
6. **Summary:** Shows statistics and completion time

---

## 📝 Cleanup Rules

### DELETE Everything:
- Brand name (already in separate field)
- Sizes/weights/quantities
- Marketing words: Premium, Healthy, Rich, Traditional, etc.
- Usage descriptions: "for cooking", "for fasting", etc.
- Symbols (except hyphen)
- Parentheses

### KEEP Only:
- Product type (Macaroni, Rice, Oil, Tea)
- Specific variety (Basmati, Seeraga Samba, Kuttu)
- Indian/regional terms (Rajasthani, Pudina, Desi Khand)
- Essential descriptors: Organic, Brown, Cold Pressed
- Dietary: Gluten Free, Sugar Free
- Combo format: "Pack of [Item1] and [Item2]"

### Maximum: 5 words in output

---

## 📊 Output

### Console Output
```
================================================================================
PRODUCTION LLM PRODUCT CLASSIFICATION
================================================================================

✅ Loaded 11,302 total products
✅ Found 4,508 products with names >= 80 characters
✅ Classifier initialized with Qwen2.5 Instruct

🚀 Starting production run...
   - Processing 4,508 products
   - Batch size: 100
   - Delay between calls: 1.0s

  -> Processing: Momsy Premium PAAN Candy | Flavored Sugar Candy...
  -> Calling Llama model: qwen2.5:7b-instruct
  -> Got response from Llama

Progress: 100/4508 (2.2%) | Rate: 0.9 products/sec | ETA: 81.5 min

💾 Saving checkpoint at 100 products...
✅ Checkpoint saved
```

### Final Summary
```
================================================================================
PRODUCTION RUN COMPLETE
================================================================================
Total Processed: 4,508
Products Updated: 4,320 (95.8%)
Errors: 12
Time Elapsed: 125.3 minutes
Average Rate: 0.6 products/second

✅ Updated products saved to data/products.csv
================================================================================
```

---

## 🛡️ Safety Features

1. **Automatic Backups:** Created before processing starts
2. **Checkpoints:** Saves every 100 products (resumable)
3. **Error Handling:** Continues on individual failures
4. **Fallback:** Uses original name if LLM fails
5. **Validation:** Checks subcategory against valid list

---

## 🐛 Troubleshooting

### Ollama Not Running
```
❌ Cannot connect to Ollama. Make sure it's running with: ollama serve
```
**Solution:** Start Ollama in a separate terminal: `ollama serve`

### Timeout Errors
```
❌ Llama classification error: Read timed out
```
**Solution:** 
- Increase timeout in `llm_classification_service.py`
- Reduce batch size
- Check system resources (CPU/RAM)

### Model Not Found
```
❌ Model qwen2.5:7b-instruct not found
```
**Solution:** Pull the model: `ollama pull qwen2.5:7b-instruct`

### Slow Processing
**Causes:**
- System resources (CPU/RAM)
- Other processes using Ollama
- Network issues (if Ollama is remote)

**Solutions:**
- Close other applications
- Increase delay between calls
- Use smaller batch size

---

## 📈 Performance

### Expected Rates
- **Fast:** 1-2 products/second (good hardware)
- **Normal:** 0.5-1 products/second (average hardware)
- **Slow:** 0.2-0.5 products/second (limited resources)

### Estimated Times
- **4,508 products:**
  - Fast: 37-75 minutes
  - Normal: 75-150 minutes
  - Slow: 150-375 minutes

---

## 🔍 Quality Checks

After processing, verify results:

```bash
# Check processed products
python scripts/data_analysis/validate_products.py

# View sample of cleaned names
python -c "
import sys
sys.path.append('scripts/core')
from csv_handler import load_products_csv
df = load_products_csv()
print(df[['product_name', 'brand', 'category']].head(20))
"
```

---

## 📋 Next Steps After Completion

1. **Review Results:** Check for any obvious errors
2. **Validate Categories:** Ensure subcategories are correct
3. **Upload to Firebase:** Sync with mobile app
4. **Update Android App:** Test with cleaned names
5. **Move to Next Task:** Category refinement or nutrition data

---

## 💡 Tips

- **Run overnight:** For large batches
- **Monitor progress:** Check console output periodically
- **Resume anytime:** Safe to interrupt (Ctrl+C)
- **Test first:** Use `run_trial.py` on 10 products
- **Check backups:** Verify backup created before processing

---

## 📞 Support

- **Issues:** Check troubleshooting section above
- **Questions:** See main [PROJECT_STATUS.md](../../../PROJECT_STATUS.md)
- **Code:** Review `llm_classification_service.py` for details

---

**Status:** Active | **Priority:** High | **Estimated Completion:** 2-3 hours
