#!/usr/bin/env python3
"""
LLM-Based Product Classification and Name Parsing
Uses LLM for intelligent subcategory classification and clean name extraction
"""

import pandas as pd
import json
import sys
import os
import time
from typing import Dict, Tuple

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'external_services'))

from csv_handler import load_products_csv, save_products_csv
from llm_nutrition_service import LLMNutritionService


class LLMProductClassifier:
    """LLM-based product classification with structured subcategory mapping"""
    
    def __init__(self):
        self.llm_service = LLMNutritionService()
        self.setup_category_subcategory_mapping()
    
    def setup_category_subcategory_mapping(self):
        """Define valid subcategories for each category"""
        
        self.category_subcategories = {
            'essentials': [
                'flour', 'salt', 'sugar', 'dry-fruits-nuts', 'oil', 
                'rice', 'pulses', 'masala', 'wheat-soya'
            ],
            'snacks': [
                'breakfast', 'chips', 'namkeen', 'biscuit', 'bakery'
            ],
            'flavourings': [
                'pickles', 'chutney', 'sauce'
            ],
            'beverage': [
                'tea', 'coffee', 'juice', 'carbonated', 'energy-drinks', 
                'health-drinks', 'syrup', 'other-beverages'
            ],
            'spread': [
                'sauce-ketchup-butter', 'jam-honey', 'other-spreads'
            ],
            'noodles_pasta': [
                'noodles', 'pasta', 'instant-noodles'
            ],
            'chocolate': [
                'chocolate', 'candy'
            ],
            'ready_to_eat': [
                'ready-to-eat', 'instant-meals'
            ],
            'baby': [
                'baby-food', 'baby-snacks'
            ],
            'dairy': [
                'milk', 'curd', 'cheese', 'paneer', 'butter', 'yogurt', 'ghee'
            ],
            'bakery': [
                'cake', 'bread', 'pastry', 'cookies'
            ]
        }
    
    def get_subcategories_for_category(self, category: str) -> list:
        """Get valid subcategories for a given category"""
        return self.category_subcategories.get(category.lower(), [])
    
    def classify_product_with_llm(self, product_name: str, current_category: str, 
                                  current_subcategory: str, brand: str) -> Dict:
        """
        Use LLM to classify product and extract clean name
        Returns: dict with new_subcategory, clean_name, confidence, etc.
        """
        
        # Get valid subcategories for this category
        valid_subcategories = self.get_subcategories_for_category(current_category)
        subcategories_str = ', '.join(valid_subcategories)
        
        # Create simplified LLM prompt
        prompt = f"""Product: {product_name}
Category: {current_category}
Valid subcategories: {subcategories_str}

Task: Extract clean product name and classify subcategory.

Clean name rules:
- Keep core product and important descriptors (Organic, Low GI, Gluten Free)
- Remove sizes, packs, marketing text

Examples:
"Dhampur Green Organic Brown Sugar 800g" -> "Organic Brown Sugar"
"Gustora Healthy Macaroni & Mini Fusilli Pasta Combo Pack of 2" -> "Healthy Macaroni & Mini Fusilli Pasta"
"LILA DRY FRUITS 4 Superseed Combo (Chia, Pumpkin) 100gms" -> "4 Superseed Combo"

Response format:
new_subcategory: <pick from valid list>
clean_product_name: <cleaned name>
confidence_score: <0.0-1.0>

Answer:"""

        # Get LLM response using local Ollama
        try:
            import requests
            
            payload = {
                "model": "llama2:13b",  # Use the local model
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 200
                }
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=60  # Longer timeout for local model
            )
            
            if response.status_code == 200:
                content = response.json().get("response", "")
                print(f"  -> Got LLM response from Ollama")
                
                # Parse the response
                parsed = self.parse_classification_response(
                    content, 
                    valid_subcategories,
                    current_subcategory,
                    product_name
                )
                return parsed
            else:
                print(f"  -> Ollama API error: {response.status_code}")
                # Fallback to unchanged
                return {
                    'new_subcategory': current_subcategory,
                    'clean_product_name': product_name,
                    'confidence_score': 0.3,
                    'classification_method': 'llm_api_error',
                    'needs_manual_review': True,
                    'processing_notes': f'Ollama API error: {response.status_code}'
                }
                
        except Exception as e:
            print(f"  -> LLM classification error: {e}")
            return {
                'new_subcategory': current_subcategory,
                'clean_product_name': product_name,
                'confidence_score': 0.3,
                'classification_method': 'error',
                'needs_manual_review': True,
                'processing_notes': f'Error: {str(e)}'
            }
    
    def parse_classification_response(self, content: str, valid_subcategories: list,
                                     fallback_subcategory: str, fallback_name: str) -> Dict:
        """Parse LLM response and extract classification data"""
        
        try:
            # Try to extract field-value pairs
            import re
            
            new_subcategory = fallback_subcategory
            clean_name = fallback_name
            confidence = 0.5
            reasoning = ""
            
            # Extract new_subcategory
            subcat_match = re.search(r'new_subcategory:\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
            if subcat_match:
                extracted_subcat = subcat_match.group(1).strip()
                # Validate against valid subcategories
                if extracted_subcat in valid_subcategories:
                    new_subcategory = extracted_subcat
                    confidence = 0.8  # Boost confidence if valid subcategory found
            
            # Extract clean_product_name
            name_match = re.search(r'clean_product_name:\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
            if name_match:
                clean_name = name_match.group(1).strip()
                # Remove quotes if present
                clean_name = clean_name.strip('"\'')
            
            # Extract confidence_score
            conf_match = re.search(r'confidence_score:\s*([\d.]+)', content, re.IGNORECASE)
            if conf_match:
                confidence = float(conf_match.group(1))
            
            # Extract reasoning
            reason_match = re.search(r'classification_reasoning:\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
            if reason_match:
                reasoning = reason_match.group(1).strip()
            
            return {
                'new_subcategory': new_subcategory,
                'clean_product_name': clean_name,
                'confidence_score': confidence,
                'classification_method': 'llm_ollama',
                'needs_manual_review': confidence < 0.7,
                'processing_notes': reasoning if reasoning else 'LLM classification'
            }
            
        except Exception as e:
            print(f"  -> Error parsing LLM response: {e}")
            return {
                'new_subcategory': fallback_subcategory,
                'clean_product_name': fallback_name,
                'confidence_score': 0.3,
                'classification_method': 'parse_error',
                'needs_manual_review': True,
                'processing_notes': f'Parse error: {str(e)}'
            }
    
    def process_product(self, row: pd.Series) -> Dict:
        """Process a single product using LLM"""
        
        product_name = str(row.get('product_name', ''))
        current_category = str(row.get('category', ''))
        current_subcategory = str(row.get('subcategory', ''))
        brand = str(row.get('brand', ''))
        
        print(f"  -> Processing: {product_name[:60]}...")
        
        # Use LLM for classification
        result = self.classify_product_with_llm(
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


def run_llm_trial_classification(batch_size=10, min_name_length=80):
    """Run trial classification using LLM on sample products"""
    
    print("=" * 80)
    print("LLM-BASED PRODUCT CLASSIFICATION - TRIAL RUN")
    print("=" * 80)
    print()
    
    # Load data
    df = load_products_csv()
    print(f"[OK] Loaded {len(df):,} products")
    
    # Filter for long names
    df['name_length'] = df['product_name'].str.len()
    long_names = df[df['name_length'] >= min_name_length].copy()
    print(f"[OK] Found {len(long_names):,} products with names >= {min_name_length} characters")
    
    # Sample products (mixed categories) - use same seed for consistency
    sample = long_names.sample(n=min(batch_size, len(long_names)), random_state=42)
    print(f"[OK] Processing {len(sample)} products for LLM trial run")
    print()
    
    # Initialize classifier
    classifier = LLMProductClassifier()
    
    # Process products
    results = []
    for idx, row in sample.iterrows():
        result = classifier.process_product(row)
        results.append(result)
        
        # Add delay to respect rate limits
        time.sleep(1)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Categorize by confidence
    high_conf = results_df[results_df['confidence_score'] >= 0.7]
    medium_conf = results_df[(results_df['confidence_score'] >= 0.5) & 
                             (results_df['confidence_score'] < 0.7)]
    low_conf = results_df[results_df['confidence_score'] < 0.5]
    
    print("\n" + "=" * 80)
    print("LLM TRIAL RUN SUMMARY")
    print("=" * 80)
    print(f"Total Processed: {len(results_df)}")
    print(f"High Confidence (>= 0.7): {len(high_conf)} ({len(high_conf)/len(results_df)*100:.1f}%)")
    print(f"Medium Confidence (0.5-0.7): {len(medium_conf)} ({len(medium_conf)/len(results_df)*100:.1f}%)")
    print(f"Low Confidence (< 0.5): {len(low_conf)} ({len(low_conf)/len(results_df)*100:.1f}%)")
    print()
    
    return results_df, high_conf, medium_conf, low_conf


if __name__ == "__main__":
    results_df, high_conf, medium_conf, low_conf = run_llm_trial_classification(
        batch_size=10,
        min_name_length=80
    )
    
    print("LLM trial run complete! Results ready for display.")
