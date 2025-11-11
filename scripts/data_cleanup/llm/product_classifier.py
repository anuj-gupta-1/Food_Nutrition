#!/usr/bin/env python3
"""
Product Classifier using Local Llama Service
Main classifier that uses the LLM classification service
"""

import pandas as pd
import sys
import os
import time
from typing import Dict

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from csv_handler import load_products_csv, save_products_csv
from category_manager import CategoryManager
from llm_classification_service import LLMClassificationService


class ProductClassifier:
    """Main product classifier using local Llama service"""
    
    def __init__(self):
        self.llm_service = LLMClassificationService()
        self.category_manager = CategoryManager()
        
        # Test connection
        if not self.llm_service.test_connection():
            raise Exception("Cannot connect to Ollama. Make sure it's running with: ollama serve")
    
    def get_subcategories_for_category(self, category: str) -> list:
        """Get valid subcategories for a given category using CategoryManager"""
        return self.category_manager.get_subcategories(category)
    
    def process_product(self, row: pd.Series) -> Dict:
        """Process a single product using Llama"""
        
        product_name = str(row.get('product_name', ''))
        current_category = str(row.get('category', ''))
        current_subcategory = str(row.get('subcategory', ''))
        brand = str(row.get('brand', ''))
        
        print(f"  -> Processing: {product_name[:60]}...")
        
        # Get valid subcategories for this category
        valid_subcategories = self.get_subcategories_for_category(current_category)
        
        # Use LLM for classification
        result = self.llm_service.classify_product(
            product_name, 
            current_category, 
            current_subcategory,
            brand,
            valid_subcategories
        )
        
        # Add original data for reference
        result['original_id'] = row.get('id', '')
        result['original_name'] = product_name
        result['original_category'] = current_category
        result['original_subcategory'] = current_subcategory
        result['original_brand'] = brand
        
        return result


def run_trial_classification(batch_size=10, min_name_length=80):
    """Run trial classification using local Llama on sample products"""
    
    print("=" * 80)
    print("LOCAL LLAMA PRODUCT CLASSIFICATION - TRIAL RUN")
    print("=" * 80)
    print()
    
    # Load data
    df = load_products_csv()
    print(f"✅ Loaded {len(df):,} products")
    
    # Filter for long names
    df['name_length'] = df['product_name'].str.len()
    long_names = df[df['name_length'] >= min_name_length].copy()
    print(f"✅ Found {len(long_names):,} products with names >= {min_name_length} characters")
    
    # Sample products (mixed categories) - use different seed for new test
    sample = long_names.sample(n=min(batch_size, len(long_names)), random_state=789)
    print(f"✅ Processing {len(sample)} products for Llama trial run")
    print()
    
    # Initialize classifier
    try:
        classifier = ProductClassifier()
    except Exception as e:
        print(f"❌ Failed to initialize classifier: {e}")
        return None, None, None, None
    
    # Process products
    results = []
    for idx, row in sample.iterrows():
        result = classifier.process_product(row)
        results.append(result)
        
        # Add delay to prevent overloading
        time.sleep(1)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Categorize by confidence
    high_conf = results_df[results_df['confidence_score'] >= 0.7]
    medium_conf = results_df[(results_df['confidence_score'] >= 0.5) & 
                             (results_df['confidence_score'] < 0.7)]
    low_conf = results_df[results_df['confidence_score'] < 0.5]
    
    print("\n" + "=" * 80)
    print("LOCAL LLAMA TRIAL RUN SUMMARY")
    print("=" * 80)
    print(f"Total Processed: {len(results_df)}")
    print(f"High Confidence (>= 0.7): {len(high_conf)} ({len(high_conf)/len(results_df)*100:.1f}%)")
    print(f"Medium Confidence (0.5-0.7): {len(medium_conf)} ({len(medium_conf)/len(results_df)*100:.1f}%)")
    print(f"Low Confidence (< 0.5): {len(low_conf)} ({len(low_conf)/len(results_df)*100:.1f}%)")
    print()
    
    return results_df, high_conf, medium_conf, low_conf


if __name__ == "__main__":
    results_df, high_conf, medium_conf, low_conf = run_trial_classification(
        batch_size=10,
        min_name_length=80
    )
    
    if results_df is not None:
        print("Local Llama trial run complete! Results ready for display.")
    else:
        print("Trial run failed!")