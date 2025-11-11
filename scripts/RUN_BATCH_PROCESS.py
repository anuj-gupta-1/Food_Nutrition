#!/usr/bin/env python3
"""
BATCH PROCESSING QUICK REFERENCE - ESTABLISHED WORKFLOW

This script documents the exact commands to run for batch processing.
DO NOT MODIFY - this is the established, working process.

Usage: python scripts/RUN_BATCH_PROCESS.py --help
"""

import sys
import os
import subprocess
from datetime import datetime

def print_help():
    """Print help information"""
    print("""
ESTABLISHED BATCH PROCESSING WORKFLOW
=====================================

STEP 1: Create new batch
    python scripts/batch_processing/create_next_batch.py [NUMBER]
    
    Examples:
    python scripts/batch_processing/create_next_batch.py 50
    python scripts/batch_processing/create_next_batch.py 100
    
STEP 2: Update process script with new batch filename
    Edit: scripts/batch_processing/process_with_local_llama.py
    Update: input_file = "llm_batches/input/input_all_categories_[N]products_[TIMESTAMP].csv"
    
STEP 3: Process with local Llama
    python scripts/batch_processing/process_with_local_llama.py
    
STEP 4: MANDATORY Quality Analysis (Enhanced Existing Validator)
    python scripts/data_analysis/validate_products.py [OUTPUT_FILE]
    
    Exit codes: 0=PASS, 1=FAIL (don't integrate), 2=WARN (review first)
    
STEP 5: Integrate to main database (Only if quality check passes)
    python scripts/integration/integrate_batch_with_missing_data.py [OUTPUT_FILE]
    
    Example:
    python scripts/integration/integrate_batch_with_missing_data.py llm_batches/output/llama_enhanced_100products_20251030_1140.csv

ESTABLISHED PATTERNS:
- N/A confidence scores are NORMAL and get default 0.75 confidence
- Success rate typically 85-90% integration
- Quality threshold: 0.6 minimum confidence
- Default confidence for N/A: 0.75
- Android/Firebase compatibility: AUTOMATIC (flat JSON format)

ANDROID/FIREBASE COMPATIBILITY (BUILT-IN):
- Nutrition data stored in flat JSON format (not nested)
- Compatible with Android CsvParser.kt expectations
- Ready for Firebase deployment without conversion
- Field mapping: total_sugars_g → sugars_g

DO NOT REINVENT - FOLLOW THIS EXACT PROCESS
""")

def create_batch(count=50):
    """Create new batch - ESTABLISHED PROCESS"""
    print(f"🔄 Creating batch of {count} products...")
    cmd = f"python scripts/batch_processing/create_next_batch.py {count}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Batch created successfully")
        print("⚠️  NEXT: Update input_file in scripts/batch_processing/process_with_local_llama.py")
        print("📝 Look for the new file in llm_batches/input/ and update the script")
    else:
        print(f"❌ Batch creation failed: {result.stderr}")

def process_batch():
    """Process batch with local Llama - ESTABLISHED PROCESS"""
    print("🤖 Processing batch with local Llama...")
    print("⚠️  Make sure you updated the input_file in process_with_local_llama.py")
    
    cmd = "python scripts/batch_processing/process_with_local_llama.py"
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("✅ Processing completed")
        print("📝 Check llm_batches/output/ for the enhanced file")
    else:
        print("❌ Processing failed")

def integrate_batch(output_file):
    """Integrate batch to main database - ESTABLISHED PROCESS"""
    if not output_file:
        print("❌ Please provide output file path")
        print("📝 Example: llm_batches/output/llama_enhanced_100products_20251030_1140.csv")
        return
    
    print(f"📊 Integrating batch: {output_file}")
    cmd = f"python scripts/integration/integrate_batch_with_missing_data.py {output_file}"
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode == 0:
        print("✅ Integration completed successfully")
    else:
        print("❌ Integration failed")

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print_help()
    elif sys.argv[1] == "create":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 50
        create_batch(count)
    elif sys.argv[1] == "process":
        process_batch()
    elif sys.argv[1] == "integrate":
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        integrate_batch(output_file)
    else:
        print_help()