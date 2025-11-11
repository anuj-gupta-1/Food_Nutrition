# 🚀 NEW SESSION? START HERE!

## 📋 IMMEDIATE CHECKLIST FOR NEW SESSIONS

### 1. READ THESE DOCUMENTS FIRST:
- **`BATCH_PROCESSING_WORKFLOW.md`** - Complete guide (5-10 min read)
- **`BATCH_PROCESSING_CHECKLIST.md`** - Quick reference checklist

### 2. VERIFY SYSTEM STATUS:
```bash
# Check database status
python -c "import pandas as pd; import sys; import os; sys.path.append('scripts/core'); from csv_handler import load_products_csv; df = load_products_csv(); enhanced = df[df['llm_fallback_used'] == True]; print(f'Enhanced: {len(enhanced)}/{len(df)} ({len(enhanced)/len(df)*100:.1f}%)')"

# Check Ollama
ollama list
```

### 3. CURRENT SYSTEM STATUS (Oct 30, 2024):
- **Enhanced products**: 1,319 
- **Success rate**: 97.2% (last batch)
- **Quality validation**: ACTIVE and MANDATORY
- **Integration safeguards**: ENABLED

## 🎯 QUICK START (5-STEP PROCESS):

### For 100 Products:
```bash
# Step 1: Create batch
python scripts/batch_processing/create_next_batch.py 100

# Step 2: Edit process_with_local_llama.py 
# - Update input_file with new filename
# - Update max_products to 100

# Step 3: Process
python scripts/batch_processing/process_with_local_llama.py

# Step 4: Validate (MANDATORY)
python scripts/data_analysis/validate_products.py [OUTPUT_FILE]

# Step 5: Integrate (only if Step 4 PASSES)
python scripts/integration/integrate_batch_with_missing_data.py [OUTPUT_FILE]
```

## 🚨 CRITICAL REMINDERS:

### NEVER:
- ❌ Skip validation (Step 4)
- ❌ Create new scripts when existing ones work
- ❌ Treat N/A confidence as invalid
- ❌ Integrate FAIL status batches

### ALWAYS:
- ✅ Follow 5-step process exactly
- ✅ Update filenames in Step 2
- ✅ Wait for PASS validation
- ✅ Use existing established scripts

## 📞 HELP COMMANDS:
```bash
# Quick help
python scripts/RUN_BATCH_PROCESS.py --help

# Validate existing batch
python scripts/data_analysis/validate_products.py [file] --brief

# Check database
python scripts/data_analysis/validate_products.py --database
```

## 🎯 SUCCESS PATTERN:
**Last Success**: 400 products, 97.2% processing rate, 100% integration rate, 0 critical issues.

**Follow the guides exactly - they are bulletproof and battle-tested!**