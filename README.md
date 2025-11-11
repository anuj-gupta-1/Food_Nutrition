# Food Nutrition Database

> Comprehensive Indian food products database with nutritional information, AI-enhanced data processing, and mobile app integration.

[![Products](https://img.shields.io/badge/Products-11,302-blue)]()
[![Nutrition Coverage](https://img.shields.io/badge/Nutrition%20Coverage-70.8%25-green)]()
[![Android](https://img.shields.io/badge/Android-Ready-success)]()

---

## 🎯 Overview

A production-ready food nutrition database featuring:
- **11,302 Indian food products** from major retailers (JioMart, StarQuik)
- **Nutritional data** for 8,000+ products (energy, macros, micronutrients)
- **AI-powered data cleanup** using local and external LLMs
- **Android app integration** with Firebase/Firestore sync
- **Automated batch processing** for continuous data enhancement

---

## 🚀 Quick Start

### For New Contributors
```bash
# 1. Clone and setup
git clone <repo-url>
cd Food_Nutrition
pip install -r requirements.txt

# 2. View current status
cat PROJECT_STATUS.md

# 3. Start contributing
# See scripts/NEW_SESSION_START_HERE.md
```

### For Developers
```bash
# Install Ollama for local LLM processing
# Visit: https://ollama.ai/
ollama pull qwen2.5:7b-instruct

# Run name cleanup (current priority)
python scripts/data_cleanup/llm/run_production.py
```

---

## 📊 Current Status

| Metric | Value | Status |
|--------|-------|--------|
| Total Products | 11,302 | ✅ Complete |
| Nutrition Data | ~8,000 (70.8%) | 🚧 In Progress |
| Name Cleanup | 30/4,508 (0.7%) | 🚧 **Active** |
| Categories | 8 main, 50+ sub | ✅ Complete |
| Android App | Production Ready | ✅ Complete |

**Current Priority:** Product name cleanup (4,478 remaining)  
**See:** [PROJECT_STATUS.md](PROJECT_STATUS.md) for detailed status

---

## 📁 Project Structure

```
Food_Nutrition/
├── data/
│   ├── products.csv              # Main database (11,302 products)
│   └── products_backup_*.csv     # Automatic backups
│
├── scripts/
│   ├── core/                     # Core utilities (CSV, schema, handlers)
│   ├── data_cleanup/             # Data cleaning tools
│   │   └── llm/                  # 🔥 Active: LLM-based name cleanup
│   ├── batch_processing/         # External LLM batch workflows
│   ├── external_services/        # Firebase/Firestore integration
│   ├── utilities/                # Helper scripts
│   └── guides/                   # Documentation
│
├── llm_batches/                  # External LLM processing
│   ├── input/                    # Batches to process
│   ├── output/                   # Processed results
│   └── templates/                # Prompt templates
│
├── android_app/                  # Android application
├── docs/                         # Additional documentation
└── PROJECT_STATUS.md             # 📋 Detailed project status
```

---

## 🛠️ Key Features

### Data Processing
- **Robust CSV Handler:** Handles complex data with `||` delimiter
- **Schema Validation:** Ensures data consistency
- **Automatic Backups:** Keeps 10 most recent versions
- **Batch Processing:** Process 100s of products efficiently

### AI Enhancement
- **Local LLM:** Ollama with Qwen 2.5 7B Instruct (free, private)
- **External LLM:** ChatGPT/Claude batch API (high quality)
- **Smart Cleanup:** Removes marketing fluff, standardizes names
- **Category Classification:** AI-powered categorization

### Integration
- **Firebase/Firestore:** Real-time sync with mobile apps
- **Android App:** Production-ready mobile application
- **REST API:** Flask-based API for data access

---

## 📖 Documentation

| Document | Purpose |
|----------|---------|
| [PROJECT_STATUS.md](PROJECT_STATUS.md) | Complete project status, tasks, and progress |
| [scripts/NEW_SESSION_START_HERE.md](scripts/NEW_SESSION_START_HERE.md) | Quick start for new sessions |
| [scripts/guides/DEVELOPER_GUIDE.md](scripts/guides/DEVELOPER_GUIDE.md) | Development setup and workflows |
| [scripts/guides/CSV_FIELD_REFERENCE.md](scripts/guides/CSV_FIELD_REFERENCE.md) | Database schema reference |
| [scripts/BATCH_PROCESSING_WORKFLOW.md](scripts/BATCH_PROCESSING_WORKFLOW.md) | External LLM batch processing |

---

## 🎯 Current Tasks

### 🔥 Active (In Progress)
- **Product Name Cleanup:** Using local LLM to clean 4,508 product names
  - Location: `scripts/data_cleanup/llm/`
  - Progress: 30/4,508 (0.7%)
  - Run: `python scripts/data_cleanup/llm/run_production.py`

### 📋 Pending (High Priority)
1. **Complete Name Cleanup:** 4,478 products remaining (~2-3 hours)
2. **Category Refinement:** Validate and correct ~500-1,000 products
3. **Missing Nutrition:** Add data for ~3,000 products

### 📋 Pending (Medium Priority)
4. **Ingredients Extraction:** Complete for ~3,000 products
5. **Data Quality Validation:** Check ranges, duplicates, consistency
6. **Image Management:** Download and optimize product images

**See [PROJECT_STATUS.md](PROJECT_STATUS.md) for complete task list**

---

## 🔧 Common Commands

```bash
# View data statistics
python scripts/data_analysis/validate_products.py

# Continue name cleanup (current priority)
python scripts/data_cleanup/llm/run_production.py

# Test LLM on small batch
python scripts/data_cleanup/llm/run_trial.py

# Upload to Firebase
python scripts/external_services/upload_to_firestore.py

# Create external LLM batch
python scripts/batch_processing/create_next_batch.py
```

---

## 🏆 Achievements

- ✅ **11,302 products** scraped and structured
- ✅ **70.8% nutrition coverage** with AI-enhanced data
- ✅ **Hierarchical categorization** (8 categories, 50+ subcategories)
- ✅ **Production-ready Android app** with Firebase sync
- ✅ **Automated workflows** for continuous improvement
- ✅ **Cost-efficient:** Free local LLM processing

---

## 🤝 Contributing

1. Read [PROJECT_STATUS.md](PROJECT_STATUS.md) to understand current state
2. Check [scripts/NEW_SESSION_START_HERE.md](scripts/NEW_SESSION_START_HERE.md) for quick start
3. Pick a task from pending list
4. Follow existing code patterns in `scripts/`
5. Test thoroughly before committing

---

## 📝 Technical Notes

- **CSV Delimiter:** `||` (double pipe) for complex data
- **Encoding:** UTF-8
- **Python:** 3.8+
- **LLM:** Ollama (local) or ChatGPT/Claude (external)
- **Database:** CSV (main), Firebase/Firestore (mobile sync)

---

## 📞 Support

- **Documentation:** Check `docs/` and `scripts/guides/`
- **Issues:** Review [PROJECT_STATUS.md](PROJECT_STATUS.md) known issues
- **Questions:** See developer guide for common scenarios

---

**Status:** Active Development | **Priority:** Name Cleanup | **Next Milestone:** Complete data enhancement

*A clean, organized, and production-ready food nutrition platform.*