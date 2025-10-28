#!/usr/bin/env python3
"""
Create next batch excluding already enhanced products
"""

import pandas as pd
from datetime import datetime
from csv_handler import load_products_csv

def create_next_batch(batch_size=200):
    """Create batch excluding enhanced products"""
    
    # Load products
    df = load_products_csv()
    beverages = df[df['category'] == 'beverage'].copy()
    
    # Filter out enhanced products (those with confidence_score)
    unenhanced = beverages[
        (beverages['confidence_score'].isna()) | 
        (beverages['confidence_score'] == '') |
        (beverages['confidence_score'] == '0.0') |
        (beverages['confidence_score'] == 'nan')
    ].copy()
    
    print(f"Total beverages: {len(beverages)}")
    print(f"Unenhanced available: {len(unenhanced)}")
    
    if len(unenhanced) < batch_size:
        print(f"⚠️ Only {len(unenhanced)} products available, creating smaller batch")
        batch_size = len(unenhanced)
    
    # Select batch
    batch = unenhanced.head(batch_size)
    
    # Create batch data
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    batch_id = f"beverages_{batch_size}products_{timestamp}"
    
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
    
    return batch_id

if __name__ == "__main__":
    create_next_batch()