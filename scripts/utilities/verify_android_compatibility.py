#!/usr/bin/env python3
"""
Verify Android Compatibility - Check if CSV format matches Android expectations
"""

import pandas as pd
import json
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from csv_handler import load_products_csv

def verify_android_compatibility():
    """Verify that the CSV format is compatible with Android app expectations"""
    
    print("🔍 VERIFYING ANDROID COMPATIBILITY")
    print("=" * 50)
    
    # Load database
    df = load_products_csv()
    print(f"📊 Total products: {len(df)}")
    
    # Check enhanced products
    enhanced = df[df['llm_fallback_used'] == True]
    print(f"📈 Enhanced products: {len(enhanced)}")
    
    # Expected Android fields (from CsvParser.kt)
    expected_fields = [
        'id', 'product_name', 'brand', 'category', 'subcategory', 
        'size_value', 'size_unit', 'price', 'source', 'source_url',
        'ingredients', 'nutrition_data', 'image_url', 'last_updated',
        'search_count', 'llm_fallback_used', 'data_quality_score'
    ]
    
    # Check CSV structure
    print(f"\n📋 CSV STRUCTURE CHECK:")
    csv_columns = df.columns.tolist()
    print(f"✅ Total columns: {len(csv_columns)}")
    
    # Check if all expected fields exist
    missing_fields = []
    for field in expected_fields:
        if field not in csv_columns:
            missing_fields.append(field)
    
    if missing_fields:
        print(f"❌ Missing fields: {missing_fields}")
    else:
        print(f"✅ All expected fields present")
    
    # Check nutrition JSON format
    print(f"\n🧪 NUTRITION JSON FORMAT CHECK:")
    
    # Expected nutrition fields (from Android CsvParser.kt)
    expected_nutrition_fields = [
        'energy_kcal', 'fat_g', 'saturated_fat_g', 'carbs_g', 
        'sugars_g', 'protein_g', 'salt_g', 'fiber_g', 'sodium_mg'
    ]
    
    valid_json_count = 0
    invalid_json_count = 0
    empty_json_count = 0
    
    # Sample check on enhanced products
    sample_size = min(100, len(enhanced))
    sample_products = enhanced.head(sample_size)
    
    for idx, row in sample_products.iterrows():
        nutrition_data = row['nutrition_data']
        
        if pd.isna(nutrition_data) or nutrition_data.strip() == '':
            empty_json_count += 1
            continue
            
        try:
            nutrition_json = json.loads(nutrition_data)
            
            # Check if it's flat format (not nested)
            if 'per_100g' in nutrition_json:
                print(f"❌ Found nested format in product: {row['product_name'][:40]}")
                invalid_json_count += 1
                continue
            
            # Check if expected fields are present
            has_nutrition_data = False
            for field in expected_nutrition_fields:
                if field in nutrition_json and nutrition_json[field] is not None:
                    has_nutrition_data = True
                    break
            
            if has_nutrition_data:
                valid_json_count += 1
            else:
                empty_json_count += 1
                
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in product: {row['product_name'][:40]}")
            invalid_json_count += 1
    
    print(f"✅ Valid JSON format: {valid_json_count}/{sample_size}")
    print(f"⚠️  Empty nutrition data: {empty_json_count}/{sample_size}")
    print(f"❌ Invalid JSON format: {invalid_json_count}/{sample_size}")
    
    # Show sample JSON
    if valid_json_count > 0:
        print(f"\n📄 SAMPLE NUTRITION JSON:")
        sample_product = enhanced[enhanced['nutrition_data'].notna()].iloc[0]
        sample_json = json.loads(sample_product['nutrition_data'])
        print(f"Product: {sample_product['product_name'][:50]}")
        print(f"JSON: {json.dumps(sample_json, indent=2)}")
    
    # Final assessment
    print(f"\n🎯 COMPATIBILITY ASSESSMENT:")
    
    compatibility_score = 0
    total_checks = 4
    
    # Check 1: All expected fields present
    if not missing_fields:
        compatibility_score += 1
        print("✅ CSV structure: Compatible")
    else:
        print("❌ CSV structure: Missing fields")
    
    # Check 2: Valid JSON format
    if invalid_json_count == 0:
        compatibility_score += 1
        print("✅ JSON format: Compatible")
    else:
        print("❌ JSON format: Has nested/invalid JSON")
    
    # Check 3: Nutrition data availability
    if valid_json_count > sample_size * 0.8:  # 80% threshold
        compatibility_score += 1
        print("✅ Nutrition data: Good coverage")
    else:
        print("⚠️ Nutrition data: Low coverage")
    
    # Check 4: Enhanced products count
    if len(enhanced) > 1000:
        compatibility_score += 1
        print("✅ Data volume: Sufficient for app")
    else:
        print("⚠️ Data volume: Limited")
    
    print(f"\n🏆 OVERALL COMPATIBILITY: {compatibility_score}/{total_checks}")
    
    if compatibility_score == total_checks:
        print("🎉 FULLY COMPATIBLE - Android app ready for deployment!")
    elif compatibility_score >= 3:
        print("✅ MOSTLY COMPATIBLE - Minor issues may exist")
    else:
        print("❌ COMPATIBILITY ISSUES - Requires fixes before deployment")
    
    return compatibility_score == total_checks

if __name__ == "__main__":
    verify_android_compatibility()