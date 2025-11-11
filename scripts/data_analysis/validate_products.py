#!/usr/bin/env python3
"""
Product Data Validation - Enhanced for Batch Processing
Validates product data quality, detects anomalies, and ensures data integrity
"""

import pandas as pd
import numpy as np
import sys
import os
import json
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'utilities'))

def validate_batch_file(csv_file, detailed=True):
    """
    Validate a batch CSV file for quality and anomalies
    
    Args:
        csv_file: Path to batch CSV file
        detailed: Whether to show detailed anomaly information
        
    Returns:
        dict: Validation results with pass/fail status
    """
    
    print(f"🔍 BATCH VALIDATION ANALYSIS")
    print(f"=" * 50)
    print(f"📁 File: {csv_file}")
    
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return {'status': 'FAIL', 'reason': 'File not found'}
    
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        return {'status': 'FAIL', 'reason': f'CSV load error: {e}'}
    
    validation = {
        'status': 'PASS',
        'total_products': len(df),
        'issues': [],
        'warnings': [],
        'stats': {}
    }
    
    print(f"📊 Total products: {len(df)}")
    
    # 1. CRITICAL FIELD VALIDATION
    print(f"\n🔍 CRITICAL FIELD VALIDATION:")
    critical_fields = ['product_name', 'brand', 'category', 'original_product_id']
    for field in critical_fields:
        if field not in df.columns:
            validation['issues'].append(f"Missing critical field: {field}")
            print(f"❌ Missing field: {field}")
        else:
            missing = df[field].isna().sum()
            if missing > 0:
                validation['issues'].append(f"{field} has {missing} missing values")
                print(f"❌ {field}: {missing} missing values")
            else:
                print(f"✅ {field}: Complete")
    
    # 2. DUPLICATE CHECK
    print(f"\n🔍 DUPLICATE CHECK:")
    if 'original_product_id' in df.columns:
        duplicates = df['original_product_id'].duplicated().sum()
        if duplicates > 0:
            validation['issues'].append(f"Found {duplicates} duplicate product IDs")
            print(f"❌ Duplicate product IDs: {duplicates}")
        else:
            print(f"✅ No duplicate product IDs")
    
    # 3. NUTRITION DATA COMPLETENESS
    print(f"\n🔍 NUTRITION DATA ANALYSIS:")
    nutrition_cols = ['energy_kcal_per_100g', 'carbs_g_per_100g', 'protein_g_per_100g', 'fat_g_per_100g']
    
    # Count products with any nutrition data
    has_any_nutrition = df[nutrition_cols].notna().any(axis=1).sum()
    success_rate = (has_any_nutrition / len(df)) * 100
    validation['stats']['success_rate'] = success_rate
    
    print(f"📈 Products with nutrition data: {has_any_nutrition}/{len(df)} ({success_rate:.1f}%)")
    
    if success_rate < 80:
        validation['issues'].append(f"Low success rate: {success_rate:.1f}% (expected >80%)")
        print(f"❌ Low success rate: {success_rate:.1f}%")
    elif success_rate < 90:
        validation['warnings'].append(f"Moderate success rate: {success_rate:.1f}% (good >90%)")
        print(f"⚠️  Moderate success rate: {success_rate:.1f}%")
    else:
        print(f"✅ Good success rate: {success_rate:.1f}%")
    
    # 4. NUTRITION VALUE ANOMALY DETECTION
    print(f"\n🔍 NUTRITION ANOMALY DETECTION:")
    anomaly_thresholds = {
        'energy_kcal_per_100g': {'max': 1000, 'min': 0},
        'carbs_g_per_100g': {'max': 100, 'min': 0},
        'protein_g_per_100g': {'max': 50, 'min': 0},
        'fat_g_per_100g': {'max': 100, 'min': 0},
        'fiber_g_per_100g': {'max': 50, 'min': 0},
        'sodium_mg_per_100g': {'max': 10000, 'min': 0}
    }
    
    for col, thresholds in anomaly_thresholds.items():
        if col in df.columns:
            values = pd.to_numeric(df[col], errors='coerce').dropna()
            if len(values) > 0:
                # Check for values outside reasonable ranges
                too_high = (values > thresholds['max']).sum()
                too_low = (values < thresholds['min']).sum()
                
                if too_high > 0:
                    validation['warnings'].append(f"{col}: {too_high} values > {thresholds['max']}")
                    print(f"⚠️  {col}: {too_high} values > {thresholds['max']}")
                    
                    if detailed and too_high <= 5:
                        high_values = df[pd.to_numeric(df[col], errors='coerce') > thresholds['max']]
                        for _, row in high_values.head(3).iterrows():
                            print(f"     - {row['product_name'][:40]}: {row[col]}")
                
                if too_low > 0:
                    validation['warnings'].append(f"{col}: {too_low} negative values")
                    print(f"⚠️  {col}: {too_low} negative values")
    
    # 5. CONFIDENCE SCORE ANALYSIS
    print(f"\n🔍 CONFIDENCE SCORE ANALYSIS:")
    if 'confidence_score' in df.columns:
        conf_scores = pd.to_numeric(df['confidence_score'], errors='coerce').dropna()
        if len(conf_scores) > 0:
            print(f"📊 Products with confidence scores: {len(conf_scores)}")
            print(f"📊 Confidence range: {conf_scores.min():.2f} - {conf_scores.max():.2f}")
            print(f"📊 Average confidence: {conf_scores.mean():.2f}")
            
            # Check for unrealistic confidence scores
            invalid_conf = ((conf_scores < 0) | (conf_scores > 1)).sum()
            if invalid_conf > 0:
                validation['issues'].append(f"Invalid confidence scores: {invalid_conf}")
                print(f"❌ Invalid confidence scores (not 0-1): {invalid_conf}")
        else:
            print(f"📊 No explicit confidence scores (using default 0.75)")
    
    # 6. FINAL ASSESSMENT
    print(f"\n🎯 FINAL ASSESSMENT:")
    
    # Determine overall status
    if len(validation['issues']) > 0:
        validation['status'] = 'FAIL'
        print(f"❌ BATCH FAILED VALIDATION")
        print(f"🚫 Critical Issues Found: {len(validation['issues'])}")
        for issue in validation['issues']:
            print(f"   - {issue}")
    elif len(validation['warnings']) > 5:
        validation['status'] = 'WARN'
        print(f"⚠️  BATCH PASSED WITH WARNINGS")
        print(f"⚠️  Warnings: {len(validation['warnings'])}")
    else:
        validation['status'] = 'PASS'
        print(f"✅ BATCH PASSED VALIDATION")
    
    if len(validation['warnings']) > 0:
        print(f"\n⚠️  Warnings ({len(validation['warnings'])}):")
        for warning in validation['warnings'][:10]:  # Show first 10 warnings
            print(f"   - {warning}")
        if len(validation['warnings']) > 10:
            print(f"   ... and {len(validation['warnings']) - 10} more warnings")
    
    # Integration recommendation
    print(f"\n🔄 INTEGRATION RECOMMENDATION:")
    if validation['status'] == 'PASS':
        print(f"✅ PROCEED WITH INTEGRATION")
        print(f"📊 Expected integration rate: {success_rate:.1f}%")
    elif validation['status'] == 'WARN':
        print(f"⚠️  PROCEED WITH CAUTION")
        print(f"📊 Review warnings before integration")
    else:
        print(f"🚫 DO NOT INTEGRATE")
        print(f"🔧 Fix critical issues first")
    
    return validation

def validate_main_database():
    """
    Validate the main products database for overall quality
    Uses the existing data_completion_analysis.py functionality
    """
    
    print(f"🔍 MAIN DATABASE VALIDATION")
    print(f"=" * 50)
    
    # Import and use existing analysis
    sys.path.append(os.path.join(os.path.dirname(__file__)))
    from data_completion_analysis import main as run_completion_analysis
    
    print(f"Running comprehensive data completion analysis...")
    run_completion_analysis()

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("❌ Usage: python validate_products.py [csv_file|--database] [--brief]")
        print("Examples:")
        print("  python validate_products.py llm_batches/output/llama_enhanced_400products_20251030_2010.csv")
        print("  python validate_products.py --database  # Validate main database")
        return
    
    if sys.argv[1] == '--database':
        validate_main_database()
        return
    
    csv_file = sys.argv[1]
    detailed = '--brief' not in sys.argv
    
    validation = validate_batch_file(csv_file, detailed=detailed)
    
    # Exit with appropriate code
    if validation['status'] == 'FAIL':
        sys.exit(1)
    elif validation['status'] == 'WARN':
        sys.exit(2)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()