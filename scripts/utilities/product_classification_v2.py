#!/usr/bin/env python3
"""
Product Classification V2 - Improved with negative patterns and LLM fallback
"""

import pandas as pd
import re
import sys
import os
import json
from typing import Dict, Tuple, List

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from csv_handler import load_products_csv


class ImprovedProductClassifier:
    """Improved classifier with negative patterns and LLM fallback"""
    
    def __init__(self):
        self.setup_classification_rules()
        self.setup_name_parsing_patterns()
    
    def setup_classification_rules(self):
        """Define improved classification rules with negative patterns"""
        
        self.subcategory_rules = {
            # ESSENTIALS: salt-sugar split with negative patterns
            'salt': {
                'keywords': ['salt', 'namak', 'sea salt', 'rock salt', 'pink salt', 'iodized'],
                'patterns': [r'\bsalt\b(?!\s*free)', r'\bnamak\b'],  # Not "salt free"
                'negative_patterns': [r'salted', r'salt[-\s]free'],  # Exclude "salted" and "salt-free"
                'confidence': 0.9
            },
            'sugar': {
                'keywords': ['sugar', 'cheeni', 'jaggery', 'gur', 'sweetener', 'stevia'],
                'patterns': [r'\bsugar\b(?!\s*free)', r'\bcheeni\b', r'\bjaggery\b', r'\bgur\b'],
                'negative_patterns': [r'sugar[-\s]free', r'no\s+sugar'],  # Exclude "sugar-free"
                'confidence': 0.9
            },
            
            # SNACKS: chips-namkeen split with better patterns
            'chips': {
                'keywords': ['chips', 'potato chips', 'wafers', 'crisps', 'banana chips'],
                'patterns': [r'\bchips\b', r'\bwafer', r'\bcrisp', r'banana\s+chips'],
                'negative_patterns': [],
                'confidence': 0.85
            },
            'namkeen': {
                'keywords': ['namkeen', 'mixture', 'sev', 'bhujia', 'chivda', 'murukku', 'chakli', 
                           'peanuts', 'roasted', 'salted peanuts'],
                'patterns': [r'\bnamkeen\b', r'\bmixture\b', r'\bsev\b', r'\bbhujia\b', 
                           r'salted\s+peanuts', r'roasted\s+peanuts'],
                'negative_patterns': [],
                'confidence': 0.85
            },
            
            # FLAVOURINGS: pickles-chutney split
            'pickles': {
                'keywords': ['pickle', 'achar', 'achaar', 'pickled'],
                'patterns': [r'\bpickle', r'\bachar', r'\bachaar'],
                'negative_patterns': [],
                'confidence': 0.9
            },
            'chutney': {
                'keywords': ['chutney', 'sauce', 'dip'],
                'patterns': [r'\bchutney\b'],
                'negative_patterns': [],
                'confidence': 0.85
            },
            
            # BEVERAGE: tea-coffee split
            'tea': {
                'keywords': ['tea', 'chai', 'green tea', 'black tea', 'tea bags', 'tea leaves'],
                'patterns': [r'\btea\b', r'\bchai\b'],
                'negative_patterns': [],
                'confidence': 0.9
            },
            'coffee': {
                'keywords': ['coffee', 'espresso', 'cappuccino', 'latte', 'instant coffee', 'coffee beans'],
                'patterns': [r'\bcoffee\b', r'\bespresso\b', r'\bcappuccino\b'],
                'negative_patterns': [],
                'confidence': 0.9
            },
            
            # BEVERAGE: juice-drink split
            'juice': {
                'keywords': ['juice', 'orange juice', 'apple juice', 'mango juice', 'fruit juice', 'ras'],
                'patterns': [r'\bjuice\b', r'\bras\b'],
                'negative_patterns': [],
                'confidence': 0.85
            },
            'carbonated': {
                'keywords': ['cola', 'pepsi', 'coca cola', 'sprite', 'fanta', 'soda', 'fizzy', 
                           'carbonated', 'soft drink', 'cold drink'],
                'patterns': [r'\bcola\b', r'\bsoda\b', r'\bfizzy\b', r'\bcarbonated\b'],
                'negative_patterns': [],
                'confidence': 0.9
            },
        }
        
        self.common_brands = [
            'tata', 'amul', 'nestle', 'britannia', 'parle', 'itc', 'dabur', 'patanjali',
            'mother dairy', 'haldiram', 'bikaji', 'lays', 'kurkure', 'bingo', 'pringles',
            'coca cola', 'pepsi', 'sprite', 'fanta', 'maaza', 'frooti', 'real',
            'lipton', 'taj mahal', 'red label', 'nescafe', 'bru'
        ]
    
    def setup_name_parsing_patterns(self):
        """Define regex patterns for name parsing"""
        
        self.patterns = {
            'size': re.compile(r'(\d+(?:\.\d+)?\s*(?:ml|l|g|kg|gm|gram|litre|liter|oz|lb))', re.IGNORECASE),
            'pack': re.compile(r'(pack\s+of\s+\d+|combo|multipack|\d+\s*x\s*\d+)', re.IGNORECASE),
            'parenthetical': re.compile(r'\([^)]*\)'),
            'pipe_separated': re.compile(r'\|[^|]*'),
            'features': re.compile(
                r'(organic|natural|sugar[-\s]free|no\s+preservatives|cold\s+pressed|'
                r'instant|fresh|pure|premium|healthy|gluten[-\s]free|vegan|'
                r'low[-\s]fat|fat[-\s]free|whole\s+grain|multigrain)',
                re.IGNORECASE
            ),
            'brand_prefix': re.compile(r'^([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)?)\s+'),
        }
    
    def classify_subcategory(self, product_name: str, current_category: str, 
                            current_subcategory: str) -> Tuple[str, float, str]:
        """Classify with negative pattern checking"""
        
        product_lower = product_name.lower()
        best_match = None
        best_confidence = 0.0
        method = 'unchanged'
        
        needs_split = current_subcategory in [
            'salt-sugar', 'chips-namkeen', 'pickles-chutney', 
            'tea-cofee', 'juice-drink', 'general'
        ]
        
        if not needs_split:
            return current_subcategory, 1.0, 'unchanged'
        
        for subcategory, rules in self.subcategory_rules.items():
            confidence = 0.0
            
            # Check negative patterns first - if match, skip this subcategory
            skip_subcategory = False
            for neg_pattern in rules.get('negative_patterns', []):
                if re.search(neg_pattern, product_lower):
                    skip_subcategory = True
                    break
            
            if skip_subcategory:
                continue
            
            # Check keywords
            for keyword in rules['keywords']:
                if keyword.lower() in product_lower:
                    confidence = max(confidence, rules['confidence'])
                    method = 'keyword_match'
            
            # Check patterns
            for pattern in rules['patterns']:
                if re.search(pattern, product_lower):
                    confidence = max(confidence, rules['confidence'] - 0.05)
                    method = 'pattern_match'
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = subcategory
        
        if best_match and best_confidence >= 0.5:
            return best_match, best_confidence, method
        
        return current_subcategory, 0.3, 'low_confidence'
    
    def extract_brand(self, product_name: str, current_brand: str) -> Tuple[str, float]:
        """Extract brand from product name"""
        
        if current_brand and len(current_brand) > 2:
            if current_brand.lower() in product_name.lower():
                return current_brand, 0.95
        
        product_lower = product_name.lower()
        for brand in self.common_brands:
            if brand.lower() in product_lower:
                return brand.title(), 0.9
        
        match = self.patterns['brand_prefix'].match(product_name)
        if match:
            return match.group(1), 0.7
        
        return current_brand, 0.5
    
    def extract_size_info(self, product_name: str) -> Tuple[str, float]:
        """Extract size information"""
        sizes = []
        for match in self.patterns['size'].finditer(product_name):
            sizes.append(match.group(1))
        return ', '.join(sizes) if sizes else '', 0.95 if sizes else 0.0
    
    def extract_pack_info(self, product_name: str) -> Tuple[str, float]:
        """Extract pack information"""
        packs = []
        for match in self.patterns['pack'].finditer(product_name):
            packs.append(match.group(1))
        return ', '.join(packs) if packs else '', 0.9 if packs else 0.0
    
    def extract_features(self, product_name: str) -> Tuple[str, float]:
        """Extract special features with deduplication"""
        features = []
        features_lower = []
        
        for match in self.patterns['features'].finditer(product_name):
            feature = match.group(1)
            feature_lower = feature.lower()
            if feature_lower not in features_lower:
                features.append(feature.title())
                features_lower.append(feature_lower)
        
        return ' | '.join(features) if features else '', 0.85 if features else 0.0
    
    def create_clean_name_improved(self, product_name: str, size_info: str, pack_info: str, 
                                   features: str, brand: str) -> Tuple[str, float]:
        """Improved clean name creation"""
        
        clean = product_name
        
        # Remove sizes
        if size_info:
            for size in size_info.split(', '):
                clean = re.sub(re.escape(size), '', clean, flags=re.IGNORECASE)
        
        # Remove pack info
        if pack_info:
            for pack in pack_info.split(', '):
                clean = re.sub(re.escape(pack), '', clean, flags=re.IGNORECASE)
        
        # Remove all parenthetical content
        clean = self.patterns['parenthetical'].sub('', clean)
        
        # Remove all pipe-separated content
        clean = self.patterns['pipe_separated'].sub('', clean)
        
        # Remove brand from beginning
        if brand and clean.lower().startswith(brand.lower()):
            clean = clean[len(brand):].strip()
        
        # Clean up whitespace and punctuation
        clean = re.sub(r'\s+', ' ', clean)
        clean = re.sub(r'[,\-\|]+$', '', clean)
        clean = re.sub(r'^\s*[,\-\|]+', '', clean)
        clean = clean.strip(' ,-|')
        
        # Remove empty parentheses or brackets
        clean = re.sub(r'\(\s*\)', '', clean)
        clean = re.sub(r'\[\s*\]', '', clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        
        # Calculate confidence
        original_len = len(product_name)
        clean_len = len(clean)
        reduction_ratio = (original_len - clean_len) / original_len if original_len > 0 else 0
        
        if 0.2 <= reduction_ratio <= 0.6 and clean_len > 10:
            confidence = 0.85
        elif 0.1 <= reduction_ratio < 0.2 or 0.6 < reduction_ratio <= 0.7:
            confidence = 0.7
        else:
            confidence = 0.5
        
        return clean, confidence
    
    def use_llm_fallback(self, product_name: str, current_category: str, 
                        current_subcategory: str, current_brand: str) -> Dict:
        """Use LLM for classification and name parsing - Placeholder for future implementation"""
        
        # TODO: Implement LLM fallback when needed
        # For now, return None to use rule-based results
        return None
    
    def process_product(self, row: pd.Series, use_llm_for_low_confidence=True) -> Dict:
        """Process product with LLM fallback option"""
        
        product_name = str(row.get('product_name', ''))
        current_category = str(row.get('category', ''))
        current_subcategory = str(row.get('subcategory', ''))
        current_brand = str(row.get('brand', ''))
        
        # Try rule-based first
        new_subcategory, cat_confidence, cat_method = self.classify_subcategory(
            product_name, current_category, current_subcategory
        )
        
        extracted_brand, brand_confidence = self.extract_brand(product_name, current_brand)
        size_info, size_confidence = self.extract_size_info(product_name)
        pack_info, pack_confidence = self.extract_pack_info(product_name)
        features, features_confidence = self.extract_features(product_name)
        clean_name, clean_confidence = self.create_clean_name_improved(
            product_name, size_info, pack_info, features, extracted_brand
        )
        
        confidences = [cat_confidence, brand_confidence, clean_confidence]
        overall_confidence = sum(confidences) / len(confidences)
        
        # Use LLM fallback if confidence is low
        if use_llm_for_low_confidence and overall_confidence < 0.7:
            llm_result = self.use_llm_fallback(
                product_name, current_category, current_subcategory, current_brand
            )
            if llm_result:
                llm_result['original_id'] = row.get('id', '')
                llm_result['original_name'] = product_name
                llm_result['original_category'] = current_category
                llm_result['original_subcategory'] = current_subcategory
                llm_result['original_brand'] = current_brand
                llm_result['brand_confidence'] = 0.8
                return llm_result
        
        return {
            'original_id': row.get('id', ''),
            'original_name': product_name,
            'original_category': current_category,
            'original_subcategory': current_subcategory,
            'original_brand': current_brand,
            'new_subcategory': new_subcategory,
            'category_confidence': round(cat_confidence, 2),
            'classification_method': cat_method,
            'clean_product_name': clean_name,
            'extracted_brand': extracted_brand,
            'brand_confidence': round(brand_confidence, 2),
            'size_info': size_info,
            'pack_info': pack_info,
            'special_features': features,
            'name_parsing_confidence': round(clean_confidence, 2),
            'overall_confidence': round(overall_confidence, 2),
            'needs_manual_review': overall_confidence < 0.7,
            'processing_notes': f'Processed with {cat_method}'
        }


def run_trial_v2(start_idx=22, end_idx=32, use_llm=False):
    """Run trial on specific product range from earlier batch"""
    
    print("=" * 80)
    print("PRODUCT CLASSIFICATION V2 - IMPROVED TRIAL RUN")
    print("=" * 80)
    print()
    
    df = load_products_csv()
    print(f"✅ Loaded {len(df):,} products")
    
    # Get long names
    df['name_length'] = df['product_name'].str.len()
    long_names = df[df['name_length'] >= 80].copy()
    
    # Get same sample as before (using same random_state)
    sample_full = long_names.sample(n=50, random_state=42)
    
    # Get products 22-32 (indices 21-31 in 0-based)
    sample = sample_full.iloc[start_idx-1:end_idx]
    
    print(f"✅ Processing products {start_idx}-{end_idx} from earlier batch")
    print(f"✅ LLM Fallback: {'Enabled' if use_llm else 'Disabled'}")
    print()
    
    classifier = ImprovedProductClassifier()
    
    results = []
    for idx, row in sample.iterrows():
        result = classifier.process_product(row, use_llm_for_low_confidence=use_llm)
        results.append(result)
    
    results_df = pd.DataFrame(results)
    
    high_conf = results_df[results_df['overall_confidence'] >= 0.7]
    medium_conf = results_df[(results_df['overall_confidence'] >= 0.5) & 
                             (results_df['overall_confidence'] < 0.7)]
    low_conf = results_df[results_df['overall_confidence'] < 0.5]
    
    print("=" * 80)
    print("TRIAL RUN V2 SUMMARY")
    print("=" * 80)
    print(f"Total Processed: {len(results_df)}")
    print(f"High Confidence (>= 0.7): {len(high_conf)} ({len(high_conf)/len(results_df)*100:.1f}%)")
    print(f"Medium Confidence (0.5-0.7): {len(medium_conf)} ({len(medium_conf)/len(results_df)*100:.1f}%)")
    print(f"Low Confidence (< 0.5): {len(low_conf)} ({len(low_conf)/len(results_df)*100:.1f}%)")
    print()
    
    return results_df, high_conf, medium_conf, low_conf


if __name__ == "__main__":
    results_df, high_conf, medium_conf, low_conf = run_trial_v2(
        start_idx=22,
        end_idx=32,
        use_llm=False  # Start without LLM to test rule improvements
    )
    
    print("Trial run V2 complete!")
