# Food Nutrition Database - Project Status

**Last Updated:** November 11, 2025  
**Total Products:** 11,302  
**Data Sources:** JioMart, StarQuik

---

## 🎯 Project Overview

This project maintains a comprehensive Indian food products database with nutritional information, designed for integration with mobile apps and web services.

### Key Features
- Product catalog with 11,302+ items
- Nutritional data (energy, macros, micronutrients)
- Category/subcategory classification
- Brand information and pricing
- Firebase/Firestore integration
- Android app compatibility

---

## ✅ Completed Tasks

### 1. Data Collection & Scraping
- ✅ Scraped 11,302 products from JioMart and StarQuik
- ✅ Extracted product names, brands, prices, sizes
- ✅ Initial category classification

### 2. Data Structure & Schema
- ✅ Established CSV schema with `||` delimiter
- ✅ Created product_schema.py for validation
- ✅ Implemented csv_handler.py for robust CSV parsing
- ✅ Android JSON format compatibility

### 3. Nutritional Data Enhancement
- ✅ Batch processing system for external LLM (ChatGPT/Claude)
- ✅ Processed ~8,000+ products with nutritional data
- ✅ Extracted ingredients lists
- ✅ Standardized nutrition fields (per 100g)

### 4. Category Management
- ✅ Created category_mapping.yaml with hierarchical structure
- ✅ Implemented CategoryManager for validation
- ✅ Defined 8 main categories with 50+ subcategories

### 5. Infrastructure
- ✅ Firebase/Firestore upload scripts
- ✅ Android app data sync
- ✅ Backup system (keeping 10 most recent)
- ✅ Data validation tools

### 6. Firebase/Firestore Integration
- ✅ Upload scripts created and tested
- ✅ Android app successfully syncs with Firebase
- ⚠️ **Firebase database NOT updated with latest CSV changes**
- ⚠️ Firebase contains older version of product data
- 📝 Pending: Upload cleaned names and latest nutrition data

---

## 🚧 In Progress

### Product Name Cleanup (CURRENT PRIORITY)
**Status:** 30/4,508 products processed (0.7%)  
**Tool:** Local Ollama with Qwen 2.5 7B Instruct model  
**Location:** `scripts/data_cleanup/llm/`

**What's Being Done:**
- Removing marketing fluff from product names
- Standardizing name format
- Keeping essential product identifiers
- Processing products with names >= 80 characters

**How to Continue:**
```bash
# Make sure Ollama is running
ollama serve

# Run the production cleanup
python scripts/data_cleanup/llm/run_production.py --min-length 80 --batch-size 100 --delay 1.0
```

**Files:**
- `llm_classification_service.py` - Core LLM service
- `product_classifier.py` - Classification logic
- `run_production.py` - Production batch processor
- `run_trial.py` - Test on small batches

**Progress Tracking:**
- Saves checkpoints every 100 products
- Creates backups before processing
- Logs all changes

---

## 📋 Pending Tasks

### High Priority

#### 1. Complete Product Name Cleanup
- **Remaining:** 4,478 products with long names
- **Estimated Time:** 2-3 hours (with local LLM)
- **Blocker:** Occasional timeouts with Ollama (increased timeout to 120s)

#### 2. Category/Subcategory Refinement
- **Issue:** Some products may be miscategorized
- **Solution:** Use LLM to validate and correct categories
- **Estimated Products:** ~500-1,000 need review
- **Tool:** Can extend current LLM workflow

#### 3. Missing Nutritional Data
- **Products Without Nutrition:** ~3,000
- **Options:**
  - Continue external LLM batch processing
  - Use local LLM (slower but free)
  - Manual data entry for high-priority items

### Medium Priority

#### 4. Firebase/Firestore Sync
**Status:** ⚠️ Out of Sync  
**Priority:** MEDIUM-HIGH  
**Estimated Time:** 30 minutes

**Description:**
Firebase/Firestore database is out of sync with the latest CSV data.

**Current State:**
- Firebase contains older product data
- Latest nutrition data not uploaded
- Cleaned product names not synced
- Android app showing outdated information

**Action Items:**
- [ ] Review current Firebase data
- [ ] Backup Firebase database
- [ ] Upload latest products.csv to Firestore
- [ ] Verify Android app sync
- [ ] Test data integrity

**How to Update:**
```bash
# Upload to Firestore
python scripts/external_services/upload_to_firestore.py

# Verify upload
python scripts/external_services/clean_firebase_data.py --verify
```

**Considerations:**
- Should wait until name cleanup is complete
- Or do incremental updates
- Check Firebase quota/limits

---

#### 5. Ingredients Extraction
- **Status:** Partially done (~8,000 products)
- **Remaining:** ~3,000 products
- **Method:** External LLM batch processing

#### 5. Data Quality Validation
- **Tasks:**
  - Validate nutrition values (realistic ranges)
  - Check for duplicate products
  - Verify brand names consistency
  - Ensure size/unit standardization

#### 6. Image Management
- **Current:** Image URLs stored
- **Needed:** 
  - Download and host images locally
  - Optimize for mobile app
  - Create thumbnails

### Low Priority

#### 7. Additional Data Fields
- Allergen information
- Dietary tags (vegan, gluten-free, etc.)
- Certifications (organic, FSSAI, etc.)
- Shelf life information

#### 8. Search & Discovery
- Implement search indexing
- Add product recommendations
- Create popular products list

---

## 🗂️ Project Structure

```
Food_Nutrition/
├── data/
│   ├── products.csv              # Main database (11,302 products)
│   └── products_backup_*.csv     # 10 most recent backups
│
├── scripts/
│   ├── core/                     # Core utilities
│   │   ├── csv_handler.py        # CSV parsing
│   │   ├── product_handler.py    # Product operations
│   │   └── product_schema.py     # Schema validation
│   │
│   ├── data_cleanup/
│   │   ├── llm/                  # LLM-based cleanup (ACTIVE)
│   │   │   ├── llm_classification_service.py
│   │   │   ├── product_classifier.py
│   │   │   ├── run_production.py
│   │   │   └── run_trial.py
│   │   ├── config/
│   │   │   └── category_mapping.yaml
│   │   └── core/
│   │       └── category_manager.py
│   │
│   ├── batch_processing/         # External LLM batches
│   ├── external_services/        # Firebase/Firestore
│   ├── utilities/                # Helper scripts
│   └── guides/                   # Documentation
│
├── llm_batches/                  # External LLM workflow
│   ├── input/                    # Batches to process
│   ├── output/                   # Processed results
│   └── templates/                # Prompt templates
│
├── android_app/                  # Android app code
├── public/                       # Web hosting files
└── docs/                         # Documentation

```

---

## 🚀 Quick Start for New Contributors

### Setup
```bash
# 1. Clone repository
git clone <repo-url>
cd Food_Nutrition

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. For LLM cleanup, install Ollama
# Visit: https://ollama.ai/
ollama pull qwen2.5:7b-instruct
```

### Common Tasks

**View Data:**
```bash
python scripts/data_analysis/validate_products.py
```

**Continue Name Cleanup:**
```bash
python scripts/data_cleanup/llm/run_production.py
```

**Upload to Firebase:**
```bash
python scripts/external_services/upload_to_firestore.py
```

**Create External LLM Batch:**
```bash
python scripts/batch_processing/create_next_batch.py
```

---

## 📊 Data Statistics

| Metric | Count | Percentage |
|--------|-------|------------|
| Total Products | 11,302 | 100% |
| With Nutrition Data | ~8,000 | 70.8% |
| With Ingredients | ~8,000 | 70.8% |
| Long Names (>80 chars) | 4,508 | 39.9% |
| Names Cleaned | 30 | 0.7% |
| Categories | 8 | - |
| Subcategories | 50+ | - |

---

## 🔧 Technical Notes

### CSV Format
- Delimiter: `||` (double pipe)
- Encoding: UTF-8
- Special handling for embedded JSON and URLs

### LLM Configuration
- **Local:** Ollama with Qwen 2.5 7B Instruct
- **External:** ChatGPT-4 or Claude (via batch API)
- **Timeout:** 120 seconds per request
- **Batch Size:** 100 products per checkpoint

### Firebase Structure
- Collection: `products`
- Document ID: Product ID
- Indexes: category, subcategory, brand

---

## 📝 Notes for Handoff

1. **Name Cleanup is Priority:** 4,478 products still need processing
2. **Ollama Must Be Running:** `ollama serve` before running cleanup
3. **Backups Are Automatic:** Created before each batch
4. **Checkpoints Every 100:** Safe to interrupt and resume
5. **Review Results:** Check `llm_batches/output/` for processed batches

---

## 🐛 Known Issues

1. **Ollama Timeouts:** Occasional timeouts with complex product names
   - **Solution:** Increased timeout to 120s, retry logic in place

2. **CSV Parsing:** Some products have `||` in URLs
   - **Solution:** csv_handler.py handles field count mismatches

3. **Category Ambiguity:** Some products fit multiple categories
   - **Solution:** Manual review needed for edge cases

---

## 📞 Contact & Resources

- **Documentation:** `docs/` and `scripts/guides/`
- **Developer Guide:** `scripts/guides/DEVELOPER_GUIDE.md`
- **CSV Reference:** `scripts/guides/CSV_FIELD_REFERENCE.md`
- **Batch Processing:** `scripts/BATCH_PROCESSING_WORKFLOW.md`

---

**Ready to contribute?** Start with `scripts/NEW_SESSION_START_HERE.md`
