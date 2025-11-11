#!/usr/bin/env python3
"""
LLM-Based Product Classification and Name Cleanup
Uses existing LLM service for intelligent subcategory classification and clean name extraction
"""

import pandas as pd
import json
import sys
import os
import time
from typing import Dict

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
        
        # Create LLM prompt for classification
        prompt = f"""PRODUCT CLASSIFICATION AND NAME EXTRACTION

Product Name: {product_name}
Brand: {brand}
Current Category: {current_category}
Current Subcategory: {current_subcategory}

TASK 1: SUBCATEGORY CLASSIFICATION
Classify this product into the MOST APPROPRIATE subcategory from the list below.

Valid subcategories for {current_category}:
{subcategories_str}

TASK 2: CLEAN NAME EXTRACTION
Extract a clean, concise product name that:
- Keeps the core product identity
- Keeps important descriptors (Organic, Low GI, Gluten Free, Sugar Free, Healthy, etc.)
- Removes marketing fluff, size info, pack details, and redundant text
- Removes parenthetical content and pipe-separated details
- Is suitable for display in a mobile app

EXAMPLES:
Input: "Dhampur Green Organic Brown Sugar 800g, 100% Certified Organic Natural Brown Demerara Sugar"
Output: "Organic Brown Sugar"

Input: "Gustora Healthy Macaroni & Mini Fusilli Pasta Combo Pack of 2 Made Of Durum Wheat Semolina"
Output: "Healthy Macaroni & Mini Fusilli Pasta"

Input: "LILA DRY FRUITS 4 Superseed Combo (Chia, Pumpkin, Sunflower & Flax) 100gms each"
Output: "4 Superseed Combo"

Input: "Wheafree Gluten Free Butter Cookies Combo Butter Namkeen Cookies (200g)"
Output: "Gluten Free Butter Cookies"

Input: "VitProFiber Low GI Multigrain Atta,Whole Grain Flour High Fiber, Protein & Vitamins Pack 1 (1 kg)"
Output: "Low GI Multigrain Atta"

RESPONSE FORMAT (provide ONLY these lines):
new_subcategory: <one of the valid subcategories>
clean_product_name: <extracted clean name>
confidence_score: <0.0-1.0>
classification_reasoning: <brief explanation>"""

        # Use LLM directly (same infrastructure as nutrition service)
        try:
            # Call Groq API directly (same as nutrition service uses)
            response_text = self.call_llm_for_classification(prompt)
            
            if response_text:
                parsed = self.parse_classification_response(
                    response_text,
                    valid_subcategories,
                    current_subcategory,
                    product_name
                )
                return parsed
            
            # Fallback to unchanged
            return {
                'new_subcategory': current_subcategory,
                'clean_product_name': product_name,
                'confidence_score': 0.3,
                'classification_method': 'llm_failed',
                'needs_manual_review': True,
                'processing_notes': 'LLM classification failed'
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
    
    def call_llm_for_classification(self, prompt: str) -> str:
        """
        Call LLM API for classification (separate from nutrition extraction)
        Uses same LLM (Groq) but dedicated method for classification
        """
        import requests
        
        # Try Groq API (same as nutrition service uses)
        try:
            # Check if we can make request
            can_request, reason = self.llm_service.can_make_request("groq")
            if not can_request:
                print(f"  -> Groq rate limit: {reason}")
                return None
            
            payload = {
                "model": "llama3-8b-8192",  # Same model as nutrition service
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 200,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.llm_service.providers["groq"]["url"],
                headers=self.llm_service.providers["groq"]["headers"],
                json=payload,
                timeout=self.llm_service.providers["groq"]["timeout"]
            )
            
            # Track request
            self.llm_service.request_timestamps["groq"].append(time.time())
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                print(f"  -> Got LLM response ({len(content)} chars)")
                return content
            else:
                print(f"  -> Groq API error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  -> Groq API exception: {e}")
            return None
    
    def parse_classification_response(self, content: str, valid_subcategories: list,
                                     fallback_subcategory: str, fallback_name: str) -> Dict:
        """Parse LLM response and extract classification data"""
        
        try:
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
                    confidence = 0.8
            
            # Extract clean_product_name
            name_match = re.search(r'clean_product_name:\s*(.+?)(?=\n|$)', content, re.IGNORECASE)
            if name_match:
                clean_name = name_match.group(1).strip()
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
                'classification_method': 'llm',
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
    print(f"✅ Loaded {len(df):,} products")
    
    # Filter for long names
    df['name_length'] = df['product_name'].str.len()
    long_names = df[df['name_length'] >= min_name_length].copy()
    print(f"✅ Found {len(long_names):,} products with names >= {min_name_length} characters")
    
    # Sample products (mixed categories) - use same seed for consistency
    sample = long_names.sample(n=min(batch_size, len(long_names)), random_state=42)
    print(f"✅ Processing {len(sample)} products for LLM trial run")
    print()
    
    # Initialize classifier
    classifier = LLMProductClassifier()
    
    # Process products
    results = []
    for idx, row in sample.iterrows():
        result = classifier.process_product(row)
        results.append(result)
        
        # Add delay to respect rate limits
        time.sleep(2)
    
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
