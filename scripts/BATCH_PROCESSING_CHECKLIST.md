# BATCH PROCESSING CHECKLIST - QUICK REFERENCE

## 🚀 BEFORE STARTING
- [ ] Ollama is running (`ollama serve`)
- [ ] Model available (`ollama list` shows llama3.2:3b)
- [ ] Check database status (enhanced products count)

## 📋 STEP-BY-STEP CHECKLIST

### STEP 1: Create Batch
- [ ] Run: `python scripts/batch_processing/create_next_batch.py [N]`
- [ ] Note EXACT filename: `input_all_categories_[N]products_[TIMESTAMP].csv`
- [ ] Verify file exists in `llm_batches/input/`

### STEP 2: Update Script  
- [ ] Edit: `scripts/batch_processing/process_with_local_llama.py`
- [ ] Update `input_file` with EXACT filename from Step 1
- [ ] Update `max_products` to match [N]
- [ ] Save file

### STEP 3: Process with Llama
- [ ] Run: `python scripts/batch_processing/process_with_local_llama.py`
- [ ] Wait for completion (2-5 minutes per 100 products)
- [ ] Note output file: `llama_enhanced_[N]products_[TIMESTAMP].csv`
- [ ] Verify success rate >95%

### STEP 4: Validate Quality (MANDATORY)
- [ ] Run: `python scripts/data_analysis/validate_products.py [OUTPUT_FILE]`
- [ ] Check exit code: 0=PASS, 1=FAIL, 2=WARN
- [ ] If FAIL: STOP, fix issues first

### STEP 5: Integrate to Database
- [ ] Run: `python scripts/integration/integrate_batch_with_missing_data.py [OUTPUT_FILE]`
- [ ] Verify integration success rate >95%
- [ ] Check Android compatibility: ✅ Flat JSON format
- [ ] Verify Android assets updated automatically
- [ ] Confirm database backup created
- [ ] If PASS/WARN: Continue to Step 5

### STEP 5: Integrate to Database
- [ ] Run: `python scripts/integration/integrate_batch_with_missing_data.py [OUTPUT_FILE]`
- [ ] Verify quality analysis passes automatically
- [ ] Check integration success rate >95%
- [ ] Verify database backup created

## ✅ SUCCESS INDICATORS
- [ ] No critical errors in any step
- [ ] Processing success rate >95%
- [ ] Validation status: PASS or WARN
- [ ] Integration success rate >95%
- [ ] Database enhanced count increased

## 🚨 RED FLAGS (STOP IF YOU SEE)
- ❌ Validation FAIL status (exit code 1)
- ❌ Processing success rate <80%
- ❌ Integration success rate <80%
- ❌ File not found errors
- ❌ Ollama connection failures

## 📞 QUICK COMMANDS

### Check Database Status:
```bash
python -c "import pandas as pd; import sys; import os; sys.path.append('scripts/core'); from csv_handler import load_products_csv; df = load_products_csv(); enhanced = df[df['llm_fallback_used'] == True]; print(f'Enhanced: {len(enhanced)}/{len(df)} ({len(enhanced)/len(df)*100:.1f}%)')"
```

### Test Ollama:
```bash
ollama list
```

### Verify Files:
```bash
ls llm_batches/input/input_all_categories_*products_*.csv | tail -1
ls llm_batches/output/llama_enhanced_*products_*.csv | tail -1
```

## 🎯 TYPICAL PERFORMANCE
- **50 products**: ~2 minutes total
- **100 products**: ~5 minutes total  
- **200 products**: ~10 minutes total
- **400 products**: ~20 minutes total

**Success Rate Expected**: 95-100% at each step