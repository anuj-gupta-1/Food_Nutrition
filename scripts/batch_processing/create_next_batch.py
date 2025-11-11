#!/usr/bin/env python3
"""
Create next batch excluding already enhanced products - ALL CATEGORIES
"""

import pandas as pd
import sys
import os
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from csv_handler import load_products_csv

def create_next_batch(batch_size=200, categories=None):
    """Create batch excluding enhanced products from all or specified categories"""
    
    # Load products
    df = load_products_csv()
    
    # Filter by categories if specified, otherwise use all
    if categories:
        if isinstance(categories, str):
            categories = [categories]
        products = df[df['category'].isin(categories)].copy()
        category_label = "_".join(categories)
    else:
        products = df.copy()
        category_label = "all_categories"
    
    # Filter out enhanced products (those with llm_fallback_used = True)
    unenhanced = products[
        (products['llm_fallback_used'] != True) & 
        (products['llm_fallback_used'].isna() | (products['llm_fallback_used'] == False))
    ].copy()
    
    print(f"Total products in selected categories: {len(products)}")
    print(f"Unenhanced available: {len(unenhanced)}")
    
    if len(unenhanced) < batch_size:
        print(f"⚠️ Only {len(unenhanced)} products available, creating smaller batch")
        batch_size = len(unenhanced)
    
    # Select batch with variety across categories
    if len(unenhanced) > 0:
        # Use timestamp-based random state to ensure different products each time
        import time
        random_state = int(time.time()) % 10000
        batch = unenhanced.sample(n=min(batch_size, len(unenhanced)), random_state=random_state)
        print(f"🎲 Using random state: {random_state} for variety")
    else:
        batch = unenhanced.head(batch_size)
    
    # Create batch data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    batch_id = f"{category_label}_{batch_size}products_{timestamp}"
    
    batch_data = []
    for i, (_, row) in enumerate(batch.iterrows(), 1):
        batch_data.append({
            'batch_id': i,
            'original_product_id': row['id'],
            'product_name': row['product_name'],
            'brand': row['brand'],
            'category': row['category'],
            'subcategory': row['subcategory'],
            'size_value': row['size_value'],
            'size_unit': row['size_unit'],
            'price': row['price'],
            'source': row['source']
        })
    
    # Save files
    input_file = f"llm_batches/input/input_{batch_id}.csv"
    output_file = f"llm_batches/output/output_{batch_id}.csv"
    
    pd.DataFrame(batch_data).to_csv(input_file, index=False)
    pd.DataFrame(batch_data).to_csv(output_file, index=False)
    
    print(f"✅ Created batch: {batch_id}")
    print(f"📥 Input: {input_file}")
    print(f"📤 Output: {output_file}")
    print(f"📊 Products: {len(batch_data)}")
    
    # Show category breakdown
    if len(batch_data) > 0:
        category_counts = batch.groupby('category').size()
        print(f"\n📋 Category breakdown:")
        for cat, count in category_counts.items():
            print(f"   {cat}: {count} products")
    
    return batch_id

def get_category_stats():
    """Get statistics for all categories"""
    df = load_products_csv()
    
    # Enhanced vs unenhanced by category
    stats = {}
    for category in df['category'].unique():
        if pd.isna(category):
            continue
            
        cat_products = df[df['category'] == category]
        enhanced = cat_products[cat_products['llm_fallback_used'] == True]
        
        stats[category] = {
            'total': len(cat_products),
            'enhanced': len(enhanced),
            'unenhanced': len(cat_products) - len(enhanced),
            'enhancement_rate': (len(enhanced) / len(cat_products) * 100) if len(cat_products) > 0 else 0
        }
    
    return stats

if __name__ == "__main__":
    # Show current stats
    print("📊 Current Enhancement Status by Category:")
    stats = get_category_stats()
    for category, data in stats.items():
        print(f"   {category}: {data['enhanced']}/{data['total']} ({data['enhancement_rate']:.1f}%)")
    
    print("\n" + "="*50)
    
    # Check for command line argument for batch size
    import sys
    batch_size = 200  # Default to 200 for production batches
    if len(sys.argv) > 1:
        try:
            batch_size = int(sys.argv[1])
        except:
            pass
    
    create_next_batch(batch_size=batch_size)