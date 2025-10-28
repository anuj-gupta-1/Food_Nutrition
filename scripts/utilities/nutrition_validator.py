"""
Nutrition Data Validator
Cross-references LLM results with known nutrition databases
"""

import json
import requests
import time
from typing import Dict, Optional, Tuple

class NutritionValidator:
    """Validates LLM-generated nutrition data against known sources"""
    
    def __init__(self):
        # Known nutrition ranges for common beverage types
        self.beverage_nutrition_ranges = {
            'cola': {
                'energy_kcal': (35, 50),
                'carbs_g': (8, 12),
                'total_sugars_g': (8, 12),
                'protein_g': (0, 0.5),
                'fat_g': (0, 0.5)
            },
            'juice': {
                'energy_kcal': (40, 60),
                'carbs_g': (10, 15),
                'total_sugars_g': (8, 15),
                'protein_g': (0, 2),
                'fat_g': (0, 1)
            },
            'energy_drink': {
                'energy_kcal': (45, 55),
                'carbs_g': (11, 14),
                'total_sugars_g': (10, 13),
                'protein_g': (0, 1),
                'fat_g': (0, 0.5)
            },
            'health_drink': {
                'energy_kcal': (350, 420),
                'carbs_g': (60, 80),
                'total_sugars_g': (25, 40),
                'protein_g': (8, 15),
                'fat_g': (1, 5)
            }
        }
        
        # OpenFoodFacts API for cross-reference
        self.openfoodfacts_api = "https://world.openfoodfacts.org/api/v0/product"
    
    def classify_beverage_type(self, product_name: str, brand: str) -> str:
        """Classify beverage type for validation"""
        product_lower = product_name.lower()
        brand_lower = brand.lower()
        
        if any(term in product_lower for term in ['coca cola', 'pepsi', 'thums up', 'sprite']):
            return 'cola'
        elif any(term in product_lower for term in ['juice', 'maaza', 'frooti', 'real']):
            return 'juice'
        elif any(term in product_lower for term in ['red bull', 'monster', 'gatorade']):
            return 'energy_drink'
        elif any(term in product_lower for term in ['horlicks', 'bournvita', 'complan', 'boost']):
            return 'health_drink'
        else:
            return 'generic'
    
    def validate_nutrition_ranges(self, nutrition_data: Dict, product_name: str, brand: str) -> Dict:
        """Validate nutrition data against expected ranges"""
        beverage_type = self.classify_beverage_type(product_name, brand)
        
        if beverage_type not in self.beverage_nutrition_ranges:
            return {
                'range_validation': 'unknown_type',
                'confidence_adjustment': 0,
                'warnings': [f'Unknown beverage type: {beverage_type}']
            }
        
        expected_ranges = self.beverage_nutrition_ranges[beverage_type]
        per_100g = nutrition_data.get('per_100g', {}) if nutrition_data else {}
        
        validation_results = {
            'range_validation': 'pass',
            'confidence_adjustment': 0,
            'warnings': [],
            'field_validations': {}
        }
        
        for field, (min_val, max_val) in expected_ranges.items():
            # Safe numeric extraction with None handling
            raw_value = per_100g.get(field) if per_100g else None
            
            if raw_value is None:
                validation_results['field_validations'][field] = 'missing'
                validation_results['warnings'].append(f'{field} is missing')
                validation_results['confidence_adjustment'] -= 0.05
            else:
                # Convert to numeric, handling None and string values
                try:
                    actual_value = float(raw_value) if raw_value is not None else 0
                    if min_val <= actual_value <= max_val:
                        validation_results['field_validations'][field] = 'valid'
                    else:
                        validation_results['field_validations'][field] = 'out_of_range'
                        validation_results['warnings'].append(
                            f'{field}: {actual_value} outside expected range {min_val}-{max_val}'
                        )
                except (ValueError, TypeError):
                    validation_results['field_validations'][field] = 'invalid_type'
                    validation_results['warnings'].append(f'{field} has invalid value: {raw_value}')
                    validation_results['confidence_adjustment'] -= 0.05
                validation_results['confidence_adjustment'] -= 0.1
        
        # Overall validation
        invalid_fields = len([v for v in validation_results['field_validations'].values() if v != 'valid'])
        if invalid_fields > 2:
            validation_results['range_validation'] = 'fail'
            validation_results['confidence_adjustment'] -= 0.2
        elif invalid_fields > 0:
            validation_results['range_validation'] = 'warning'
        
        return validation_results
    
    def search_openfoodfacts(self, product_name: str, brand: str) -> Optional[Dict]:
        """Search OpenFoodFacts for nutrition data"""
        try:
            # Search by product name and brand
            search_query = f"{brand} {product_name}".replace(' ', '+')
            search_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={search_query}&json=1"
            
            response = requests.get(search_url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])
                
                if products:
                    # Take the first match
                    product = products[0]
                    nutriments = product.get('nutriments', {})
                    
                    if nutriments:
                        return {
                            'source': 'openfoodfacts',
                            'product_name': product.get('product_name', ''),
                            'brand': product.get('brands', ''),
                            'energy_kcal': nutriments.get('energy-kcal_100g'),
                            'carbs_g': nutriments.get('carbohydrates_100g'),
                            'sugars_g': nutriments.get('sugars_100g'),
                            'protein_g': nutriments.get('proteins_100g'),
                            'fat_g': nutriments.get('fat_100g'),
                            'sodium_mg': nutriments.get('sodium_100g'),
                            'confidence': 0.8
                        }
            
            return None
            
        except Exception as e:
            print(f"  ⚠️ OpenFoodFacts search failed: {e}")
            return None
    
    def cross_reference_nutrition(self, nutrition_data: Dict, product_name: str, brand: str) -> Dict:
        """Cross-reference nutrition data with external sources"""
        print(f"  🔍 Cross-referencing nutrition data...")
        
        # Search OpenFoodFacts
        off_data = self.search_openfoodfacts(product_name, brand)
        
        if not off_data:
            return {
                'cross_reference': 'no_match',
                'confidence_adjustment': -0.1,
                'warnings': ['No external nutrition data found for cross-reference']
            }
        
        # Compare key nutrition values
        per_100g = nutrition_data.get('per_100g', {}) if nutrition_data else {}
        comparison_results = {
            'cross_reference': 'match',
            'confidence_adjustment': 0,
            'warnings': [],
            'comparisons': {}
        }
        
        key_fields = ['energy_kcal', 'carbs_g', 'protein_g', 'fat_g']
        
        for field in key_fields:
            # Safe LLM value extraction
            raw_llm_value = per_100g.get(field) if per_100g else None
            try:
                llm_value = float(raw_llm_value) if raw_llm_value is not None else None
            except (ValueError, TypeError):
                llm_value = None
            
            off_field = field.replace('_g', '_g').replace('energy_kcal', 'energy_kcal')
            off_value = off_data.get(off_field)
            
            if off_value is not None and llm_value is not None:
                # Calculate percentage difference
                if off_value > 0:
                    diff_pct = abs(llm_value - off_value) / off_value * 100
                    
                    if diff_pct <= 10:  # Within 10%
                        comparison_results['comparisons'][field] = 'close_match'
                        comparison_results['confidence_adjustment'] += 0.05
                    elif diff_pct <= 25:  # Within 25%
                        comparison_results['comparisons'][field] = 'acceptable'
                    else:  # > 25% difference
                        comparison_results['comparisons'][field] = 'significant_difference'
                        comparison_results['warnings'].append(
                            f'{field}: LLM={llm_value}, OpenFoodFacts={off_value} ({diff_pct:.1f}% diff)'
                        )
                        comparison_results['confidence_adjustment'] -= 0.1
        
        # Overall cross-reference result
        significant_diffs = len([c for c in comparison_results['comparisons'].values() 
                               if c == 'significant_difference'])
        
        if significant_diffs > 2:
            comparison_results['cross_reference'] = 'poor_match'
            comparison_results['confidence_adjustment'] -= 0.2
        elif significant_diffs > 0:
            comparison_results['cross_reference'] = 'partial_match'
        
        return comparison_results
    
    def validate_ingredients_logic(self, ingredients_data: Dict, nutrition_data: Dict) -> Dict:
        """Validate logical consistency between ingredients and nutrition"""
        ingredients_list = ingredients_data.get('ingredients_list', [])
        per_100g = nutrition_data.get('per_100g', {}) if nutrition_data else {}
        
        validation_results = {
            'logic_validation': 'pass',
            'confidence_adjustment': 0,
            'warnings': []
        }
        
        # Check sugar consistency with safe numeric handling
        has_sugar_ingredient = any('sugar' in ing.lower() for ing in ingredients_list)
        raw_sugar = per_100g.get('total_sugars_g') if per_100g else None
        
        # Safe sugar content extraction
        try:
            sugar_content = float(raw_sugar) if raw_sugar is not None else 0
        except (ValueError, TypeError):
            sugar_content = 0
        
        if has_sugar_ingredient and sugar_content == 0:
            validation_results['warnings'].append('Sugar in ingredients but 0g sugar in nutrition')
            validation_results['confidence_adjustment'] -= 0.1
        elif not has_sugar_ingredient and sugar_content > 5:
            validation_results['warnings'].append('High sugar content but no sugar in ingredients')
            validation_results['confidence_adjustment'] -= 0.1
        
        # Check protein consistency with safe numeric handling
        has_milk_ingredient = any(term in ' '.join(ingredients_list).lower() 
                                for term in ['milk', 'protein', 'whey', 'casein'])
        raw_protein = per_100g.get('protein_g') if per_100g else None
        
        # Safe protein content extraction
        try:
            protein_content = float(raw_protein) if raw_protein is not None else 0
        except (ValueError, TypeError):
            protein_content = 0
        
        if has_milk_ingredient and protein_content == 0:
            validation_results['warnings'].append('Milk ingredients but 0g protein')
            validation_results['confidence_adjustment'] -= 0.05
        
        # Overall logic validation
        if len(validation_results['warnings']) > 2:
            validation_results['logic_validation'] = 'fail'
        elif len(validation_results['warnings']) > 0:
            validation_results['logic_validation'] = 'warning'
        
        return validation_results
    
    def comprehensive_validation(self, ingredients_data: Dict, nutrition_data: Dict, 
                               product_name: str, brand: str) -> Dict:
        """Perform comprehensive validation of LLM-generated data"""
        print(f"🔍 Validating: {product_name}")
        
        # Range validation
        range_results = self.validate_nutrition_ranges(nutrition_data, product_name, brand)
        
        # Cross-reference validation (with rate limiting)
        cross_ref_results = self.cross_reference_nutrition(nutrition_data, product_name, brand)
        time.sleep(1)  # Rate limiting for OpenFoodFacts
        
        # Logic validation
        logic_results = self.validate_ingredients_logic(ingredients_data, nutrition_data)
        
        # Calculate overall confidence adjustment
        total_confidence_adjustment = (
            range_results['confidence_adjustment'] +
            cross_ref_results['confidence_adjustment'] +
            logic_results['confidence_adjustment']
        )
        
        # Determine overall validation status
        validation_statuses = [
            range_results['range_validation'],
            cross_ref_results['cross_reference'],
            logic_results['logic_validation']
        ]
        
        if 'fail' in validation_statuses:
            overall_status = 'fail'
        elif 'warning' in validation_statuses or 'poor_match' in validation_statuses:
            overall_status = 'warning'
        else:
            overall_status = 'pass'
        
        # Compile all warnings
        all_warnings = (
            range_results['warnings'] +
            cross_ref_results['warnings'] +
            logic_results['warnings']
        )
        
        return {
            'overall_status': overall_status,
            'confidence_adjustment': max(-0.5, min(0.3, total_confidence_adjustment)),  # Cap adjustments
            'warnings': all_warnings,
            'validation_details': {
                'range_validation': range_results,
                'cross_reference': cross_ref_results,
                'logic_validation': logic_results
            },
            'recommendation': self.get_recommendation(overall_status, len(all_warnings))
        }
    
    def get_recommendation(self, status: str, warning_count: int) -> str:
        """Get recommendation based on validation results"""
        if status == 'pass' and warning_count == 0:
            return 'accept_high_confidence'
        elif status == 'pass' or (status == 'warning' and warning_count <= 2):
            return 'accept_medium_confidence'
        elif status == 'warning':
            return 'accept_low_confidence'
        else:
            return 'reject_or_manual_review'


def test_validation():
    """Test the validation system"""
    print("🧪 TESTING NUTRITION VALIDATION")
    print("=" * 60)
    
    validator = NutritionValidator()
    
    # Test data (mock LLM response)
    test_ingredients = {
        "ingredients_list": ["Water", "Sugar", "Natural Flavors", "Citric Acid"],
        "ingredients_detailed": []
    }
    
    test_nutrition = {
        "per_100g": {
            "energy_kcal": 42,
            "carbs_g": 10.6,
            "total_sugars_g": 10.6,
            "protein_g": 0,
            "fat_g": 0,
            "sodium_mg": 4
        },
        "confidence_scores": {
            "overall_confidence": 0.80
        }
    }
    
    # Test validation
    result = validator.comprehensive_validation(
        test_ingredients, 
        test_nutrition, 
        "Coca Cola 750ml", 
        "Coca Cola"
    )
    
    print(f"✅ Validation complete!")
    print(f"   Overall status: {result['overall_status']}")
    print(f"   Confidence adjustment: {result['confidence_adjustment']:+.2f}")
    print(f"   Recommendation: {result['recommendation']}")
    
    if result['warnings']:
        print(f"   Warnings:")
        for warning in result['warnings']:
            print(f"     • {warning}")
    
    # Calculate final confidence
    original_confidence = test_nutrition['confidence_scores']['overall_confidence']
    final_confidence = max(0.1, min(1.0, original_confidence + result['confidence_adjustment']))
    
    print(f"   Original confidence: {original_confidence:.2f}")
    print(f"   Final confidence: {final_confidence:.2f}")

if __name__ == "__main__":
    test_validation()