#!/usr/bin/env python3
"""
Run production classification using Qwen2.5 Instruct model
Process all products with long names and update the database
"""

import sys
import os
import time
import pandas as pd
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__)))
from product_classifier import ProductClassifier

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from csv_handler import load_products_csv, save_products_csv


def run_production_classification(min_name_length=80, batch_size=100, delay_seconds=1):
    """
    Run production classification on all products with long names
    
    Args:
        min_name_length: Minimum product name length to process
        batch_size: Number of products to process before saving checkpoint
        delay_seconds: Delay between API calls to avoid overload
    """
    
    print("=" * 80)
    print("PRODUCTION LLM PRODUCT CLASSIFICATION")
    print("=" * 80)
    print()
    
    # Load data
    df = load_products_csv()
    print(f"✅ Loaded {len(df):,} total products")
    
    # Filter for long names
    df['name_length'] = df['product_name'].str.len()
    long_names = df[df['name_length'] >= min_name_length].copy()
    print(f"✅ Found {len(long_names):,} products with names >= {min_name_length} characters")
    print()
    
    # Initialize classifier
    try:
        classifier = ProductClassifier()
        print("✅ Classifier initialized with Qwen2.5 Instruct")
    except Exception as e:
        print(f"❌ Failed to initialize classifier: {e}")
        return False
    
    print()
    print(f"🚀 Starting production run...")
    print(f"   - Processing {len(long_names):,} products")
    print(f"   - Batch size: {batch_size}")
    print(f"   - Delay between calls: {delay_seconds}s")
    print()
    
    # Track progress
    processed = 0
    updated = 0
    errors = 0
    start_time = time.time()
    
    # Process products
    for idx, row in long_names.iterrows():
        try:
            processed += 1
            
            # Show progress every 10 products
            if processed % 10 == 0:
                elapsed = time.time() - start_time
                rate = processed / elapsed if elapsed > 0 else 0
                remaining = len(long_names) - processed
                eta_seconds = remaining / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                
                print(f"Progress: {processed}/{len(long_names)} ({processed/len(long_names)*100:.1f}%) | "
                      f"Rate: {rate:.1f} products/sec | ETA: {eta_minutes:.1f} min")
            
            # Classify product
            result = classifier.process_product(row)
            
            # Update if we got a clean name
            if result.get('clean_product_name') and result['clean_product_name'] != row['product_name']:
                df.at[idx, 'product_name'] = result['clean_product_name']
                updated += 1
            
            # Update subcategory if changed
            if result.get('new_subcategory') and result['new_subcategory'] != row['subcategory']:
                df.at[idx, 'subcategory'] = result['new_subcategory']
            
            # Add delay to prevent overload
            time.sleep(delay_seconds)
            
            # Save checkpoint every batch_size products
            if processed % batch_size == 0:
                print(f"\n💾 Saving checkpoint at {processed} products...")
                save_products_csv(df)
                print(f"✅ Checkpoint saved\n")
        
        except Exception as e:
            errors += 1
            print(f"❌ Error processing product {idx}: {e}")
            continue
    
    # Final save
    print(f"\n💾 Saving final results...")
    save_products_csv(df)
    
    # Summary
    elapsed = time.time() - start_time
    print()
    print("=" * 80)
    print("PRODUCTION RUN COMPLETE")
    print("=" * 80)
    print(f"Total Processed: {processed:,}")
    print(f"Products Updated: {updated:,} ({updated/processed*100:.1f}%)")
    print(f"Errors: {errors}")
    print(f"Time Elapsed: {elapsed/60:.1f} minutes")
    print(f"Average Rate: {processed/elapsed:.1f} products/second")
    print()
    print(f"✅ Updated products saved to data/products.csv")
    print("=" * 80)
    
    return True


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Run production LLM classification')
    parser.add_argument('--min-length', type=int, default=80, 
                       help='Minimum product name length to process (default: 80)')
    parser.add_argument('--batch-size', type=int, default=100,
                       help='Checkpoint save frequency (default: 100)')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between API calls in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    print(f"\n⚠️  WARNING: This will process and update product names in the database!")
    print(f"   - Products to process: ~4,694 (names >= {args.min_length} chars)")
    print(f"   - Estimated time: ~1-2 hours")
    print()
    
    response = input("Do you want to continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("❌ Aborted by user")
        sys.exit(0)
    
    print()
    success = run_production_classification(
        min_name_length=args.min_length,
        batch_size=args.batch_size,
        delay_seconds=args.delay
    )
    
    if not success:
        print("❌ Production run failed")
        sys.exit(1)
