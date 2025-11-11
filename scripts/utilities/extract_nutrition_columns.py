#!/usr/bin/env python3
"""
Extract Nutrition Data from JSON to Individual Columns
Converts nutrition_data JSON field to individual CSV columns for Android app compatibility
"""

import pandas as pd
import json
import sys
import os

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from csv_handler import load_products_csv, save_products_csv

def extract_nutrition_to_columns():
    """
    Extract nutrition data from JSON nutrition_data field to individual columns
    """
    print("🔄 EXTRACTING NUTRITION DATA TO INDIVIDUAL COLUMNS")
    print("=" * 60)
    
    # Load the database
    df = load_products_csv()
    print(f"📊 Total products: {len(df)}")
    
    # Find products with nutrition_data
    with_nutrition_data = df[df['nutrition_data'].notna() & (df['nutrition_data'] != '')]
    print(f"📊 Products with nutrition_data: {len(with_nutrition_data)}")
    
    extracted_count = 0
    
    for idx, row in with_nutrition_data.iterrows():
        try:
            # Parse the JSON nutrition data
            nutrition_data = json.loads(row['nutrition_data'])
            per_100g = nutrition_data.get('per_100g', {})
            
            # Extract nutrition values to individual columns
            df.at[idx, 'energy_kcal_per_100g'] = per_100g.get('energy_kcal', '')
            df.at[idx, 'carbs_g_per_100g'] = per_100g.get('carbs_g', '')
            df.at[idx, 'protein_g_per_100g'] = per_100g.get('protein_g', '')
            df.at[idx, 'fat_g_per_100g'] = per_100g.get('fat_g', '')
            
            # Add additional nutrition columns if they don't exist
            if 'total_sugars_g_per_100g' not in df.columns:
                df['total_sugars_g_per_100g'] = ''
            if 'saturated_fat_g_per_100g' not in df.columns:
                df['saturated_fat_g_per_100g'] = ''
            if 'fiber_g_per_100g' not in df.columns:
                df['fiber_g_per_100g'] = ''
            if 'sodium_mg_per_100g' not in df.columns:
                df['sodium_mg_per_100g'] = ''
            if 'salt_g_per_100g' not in df.columns:
                df['salt_g_per_100g'] = ''
                
            df.at[idx, 'total_sugars_g_per_100g'] = per_100g.get('total_sugars_g', '')
            df.at[idx, 'saturated_fat_g_per_100g'] = per_100g.get('saturated_fat_g', '')
            df.at[idx, 'fiber_g_per_100g'] = per_100g.get('fiber_g', '')
            df.at[idx, 'sodium_mg_per_100g'] = per_100g.get('sodium_mg', '')
            df.at[idx, 'salt_g_per_100g'] = per_100g.get('salt_g', '')
            
            extracted_count += 1
            
            if extracted_count % 100 == 0:
                print(f"✅ Processed {extracted_count} products...")
                
        except Exception as e:
            print(f"❌ Error processing {row['product_name']}: {str(e)}")
            continue
    
    # Save the updated database
    save_products_csv(df)
    
    print(f"\n🎉 EXTRACTION COMPLETE!")
    print(f"✅ Successfully extracted nutrition data for {extracted_count} products")
    print(f"📊 Individual nutrition columns now populated")
    
    # Verify the extraction
    print(f"\n🔍 VERIFICATION:")
    energy_populated = len(df[df['energy_kcal_per_100g'].notna() & (df['energy_kcal_per_100g'] != '')])
    carbs_populated = len(df[df['carbs_g_per_100g'].notna() & (df['carbs_g_per_100g'] != '')])
    protein_populated = len(df[df['protein_g_per_100g'].notna() & (df['protein_g_per_100g'] != '')])
    
    print(f"Products with energy data: {energy_populated}")
    print(f"Products with carbs data: {carbs_populated}")
    print(f"Products with protein data: {protein_populated}")
    
    return extracted_count

if __name__ == "__main__":
    extract_nutrition_to_columns()