# Scripts Organization

> Organized development tools for the Food Nutrition Database project

---

## 📁 Directory Structure

```
scripts/
├── core/                    # Core utilities
├── data_cleanup/            # Data cleaning tools
│   └── llm/                # 🔥 Active: LLM name cleanup
├── batch_processing/        # External LLM workflows
├── data_analysis/           # Validation and reporting
├── external_services/       # Firebase/API integration
├── utilities/               # Helper scripts
├── guides/                  # Documentation
├── specs/                   # Specifications
└── templates/               # Prompt templates
```

---

## 🔥 Currently Active

### LLM Name Cleanup (`data_cleanup/llm/`)
**Status:** In Progress (30/4,508 products)  
**Priority:** HIGH

Clean verbose product names using local Ollama LLM.

```bash
# Run production cleanup
python scripts/data_cleanup/llm/run_production.py

# Test on small batch
python scripts/data_cleanup/llm/run_trial.py
```

**See:** [data_cleanup/llm/README.md](data_cleanup/llm/README.md) for details

---

## 📂 Core Modules

### `core/` - Essential Utilities
| File | Purpose |
|------|---------|
| `csv_handler.py` | Robust CSV parsing with `\|\|` delimiter |
| `product_handler.py` | Product data operations |
| `product_schema.py` | Schema validation |

### `data_cleanup/` - Data Cleaning
| Directory | Purpose |
|-----------|---------|
| `llm/` | **Active:** LLM-based name cleanup |
| `config/` | Category mappings and configs |
| `core/` | Category manager and validators |
| `migrations/` | Data migration scripts |

### `batch_processing/` - External LLM Workflows
| File | Purpose |
|------|---------|
| `create_next_batch.py` | Create batches for external LLM |
| `process_with_local_llama.py` | Process with local Llama |
| `setup_batch_folders.py` | Initialize batch structure |

### `data_analysis/` - Validation & Reporting
| File | Purpose |
|------|---------|
| `validate_products.py` | Validate product data |
| `data_completion_analysis.py` | Analyze data completeness |

### `external_services/` - Integration
| File | Purpose |
|------|---------|
| `upload_to_firestore.py` | Upload to Firebase |
| `clean_firebase_data.py` | Clean Firebase data |
| `llm_nutrition_service.py` | LLM service integration |
| `realtime_nutrition_api.py` | REST API endpoints |

### `utilities/` - Helper Scripts
| File | Purpose |
|------|---------|
| `nutrition_validator.py` | Validate nutrition data |
| `standardize_nutrition.py` | Standardize nutrition fields |
| `standardize_units.py` | Standardize units |
| `fix_android_json_format.py` | Android compatibility |
| `update_android_assets.py` | Update Android app data |

---

## 📖 Documentation

### Guides (`guides/`)
- **DEVELOPER_GUIDE.md** - Complete development setup
- **EXTERNAL_LLM_GUIDE.md** - External LLM processing
- **CSV_FIELD_REFERENCE.md** - Database schema
- **CSV_SHARING_GUIDE.md** - Data sharing guide

### Specifications (`specs/`)
- **Product_Specifications.md** - Product data specs

### Templates (`templates/`)
- **external_llm_prompt_template.txt** - LLM prompt template

---

## 🚀 Common Workflows

### 1. LLM Name Cleanup (Current Priority)
```bash
# Ensure Ollama is running
ollama serve

# Run production cleanup
python scripts/data_cleanup/llm/run_production.py --min-length 80 --batch-size 100 --delay 1.0

# Or test first
python scripts/data_cleanup/llm/run_trial.py
```

### 2. External LLM Batch Processing
```bash
# Create batch
python scripts/batch_processing/create_next_batch.py 200

# Process with local Llama
python scripts/batch_processing/process_with_local_llama.py

# Validate results
python scripts/data_analysis/validate_products.py llm_batches/output/[file].csv

# Integrate to database
python scripts/integration/integrate_batch_with_missing_data.py llm_batches/output/[file].csv
```

### 3. Data Validation
```bash
# Validate all products
python scripts/data_analysis/validate_products.py

# Check data completeness
python scripts/data_analysis/data_completion_analysis.py
```

### 4. Firebase Sync
```bash
# Upload to Firestore
python scripts/external_services/upload_to_firestore.py

# Clean Firebase data
python scripts/external_services/clean_firebase_data.py
```

### 5. Android App Update
```bash
# Update Android assets
python scripts/utilities/update_android_assets.py

# Verify compatibility
python scripts/utilities/verify_android_compatibility.py
```

---

## 🛡️ Quality Safeguards

All scripts include:
- **Automatic backups** before modifications
- **Validation checks** for data integrity
- **Error handling** with fallbacks
- **Progress tracking** and logging
- **Checkpoint saves** for long operations

---

## 📊 Script Statistics

- **Total Scripts:** ~25 active scripts
- **Core Utilities:** 3 essential modules
- **Data Cleanup:** 5 LLM scripts (active)
- **Batch Processing:** 3 workflow scripts
- **Integration:** 4 service scripts
- **Documentation:** 7 comprehensive guides

---

## 🎯 Quick Reference

### For New Contributors
1. Read [PROJECT_STATUS.md](../PROJECT_STATUS.md)
2. Review [guides/DEVELOPER_GUIDE.md](guides/DEVELOPER_GUIDE.md)
3. Check [NEW_SESSION_START_HERE.md](NEW_SESSION_START_HERE.md)

### For Current Tasks
- **Name Cleanup:** See [data_cleanup/llm/README.md](data_cleanup/llm/README.md)
- **Batch Processing:** See [BATCH_PROCESSING_WORKFLOW.md](BATCH_PROCESSING_WORKFLOW.md)
- **CSV Format:** See [guides/CSV_FIELD_REFERENCE.md](guides/CSV_FIELD_REFERENCE.md)

### For Integration
- **Firebase:** See [external_services/](external_services/)
- **Android:** See [utilities/](utilities/) Android scripts
- **API:** See [external_services/realtime_nutrition_api.py](external_services/realtime_nutrition_api.py)

---

## 💡 Tips

- **Always backup:** Scripts create automatic backups
- **Test first:** Use trial/test scripts before production
- **Check status:** Review PROJECT_STATUS.md regularly
- **Follow patterns:** Use existing scripts as templates
- **Document changes:** Update relevant READMEs

---

**Status:** Organized & Production Ready | **Last Updated:** November 11, 2025