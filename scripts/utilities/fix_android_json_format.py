#!/usr/bin/env python3
"""
Fix Android JSON Format - Convert nested nutrition JSON to flat format
This script converts the current nested JSON format to the flat format expected by Android app
"""

import pandas as pd
import json
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from csv_handler import load_products_csv, save_products_csv

def flatten_nutrition_json(nutrition_data_str):
    """
    Convert nested nutrition JSON to flat format for Android compatibility
    
    From: {"per_100g": {"energy_kcal": 550.0, ...}, "serving_info": {...}}
    To: {"energy_kcal": 550.0, "fat_g": 34.0, ...}
    """
    if not nutrition_data_str or nutrition_data_str.strip() == '':
        return '{"energy_kcal": null, "fat_g": null, "saturated_fat_g": null, "carbs_g": null, "sugars_g": null, "protein_g": null, "salt_g": null, "fiber_g": null, "sodium_mg": null}'
    
    try:
        # Parse the current nested JSON
        data = json.loads(nutrition_data_str)
        
        # Extract per_100g data if it exists
        if 'per_100g' in data and isinstance(data['per_100g'], dict):
            per_100g = data['per_100g']
        else:
            # If already flat, return as is
            per_100g = data
        
        # Create flat JSON with expected fields
        flat_json = {
            "energy_kcal": per_100g.get('energy_kcal'),
            "fat_g": per_100g.get('fat_g'),
            "saturated_fat_g": per_100g.get('saturated_fat_g'),
            "carbs_g": per_100g.get('carbs_g'),
            "sugars_g": per_100g.get('total_sugars_g') or per_100g.get('sugars_g'),  # Handle both field names
            "protein_g": per_100g.get('protein_g'),
            "salt_g": per_100g.get('salt_g'),
            "fiber_g": per_100g.get('fiber_g'),
            "sodium_mg": per_100g.get('sodium_mg')
        }
        
        return json.dumps(flat_json)
        
    except (json.JSONDecodeError, TypeError, AttributeError) as e:
        print(f"Warning: Could not parse nutrition JSON: {e}")
        # Return default null structure
        return '{"energy_kcal": null, "fat_g": null, "saturated_fat_g": null, "carbs_g": null, "sugars_g": null, "protein_g": null, "salt_g": null, "fiber_g": null, "sodium_mg": null}'

def fix_android_json_format():
    """Fix the JSON format for Android compatibility"""
    
    print("🔧 FIXING ANDROID JSON FORMAT")
    print("=" * 50)
    
    # Load current database
    df = load_products_csv()
    print(f"📊 Loaded {len(df)} products")
    
    # Create backup
    backup_file = f"data/products_backup_android_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    save_products_csv(df, backup_file)
    print(f"💾 Backup created: {backup_file}")
    
    # Count products that need fixing
    enhanced_products = df[df['llm_fallback_used'] == True]
    print(f"📈 Found {len(enhanced_products)} enhanced products to fix")
    
    # Fix nutrition_data JSON format
    fixed_count = 0
    for idx, row in enhanced_products.iterrows():
        if pd.notna(row['nutrition_data']) and row['nutrition_data'].strip():
            try:
                # Convert to flat format
                flat_json = flatten_nutrition_json(row['nutrition_data'])
                df.at[idx, 'nutrition_data'] = flat_json
                fixed_count += 1
                
                if fixed_count % 100 == 0:
                    print(f"✅ Fixed {fixed_count} products...")
                    
            except Exception as e:
                print(f"❌ Error fixing product {row['product_name'][:50]}: {e}")
                continue
    
    # Also fix products with empty nutrition_data but individual columns populated
    individual_columns = ['energy_kcal_per_100g', 'carbs_g_per_100g', 'protein_g_per_100g', 
                         'fat_g_per_100g', 'total_sugars_g_per_100g', 'saturated_fat_g_per_100g', 
                         'fiber_g_per_100g', 'sodium_mg_per_100g', 'salt_g_per_100g']
    
    # Find products with individual columns but empty JSON
    needs_json_creation = df[
        (df['nutrition_data'].isna() | (df['nutrition_data'] == '') | 
         (df['nutrition_data'] == '{"energy_kcal": null, "fat_g": null, "saturated_fat_g": null, "carbs_g": null, "sugars_g": null, "protein_g": null, "salt_g": null, "fiber_g": null, "sodium_mg": null}')) &
        (df[individual_columns].notna().any(axis=1))
    ]
    
    print(f"📋 Found {len(needs_json_creation)} products with individual columns but empty JSON")
    
    for idx, row in needs_json_creation.iterrows():
        # Create JSON from individual columns
        flat_json = {
            "energy_kcal": row.get('energy_kcal_per_100g'),
            "fat_g": row.get('fat_g_per_100g'),
            "saturated_fat_g": row.get('saturated_fat_g_per_100g'),
            "carbs_g": row.get('carbs_g_per_100g'),
            "sugars_g": row.get('total_sugars_g_per_100g'),
            "protein_g": row.get('protein_g_per_100g'),
            "salt_g": row.get('salt_g_per_100g'),
            "fiber_g": row.get('fiber_g_per_100g'),
            "sodium_mg": row.get('sodium_mg_per_100g')
        }
        
        # Only create JSON if at least one value is not null
        if any(v is not None and pd.notna(v) for v in flat_json.values()):
            df.at[idx, 'nutrition_data'] = json.dumps(flat_json)
            fixed_count += 1
    
    # Save the fixed database
    save_products_csv(df)
    
    print(f"\n🎉 ANDROID JSON FORMAT FIX COMPLETE!")
    print("=" * 50)
    print(f"✅ Fixed {fixed_count} products")
    print(f"📱 Android app can now properly parse nutrition data")
    print(f"💾 Original data backed up to: {backup_file}")
    
    # Verify the fix
    print(f"\n🔍 VERIFICATION:")
    sample_enhanced = df[df['llm_fallback_used'] == True].head(3)
    for idx, row in sample_enhanced.iterrows():
        print(f"Product: {row['product_name'][:40]}")
        try:
            nutrition_json = json.loads(row['nutrition_data'])
            has_data = any(v is not None for v in nutrition_json.values())
            print(f"  JSON format: {'✅ Valid' if has_data else '⚠️ Empty'}")
            print(f"  Sample: energy_kcal={nutrition_json.get('energy_kcal')}, protein_g={nutrition_json.get('protein_g')}")
        except:
            print(f"  JSON format: ❌ Invalid")
        print()

if __name__ == "__main__":
    fix_android_json_format()