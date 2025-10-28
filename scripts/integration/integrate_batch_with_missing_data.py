#!/usr/bin/env python3
"""
Integrate Batch with Missing Data Handling
Handles products with incomplete data appropriately
"""

import pandas as pd
import json
from datetime import datetime
from csv_handler import load_products_csv, save_products_csv, get_beverage_stats

def integrate_batch_with_missing_data(csv_file, min_confidence=0.6):
    """Integrate batch handling missing data appropriately"""
    
    print("🔄 INTEGRATING BATCH WITH SMART MISSING DATA HANDLING")
    print("=" * 60)
    print(f"📁 Processing: {csv_file}")
    
    # Load the CSV
    try:
        df_batch = pd.read_csv(csv_file)
    except Exception as e:
        print(f"❌ Cannot read CSV file: {e}")
        return False
    
    print(f"📊 Batch Analysis:")
    print(f"   Total rows: {len(df_batch)}")
    
    # Analyze data completeness
    df_batch['confidence_numeric'] = pd.to_numeric(df_batch['confidence_score'], errors='coerce')
    
    # Categorize products by data availability
    complete_data = df_batch[df_batch['confidence_numeric'] >= min_confidence]
    incomplete_data = df_batch[(df_batch['confidence_numeric'] < min_confidence) | (df_batch['confidence_numeric'].isna())]
    no_data_available = df_batch[df_batch['processing_notes'].str.contains('No data available', na=False)]
    
    print(f"   Complete data (≥{min_confidence}): {len(complete_data)}")
    print(f"   Incomplete data (<{min_confidence}): {len(incomplete_data)}")
    print(f"   No data available: {len(no_data_available)}")
    
    if len(complete_data) == 0:
        print("❌ No products with sufficient data quality to integrate")
        return False
    
    # Load main database
    df_main = load_products_csv()
    current_stats = get_beverage_stats()
    
    print(f"\n📊 Current Database Status:")
    print(f"   Enhanced beverages: {current_stats['enhanced_beverages']}")
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"data/products_backup_batch2_{timestamp}.csv"
    save_products_csv(df_main, backup_file)
    print(f"💾 Backup created: {backup_file}")
    
    # Integration process
    integration_stats = {
        'processed': 0,
        'integrated': 0,
        'skipped_not_found': 0,
        'skipped_already_enhanced': 0,
        'skipped_low_confidence': 0,
        'skipped_no_data': 0,
        'total_confidence': 0
    }
    
    print(f"\n🔄 Processing all {len(df_batch)} products...")
    
    for _, row in df_batch.iterrows():
        integration_stats['processed'] += 1
        
        # Find product in main database
        product_id = row['product_id']
        product_matches = df_main[df_main['id'] == product_id]
        
        if len(product_matches) == 0:
            integration_stats['skipped_not_found'] += 1
            print(f"⏭️  Product not found: {product_id}")
            continue
        
        product_idx = product_matches.index[0]
        
        # Check if already enhanced
        if df_main.at[product_idx, 'llm_fallback_used'] == True:
            integration_stats['skipped_already_enhanced'] += 1
            print(f"⏭️  Already enhanced: {row['product_name'][:40]}")
            continue
        
        # Handle missing data cases
        confidence = row.get('confidence_numeric', 0)
        if pd.isna(confidence):
            confidence = 0
        
        # Skip products with no data available
        if 'No data available' in str(row.get('processing_notes', '')):
            integration_stats['skipped_no_data'] += 1
            print(f"📋 No data available: {row['product_name'][:40]}")
            continue
        
        # Skip low confidence products
        if confidence < min_confidence:
            integration_stats['skipped_low_confidence'] += 1
            print(f"⚠️  Low confidence ({confidence:.2f}): {row['product_name'][:40]}")
            continue
        
        # Integrate high-quality products
        try:
            # Create nutrition data structure with safe handling
            nutrition_data = {
                "per_100g": {
                    "energy_kcal": safe_numeric(row.get('energy_kcal_per_100g')),
                    "carbs_g": safe_numeric(row.get('carbs_g_per_100g')),
                    "total_sugars_g": safe_numeric(row.get('total_sugars_g_per_100g')),
                    "protein_g": safe_numeric(row.get('protein_g_per_100g')),
                    "fat_g": safe_numeric(row.get('fat_g_per_100g')),
                    "saturated_fat_g": safe_numeric(row.get('saturated_fat_g_per_100g')),
                    "fiber_g": safe_numeric(row.get('fiber_g_per_100g')),
                    "sodium_mg": safe_numeric(row.get('sodium_mg_per_100g')),
                    "salt_g": safe_numeric(row.get('salt_g_per_100g'))
                },
                "serving_info": {
                    "manufacturer_serving_size": str(row.get('serving_size', '')),
                    "servings_per_container": safe_numeric(row.get('servings_per_container'))
                },
                "confidence_scores": {
                    "overall_confidence": float(confidence),
                    "data_source": str(row.get('data_source', 'external_batch')),
                    "processing_notes": str(row.get('processing_notes', ''))
                }
            }
            
            # Create ingredients data with safe handling
            ingredients_raw = str(row.get('ingredients_list', ''))
            if ingredients_raw and ingredients_raw != 'nan' and ingredients_raw.strip():
                ingredients_list = [ing.strip() for ing in ingredients_raw.split(',') if ing.strip()]
            else:
                ingredients_list = []
            
            ingredients_data = {
                "ingredients_list": ingredients_list,
                "preparation_metadata": {
                    "manufacturer_serving_size": str(row.get('serving_size', '')),
                    "preparation_method": "Ready to drink",
                    "processed_by": "external_llm_batch2"
                }
            }
            
            # Update main database
            df_main.at[product_idx, 'llm_fallback_used'] = True
            df_main.at[product_idx, 'ingredients'] = json.dumps(ingredients_data)
            df_main.at[product_idx, 'nutrition_data'] = json.dumps(nutrition_data)
            df_main.at[product_idx, 'llm_confidence'] = float(confidence)
            df_main.at[product_idx, 'llm_provider'] = 'external_llm_batch2'
            df_main.at[product_idx, 'llm_response_time'] = 0
            
            # Quality score boost
            confidence_boost = int(float(confidence) * 25)
            source_boost = 5 if 'official' in str(row.get('data_source', '')).lower() else 0
            
            current_score = int(df_main.at[product_idx, 'data_quality_score'] or 90)
            new_score = min(100, current_score + confidence_boost + source_boost)
            df_main.at[product_idx, 'data_quality_score'] = new_score
            
            integration_stats['integrated'] += 1
            integration_stats['total_confidence'] += float(confidence)
            
            print(f"✅ {row['product_name'][:50]:<50} (conf: {confidence:.2f})")
            
        except Exception as e:
            print(f"❌ Error integrating {row['product_name'][:40]}: {str(e)[:50]}")
            continue
    
    # Save updated database
    save_products_csv(df_main)
    
    # Results summary
    final_stats = get_beverage_stats()
    avg_confidence = integration_stats['total_confidence'] / integration_stats['integrated'] if integration_stats['integrated'] > 0 else 0
    improvement = final_stats['enhanced_beverages'] - current_stats['enhanced_beverages']
    
    print(f"\n🎉 BATCH 2 INTEGRATION COMPLETE!")
    print("=" * 60)
    print(f"📊 Integration Results:")
    print(f"   Total processed: {integration_stats['processed']} products")
    print(f"   Successfully integrated: {integration_stats['integrated']} products")
    print(f"   Average confidence: {avg_confidence:.2f}")
    
    print(f"\n📋 Skipped Products Breakdown:")
    print(f"   No data available: {integration_stats['skipped_no_data']} products")
    print(f"   Low confidence (<{min_confidence}): {integration_stats['skipped_low_confidence']} products")
    print(f"   Already enhanced: {integration_stats['skipped_already_enhanced']} products")
    print(f"   Not found in database: {integration_stats['skipped_not_found']} products")
    
    print(f"\n📈 Database Impact:")
    print(f"   Before: {current_stats['enhanced_beverages']} enhanced beverages")
    print(f"   After: {final_stats['enhanced_beverages']} enhanced beverages")
    print(f"   Improvement: +{improvement} products")
    print(f"   New coverage: {final_stats['enhancement_rate']:.1f}%")
    
    # Success assessment
    success_rate = integration_stats['integrated'] / integration_stats['processed'] * 100
    
    print(f"\n🎯 Quality Assessment:")
    if improvement >= 30:
        print(f"🏆 EXCELLENT! Added {improvement} high-quality products!")
    elif improvement >= 20:
        print(f"🥇 GREAT! Added {improvement} products!")
    elif improvement >= 10:
        print(f"✅ GOOD! Added {improvement} products!")
    else:
        print(f"📈 PROGRESS! Added {improvement} products!")
    
    print(f"📊 Processing efficiency: {success_rate:.1f}%")
    
    if avg_confidence >= 0.8:
        print(f"🎯 HIGH QUALITY: Excellent confidence scores!")
    elif avg_confidence >= 0.7:
        print(f"✅ GOOD QUALITY: Solid confidence scores!")
    
    # Show what was skipped for transparency
    if integration_stats['skipped_no_data'] > 0:
        print(f"\n💡 Note: {integration_stats['skipped_no_data']} products had no available data")
        print(f"   This is normal for specialized categories like tea/coffee")
    
    return True

def safe_numeric(value):
    """Safely convert value to numeric"""
    if pd.isna(value) or value == '' or value == 'nan' or str(value).strip() == '':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

if __name__ == "__main__":
    # Integrate the latest batch
    csv_file = "llm_batches/output/output_beverages_100products_20251028_1134.csv"
    integrate_batch_with_missing_data(csv_file, min_confidence=0.6)