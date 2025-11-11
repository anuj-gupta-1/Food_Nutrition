#!/usr/bin/env python3
"""
Product Classification and Name Parsing Engine
Rule-based classification with confidence scoring
"""

import pandas as pd
import re
import sys
import os
from typing import Dict, Tuple, List

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from csv_handler import load_products_csv, save_products_csv


class ProductClassifier:
    """Rule-based product classification with confidence scoring"""
    
    def __init__(self):
        self.setup_classification_rules()
        self.setup_name_parsing_patterns()
    
    def setup_classification_rules(self):
        """Define classification rules for category/subcategory splits"""
        
        # Subcategory split rules with keywords and patterns
        self.subcategory_rules = {
            # ESSENTIALS: salt-sugar split
            'salt': {
                'keywords': ['salt', 'namak', 'sea salt', 'rock salt', 'pink salt', 'iodized'],
                'patterns': [r'\bsalt\b', r'\bnamak\b'],
                'confidence': 0.9
            },
            'sugar': {
                'keywords': ['sugar', 'cheeni', 'jaggery', 'gur', 'sweetener', 'stevia'],
                'patterns': [r'\bsugar\b', r'\bcheeni\b', r'\bjaggery\b', r'\bgur\b'],
                'confidence': 0.9
            },
            
            # SNACKS: chips-namkeen split
            'chips': {
                'keywords': ['chips', 'potato chips', 'wafers', 'crisps', 'lays', 'pringles'],
                'patterns': [r'\bchips\b', r'\bwafer', r'\bcrisp'],
                'confidence': 0.85
            },
            'namkeen': {
                'keywords': ['namkeen', 'mixture', 'sev', 'bhujia', 'chivda', 'murukku', 'chakli'],
                'patterns': [r'\bnamkeen\b', r'\bmixture\b', r'\bsev\b', r'\bbhujia\b'],
                'confidence': 0.85
            },
            
            # FLAVOURINGS: pickles-chutney split
            'pickles': {
                'keywords': ['pickle', 'achar', 'achaar', 'pickled'],
                'patterns': [r'\bpickle', r'\bachar', r'\bachaar'],
                'confidence': 0.9
            },
            'chutney': {
                'keywords': ['chutney', 'sauce', 'dip'],
                'patterns': [r'\bchutney\b'],
                'confidence': 0.85
            },
            
            # BEVERAGE: tea-coffee split
            'tea': {
                'keywords': ['tea', 'chai', 'green tea', 'black tea', 'tea bags', 'tea leaves'],
                'patterns': [r'\btea\b', r'\bchai\b'],
                'confidence': 0.9
            },
            'coffee': {
                'keywords': ['coffee', 'espresso', 'cappuccino', 'latte', 'instant coffee', 'coffee beans'],
                'patterns': [r'\bcoffee\b', r'\bespresso\b', r'\bcappuccino\b'],
                'confidence': 0.9
            },
            
            # BEVERAGE: juice-drink split
            'juice': {
                'keywords': ['juice', 'orange juice', 'apple juice', 'mango juice', 'fruit juice', 'ras'],
                'patterns': [r'\bjuice\b', r'\bras\b'],
                'confidence': 0.85
            },
            'carbonated': {
                'keywords': ['cola', 'pepsi', 'coca cola', 'sprite', 'fanta', 'soda', 'fizzy', 
                           'carbonated', 'soft drink', 'cold drink'],
                'patterns': [r'\bcola\b', r'\bsoda\b', r'\bfizzy\b', r'\bcarbonated\b'],
                'confidence': 0.9
            },
            'energy-drinks': {
                'keywords': ['energy drink', 'red bull', 'monster', 'energy'],
                'patterns': [r'\benergy\s+drink', r'\bred\s+bull\b', r'\bmonster\b'],
                'confidence': 0.9
            },
            'health-drinks': {
                'keywords': ['protein drink', 'health drink', 'nutrition drink', 'boost', 'horlicks', 
                           'complan', 'bournvita'],
                'patterns': [r'\bprotein\s+drink', r'\bhealth\s+drink', r'\bboost\b', r'\bhorlicks\b'],
                'confidence': 0.85
            },
            
            # DAIRY expansion
            'milk': {
                'keywords': ['milk', 'doodh', 'toned milk', 'full cream', 'skimmed milk'],
                'patterns': [r'\bmilk\b', r'\bdoodh\b'],
                'confidence': 0.9
            },
            'curd': {
                'keywords': ['curd', 'dahi', 'yogurt', 'yoghurt'],
                'patterns': [r'\bcurd\b', r'\bdahi\b', r'\byogurt\b', r'\byoghurt\b'],
                'confidence': 0.9
            },
            'cheese': {
                'keywords': ['cheese', 'cheddar', 'mozzarella', 'processed cheese'],
                'patterns': [r'\bcheese\b', r'\bcheddar\b', r'\bmozzarella\b'],
                'confidence': 0.85
            },
            'paneer': {
                'keywords': ['paneer', 'cottage cheese'],
                'patterns': [r'\bpaneer\b', r'\bcottage\s+cheese\b'],
                'confidence': 0.95
            },
            'butter': {
                'keywords': ['butter', 'ghee', 'makhan'],
                'patterns': [r'\bbutter\b', r'\bghee\b', r'\bmakhan\b'],
                'confidence': 0.9
            }
        }
        
        # Brand patterns for better extraction
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
            'parenthetical': re.compile(r'\(([^)]+)\)'),
            'pipe_separated': re.compile(r'\|([^|]+)'),
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
        """
        Classify product into new subcategory
        Returns: (new_subcategory, confidence, method)
        """
        product_lower = product_name.lower()
        best_match = None
        best_confidence = 0.0
        method = 'unchanged'
        
        # Check if current subcategory needs splitting
        needs_split = current_subcategory in [
            'salt-sugar', 'chips-namkeen', 'pickles-chutney', 
            'tea-cofee', 'juice-drink', 'general'
        ]
        
        if not needs_split:
            return current_subcategory, 1.0, 'unchanged'
        
        # Try to match against subcategory rules
        for subcategory, rules in self.subcategory_rules.items():
            confidence = 0.0
            
            # Check exact keyword matches
            for keyword in rules['keywords']:
                if keyword.lower() in product_lower:
                    confidence = max(confidence, rules['confidence'])
                    method = 'keyword_match'
            
            # Check regex patterns
            for pattern in rules['patterns']:
                if re.search(pattern, product_lower):
                    confidence = max(confidence, rules['confidence'] - 0.05)
                    method = 'pattern_match'
            
            # Update best match
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = subcategory
        
        if best_match and best_confidence >= 0.5:
            return best_match, best_confidence, method
        
        return current_subcategory, 0.3, 'low_confidence'
    
    def extract_brand(self, product_name: str, current_brand: str) -> Tuple[str, float]:
        """Extract brand from product name"""
        
        # If current brand is valid and in name, use it
        if current_brand and len(current_brand) > 2:
            if current_brand.lower() in product_name.lower():
                return current_brand, 0.95
        
        # Check against common brands
        product_lower = product_name.lower()
        for brand in self.common_brands:
            if brand.lower() in product_lower:
                return brand.title(), 0.9
        
        # Try to extract from beginning of name
        match = self.patterns['brand_prefix'].match(product_name)
        if match:
            return match.group(1), 0.7
        
        return current_brand, 0.5
    
    def extract_size_info(self, product_name: str) -> Tuple[str, float]:
        """Extract size/quantity information"""
        
        sizes = []
        
        # Find all size mentions
        for match in self.patterns['size'].finditer(product_name):
            sizes.append(match.group(1))
        
        if sizes:
            return ', '.join(sizes), 0.95
        
        return '', 0.0
    
    def extract_pack_info(self, product_name: str) -> Tuple[str, float]:
        """Extract pack/combo information"""
        
        packs = []
        
        # Find pack mentions
        for match in self.patterns['pack'].finditer(product_name):
            packs.append(match.group(1))
        
        if packs:
            return ', '.join(packs), 0.9
        
        return '', 0.0
    
    def extract_features(self, product_name: str) -> Tuple[str, float]:
        """Extract special features"""
        
        features = []
        features_lower = []  # Track lowercase versions to avoid duplicates
        
        # Find feature mentions
        for match in self.patterns['features'].finditer(product_name):
            feature = match.group(1)
            feature_lower = feature.lower()
            if feature_lower not in features_lower:
                features.append(feature.title())  # Normalize to title case
                features_lower.append(feature_lower)
        
        # Check parenthetical content for features
        for match in self.patterns['parenthetical'].finditer(product_name):
            content = match.group(1).lower()
            if any(word in content for word in ['free', 'organic', 'natural', 'pure']):
                feature = match.group(1)
                feature_lower = feature.lower()
                if feature_lower not in features_lower:
                    features.append(feature)
                    features_lower.append(feature_lower)
        
        if features:
            return ' | '.join(features), 0.85
        
        return '', 0.0
    
    def create_clean_name(self, product_name: str, size_info: str, pack_info: str, 
                         features: str, brand: str) -> Tuple[str, float]:
        """Create clean product name by removing extracted components"""
        
        clean = product_name
        
        # Remove size info
        if size_info:
            for size in size_info.split(', '):
                clean = clean.replace(size, '')
        
        # Remove pack info
        if pack_info:
            for pack in pack_info.split(', '):
                clean = clean.replace(pack, '')
        
        # Remove parenthetical content
        clean = self.patterns['parenthetical'].sub('', clean)
        
        # Remove pipe-separated content
        clean = self.patterns['pipe_separated'].sub('', clean)
        
        # Remove brand from beginning if present
        if brand and clean.lower().startswith(brand.lower()):
            clean = clean[len(brand):].strip()
        
        # Clean up extra spaces and punctuation
        clean = re.sub(r'\s+', ' ', clean)
        clean = re.sub(r'[,\-\|]+$', '', clean)
        clean = clean.strip(' ,-|')
        
        # Calculate confidence based on how much we cleaned
        original_len = len(product_name)
        clean_len = len(clean)
        reduction_ratio = (original_len - clean_len) / original_len if original_len > 0 else 0
        
        # Good cleaning should remove 20-60% of original
        if 0.2 <= reduction_ratio <= 0.6:
            confidence = 0.85
        elif 0.1 <= reduction_ratio < 0.2 or 0.6 < reduction_ratio <= 0.7:
            confidence = 0.7
        else:
            confidence = 0.5
        
        return clean, confidence
    
    def process_product(self, row: pd.Series) -> Dict:
        """Process a single product and return classification results"""
        
        product_name = str(row.get('product_name', ''))
        current_category = str(row.get('category', ''))
        current_subcategory = str(row.get('subcategory', ''))
        current_brand = str(row.get('brand', ''))
        
        # Classify subcategory
        new_subcategory, cat_confidence, cat_method = self.classify_subcategory(
            product_name, current_category, current_subcategory
        )
        
        # Extract brand
        extracted_brand, brand_confidence = self.extract_brand(product_name, current_brand)
        
        # Extract size info
        size_info, size_confidence = self.extract_size_info(product_name)
        
        # Extract pack info
        pack_info, pack_confidence = self.extract_pack_info(product_name)
        
        # Extract features
        features, features_confidence = self.extract_features(product_name)
        
        # Create clean name
        clean_name, clean_confidence = self.create_clean_name(
            product_name, size_info, pack_info, features, extracted_brand
        )
        
        # Calculate overall confidence
        confidences = [cat_confidence, brand_confidence, clean_confidence]
        overall_confidence = sum(confidences) / len(confidences)
        
        # Determine if needs manual review
        needs_review = overall_confidence < 0.7
        
        return {
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
            'needs_manual_review': needs_review,
            'processing_notes': f'Processed with {cat_method}'
        }


def run_trial_classification(batch_size=50, min_name_length=80):
    """Run trial classification on sample products"""
    
    print("=" * 80)
    print("PRODUCT CLASSIFICATION & NAME PARSING - TRIAL RUN")
    print("=" * 80)
    print()
    
    # Load data
    df = load_products_csv()
    print(f"✅ Loaded {len(df):,} products")
    
    # Filter for long names
    df['name_length'] = df['product_name'].str.len()
    long_names = df[df['name_length'] >= min_name_length].copy()
    print(f"✅ Found {len(long_names):,} products with names >= {min_name_length} characters")
    
    # Sample products (mixed categories)
    sample = long_names.sample(n=min(batch_size, len(long_names)), random_state=42)
    print(f"✅ Processing {len(sample)} products for trial run")
    print()
    
    # Initialize classifier
    classifier = ProductClassifier()
    
    # Process products
    results = []
    for idx, row in sample.iterrows():
        result = classifier.process_product(row)
        result['original_id'] = row['id']
        result['original_name'] = row['product_name']
        result['original_category'] = row['category']
        result['original_subcategory'] = row['subcategory']
        result['original_brand'] = row['brand']
        results.append(result)
    
    # Convert to DataFrame
    results_df = pd.DataFrame(results)
    
    # Categorize by confidence
    high_conf = results_df[results_df['overall_confidence'] >= 0.7]
    medium_conf = results_df[(results_df['overall_confidence'] >= 0.5) & 
                             (results_df['overall_confidence'] < 0.7)]
    low_conf = results_df[results_df['overall_confidence'] < 0.5]
    
    print("=" * 80)
    print("TRIAL RUN SUMMARY")
    print("=" * 80)
    print(f"Total Processed: {len(results_df)}")
    print(f"High Confidence (>= 0.7): {len(high_conf)} ({len(high_conf)/len(results_df)*100:.1f}%)")
    print(f"Medium Confidence (0.5-0.7): {len(medium_conf)} ({len(medium_conf)/len(results_df)*100:.1f}%)")
    print(f"Low Confidence (< 0.5): {len(low_conf)} ({len(low_conf)/len(results_df)*100:.1f}%)")
    print()
    
    return results_df, high_conf, medium_conf, low_conf


if __name__ == "__main__":
    results_df, high_conf, medium_conf, low_conf = run_trial_classification(
        batch_size=50, 
        min_name_length=80
    )
    
    print("Trial run complete! Results ready for display.")
