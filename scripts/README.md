# Scripts Organization - Production Ready

## 📁 **Core** (Essential utilities)
- `csv_handler.py` - Main CSV parsing and handling
- `product_handler.py` - Product data management  
- `product_schema.py` - Data structure definitions

## 🔄 **Batch Processing** (LLM workflows)
- `create_next_batch.py` - **PRIMARY**: Create new batches excluding enhanced products
- `setup_batch_folders.py` - Initialize batch folder structure

## 🔗 **Integration** (Merge LLM results)
- `integrate_batch_with_missing_data.py` - **PRIMARY**: Smart integration with quality filtering

## 📊 **Data Analysis** (Quality and reporting)
- `data_completion_analysis.py` - Analyze data completeness
- `validate_products.py` - Product data validation

## 🛠️ **Utilities** (Helper functions)
- `nutrition_validator.py` - Nutrition data validation
- `nutrition_display.py` - Display formatting
- `standardize_nutrition.py` - Nutrition standardization
- `standardize_units.py` - Unit standardization

## 🌐 **External Services** (Production APIs)
- `llm_nutrition_service.py` - LLM service integration
- `realtime_nutrition_api.py` - Real-time API endpoints
- `upload_to_firestore.py` - Firebase integration
- `clean_firebase_data.py` - Firebase cleanup

## 🔧 **Legacy Fixes** (Historical fixes)
- `fix_csv_parsing.py` - CSV parsing fixes
- `fix_none_comparisons.py` - None comparison fixes

---

## 🚀 **Production Workflow**
1. **Create batch**: `python scripts/batch_processing/create_next_batch.py`
2. **Process with external LLM**: Use ChatGPT/Gemini with templates
3. **Integrate results**: `python scripts/integration/integrate_batch_with_missing_data.py`
4. **Validate**: `python scripts/data_analysis/validate_products.py`

## 📈 **Current Status**
- **Total scripts**: 18 (down from 60+)
- **Essential only**: Removed 40+ redundant/obsolete scripts
- **Clean structure**: Organized by function
- **Production ready**: Focused on core functionality