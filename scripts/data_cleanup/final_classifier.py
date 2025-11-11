#!/usr/bin/env python3
"""
Final Product Classifier with Improved LLM Service
Addresses all feedback and includes processing flags
"""

import pandas as pd
import sys
import os
import time
from typing import Dict

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from csv_handler import load_products_csv, save_products_csv
from improved_llm_service import ImprovedLLMClassificationService


class FinalProductClassifier:
    """Final product classifier with all improvements"""
    
    def __init__(self):
        self.llm_service = ImprovedLLMClassificationService()
        
        # Test connection
        if not self.llm_service.test_connection():
            raise Exception("Cannot connect to Ollama. Make sure it's running with: ollama serve")
    
    def process_product(self, row: pd.Series) -> Dict:
        """Process a single product using improved Llama service"""
        
        product_name = str(row.get('product_name', ''))
        current_category = str(row.get('category', ''))
        current_subcategory = str(row.get('subcategory', ''))
        brand = str(row.get('brand', ''))
        
        print(f"  -> Processing: {product_name[:60]}...")
        
        # Use improved LLM service
        result = self.llm_service.classify_product(
            product_name, 
            current_category, 
            current_subcategory,
            brand
        )
        
        # Add original data for reference
        result['original_id'] = row.get('id', '')
        result['original_name'] = product_name
        result['original_category'] = current_category
        result['original_subcategory'] = current_subcategory
        result['original_brand'] = brand
        
        return result


def run_final_trial(batch_size=10, min_name_length=80):
    """Run final trial with improved service"""
    
    print("=" * 80)
    print("FINAL IMPROVED LLAMA CLASSIFICATION - TRIAL RUN")
    print("=" * 80)
    print()
    
    # Load data
    df = load_products_csv()
    print(f"✅ Loaded {len(df):,} products")
    
    # Filter for long names
    df['name_length'] = df['product_name'].str.len()
    long_names = df[df['name_length'] >= min_name_length].copy()
    print(f"✅ Found {len(long_names):,} products with names >= {min_name_length} characters")
    
    # Sample products (same seed for consistency)
    sample = long_names.sample(n=min(batch_size, len(long_names)), random_state=42)
    print(f"✅ Processing {len(sample)} products for final trial")
    print()
    
    # Initialize classifier
    try:
        classifier = FinalProductClassifier()
    except Exception as e:
        print(f"❌ Failed to initialize classifier: {e}")
        return None, None, None, None
    
    # Process products
    results = []
    for idx, row in sample.iterrows():
        result = classifier.process_product(row)
        results.append(result)
        
        # Add delay
        time.sleep(1)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Categorize by confidence and flags
    high_conf = results_df[results_df['confidence_score'] >= 0.7]
    medium_conf = results_df[(results_df['confidence_score'] >= 0.5) & 
                             (results_df['confidence_score'] < 0.7)]
    low_conf = results_df[results_df['confidence_score'] < 0.5]
    
    auto_accept = results_df[results_df['auto_accept'] == True]
    processed = results_df[results_df['processed_for_cleanup'] == True]
    
    print("\n" + "=" * 80)
    print("FINAL IMPROVED TRIAL SUMMARY")
    print("=" * 80)
    print(f"Total Processed: {len(results_df)}")
    print(f"High Confidence (>= 0.7): {len(high_conf)} ({len(high_conf)/len(results_df)*100:.1f}%)")
    print(f"Medium Confidence (0.5-0.7): {len(medium_conf)} ({len(medium_conf)/len(results_df)*100:.1f}%)")
    print(f"Low Confidence (< 0.5): {len(low_conf)} ({len(low_conf)/len(results_df)*100:.1f}%)")
    print(f"Auto Accept (>= 0.8): {len(auto_accept)} ({len(auto_accept)/len(results_df)*100:.1f}%)")
    print(f"Successfully Processed: {len(processed)} ({len(processed)/len(results_df)*100:.1f}%)")
    print()
    
    return results_df, high_conf, medium_conf, low_conf


def display_final_results(results_df, high_conf, medium_conf, low_conf):
    """Display final results with all improvements"""
    
    print("\n" + "="*80)
    print("FINAL IMPROVED RESULTS")
    print("="*80)
    
    # Show a few examples from each category
    categories = [
        ("HIGH CONFIDENCE", high_conf, "✅"),
        ("MEDIUM CONFIDENCE", medium_conf, "⚠️"),
        ("LOW CONFIDENCE", low_conf, "❌")
    ]
    
    for cat_name, cat_df, emoji in categories:
        if len(cat_df) > 0:
            print(f"\n{emoji} {cat_name} EXAMPLES:")
            print("-" * 60)
            
            # Show first 3 examples
            for idx, (_, result) in enumerate(cat_df.head(3).iterrows(), 1):
                print(f"\n{idx}. {result['original_name'][:70]}...")
                print(f"   Clean Name: {result['clean_product_name']}")
                print(f"   Subcategory: {result['original_subcategory']} → {result['new_subcategory']}")
                print(f"   Confidence: {result['confidence_score']:.2f}")
                print(f"   Auto Accept: {result['auto_accept']}")
                print(f"   Processed: {result['processed_for_cleanup']}")
    
    # Summary stats
    avg_confidence = results_df['confidence_score'].mean()
    auto_accept_count = len(results_df[results_df['auto_accept'] == True])
    processed_count = len(results_df[results_df['processed_for_cleanup'] == True])
    
    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print(f"{'='*80}")
    print(f"Average Confidence: {avg_confidence:.2f}")
    print(f"Auto Accept Rate: {auto_accept_count}/{len(results_df)} ({auto_accept_count/len(results_df)*100:.1f}%)")
    print(f"Processing Success Rate: {processed_count}/{len(results_df)} ({processed_count/len(results_df)*100:.1f}%)")
    
    if avg_confidence >= 0.75:
        print("✅ Recommendation: Ready for production use")
    elif avg_confidence >= 0.65:
        print("⚠️  Recommendation: Good for trial, monitor results")
    else:
        print("❌ Recommendation: Needs more improvement")
    
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    print("Starting Final Improved Classification Trial...")
    print("This addresses all your feedback points...\n")
    
    results_df, high_conf, medium_conf, low_conf = run_final_trial(
        batch_size=10,
        min_name_length=80
    )
    
    if results_df is not None:
        display_final_results(results_df, high_conf, medium_conf, low_conf)
    else:
        print("❌ Trial run failed!")