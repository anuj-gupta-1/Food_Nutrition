#!/usr/bin/env python3
"""
Migration Validation Script
Validates migration results and data integrity
"""

import sys
import os
import pandas as pd
from typing import Dict, List

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))

from category_manager import CategoryManager
from csv_handler import load_products_csv


class MigrationValidator:
    """Validates migration results and data integrity"""
    
    def __init__(self):
        self.category_manager = CategoryManager()
        self.validation_results = {
            'total_products': 0,
            'valid_categories': 0,
            'invalid_categories': 0,
            'valid_subcategories': 0,
            'invalid_subcategories': 0,
            'issues': []
        }
    
    def validate_categories(self, df: pd.DataFrame) -> Dict:
        """Validate all categories in the dataset"""
        valid_categories = set(self.category_manager.get_all_categories())
        
        # Check each product's category
        invalid_categories = []
        for idx, row in df.iterrows():
            category = str(row.get('category', ''))
            if category not in valid_categories:
                invalid_categories.append({
                    'product_id': row.get('id', ''),
                    'product_name': row.get('product_name', '')[:50],
                    'invalid_category': category
                })
        
        return {
            'total_checked': len(df),
            'valid_count': len(df) - len(invalid_categories),
            'invalid_count': len(invalid_categories),
            'invalid_items': invalid_categories[:10]  # Show first 10
        }
    
    def validate_subcategories(self, df: pd.DataFrame) -> Dict:
        """Validate all subcategories in the dataset"""
        invalid_subcategories = []
        
        for idx, row in df.iterrows():
            category = str(row.get('category', ''))
            subcategory = str(row.get('subcategory', ''))
            
            if not self.category_manager.is_valid_subcategory(category, subcategory):
                invalid_subcategories.append({
                    'product_id': row.get('id', ''),
                    'product_name': row.get('product_name', '')[:50],
                    'category': category,
                    'invalid_subcategory': subcategory,
                    'valid_options': self.category_manager.get_subcategories(category)
                })
        
        return {
            'total_checked': len(df),
            'valid_count': len(df) - len(invalid_subcategories),
            'invalid_count': len(invalid_subcategories),
            'invalid_items': invalid_subcategories[:10]  # Show first 10
        }
    
    def check_data_integrity(self, df: pd.DataFrame) -> Dict:
        """Check overall data integrity"""
        issues = []
        
        # Check for missing categories
        missing_categories = df[df['category'].isna() | (df['category'] == '')].shape[0]
        if missing_categories > 0:
            issues.append(f"Missing categories: {missing_categories} products")
        
        # Check for missing subcategories
        missing_subcategories = df[df['subcategory'].isna() | (df['subcategory'] == '')].shape[0]
        if missing_subcategories > 0:
            issues.append(f"Missing subcategories: {missing_subcategories} products")
        
        # Check for duplicate product IDs
        duplicate_ids = df[df['id'].duplicated()].shape[0]
        if duplicate_ids > 0:
            issues.append(f"Duplicate product IDs: {duplicate_ids} products")
        
        return {
            'total_products': len(df),
            'issues': issues,
            'data_quality_score': max(0, 100 - len(issues) * 10)
        }
    
    def generate_category_distribution(self, df: pd.DataFrame) -> Dict:
        """Generate category distribution statistics"""
        distribution = {}
        
        for category in self.category_manager.get_all_categories():
            category_products = df[df['category'] == category]
            subcategory_dist = category_products['subcategory'].value_counts().to_dict()
            
            distribution[category] = {
                'total_products': len(category_products),
                'subcategory_distribution': subcategory_dist,
                'percentage': (len(category_products) / len(df)) * 100 if len(df) > 0 else 0
            }
        
        return distribution
    
    def run_full_validation(self) -> Dict:
        """Run complete validation suite"""
        print("="*80)
        print("MIGRATION VALIDATION REPORT")
        print("="*80)
        
        try:
            # Load data
            df = load_products_csv()
            print(f"✅ Loaded {len(df):,} products for validation")
            
            # Validate categories
            print("\n🔍 Validating categories...")
            category_results = self.validate_categories(df)
            
            # Validate subcategories
            print("🔍 Validating subcategories...")
            subcategory_results = self.validate_subcategories(df)
            
            # Check data integrity
            print("🔍 Checking data integrity...")
            integrity_results = self.check_data_integrity(df)
            
            # Generate distribution
            print("📊 Generating category distribution...")
            distribution = self.generate_category_distribution(df)
            
            # Compile results
            validation_results = {
                'timestamp': pd.Timestamp.now().isoformat(),
                'total_products': len(df),
                'categories': category_results,
                'subcategories': subcategory_results,
                'integrity': integrity_results,
                'distribution': distribution,
                'overall_status': 'PASS' if (category_results['invalid_count'] == 0 and 
                                           subcategory_results['invalid_count'] == 0 and
                                           len(integrity_results['issues']) == 0) else 'FAIL'
            }
            
            # Print summary
            self.print_validation_summary(validation_results)
            
            return validation_results
            
        except Exception as e:
            print(f"❌ Validation failed: {e}")
            return {'overall_status': 'ERROR', 'error': str(e)}
    
    def print_validation_summary(self, results: Dict) -> None:
        """Print validation summary"""
        print(f"\n📋 VALIDATION SUMMARY")
        print(f"{'='*50}")
        
        # Overall status
        status = results['overall_status']
        status_icon = "✅" if status == "PASS" else "❌"
        print(f"Overall Status: {status_icon} {status}")
        
        # Category validation
        cat_results = results['categories']
        print(f"\n📁 Categories:")
        print(f"   Valid: {cat_results['valid_count']:,} / {cat_results['total_checked']:,}")
        print(f"   Invalid: {cat_results['invalid_count']:,}")
        
        if cat_results['invalid_count'] > 0:
            print(f"   Sample invalid categories:")
            for item in cat_results['invalid_items'][:3]:
                print(f"     - {item['product_name']}: '{item['invalid_category']}'")
        
        # Subcategory validation
        subcat_results = results['subcategories']
        print(f"\n📂 Subcategories:")
        print(f"   Valid: {subcat_results['valid_count']:,} / {subcat_results['total_checked']:,}")
        print(f"   Invalid: {subcat_results['invalid_count']:,}")
        
        if subcat_results['invalid_count'] > 0:
            print(f"   Sample invalid subcategories:")
            for item in subcat_results['invalid_items'][:3]:
                print(f"     - {item['product_name']}: '{item['category']}.{item['invalid_subcategory']}'")
        
        # Data integrity
        integrity = results['integrity']
        print(f"\n🔍 Data Integrity:")
        print(f"   Quality Score: {integrity['data_quality_score']}/100")
        if integrity['issues']:
            print(f"   Issues:")
            for issue in integrity['issues']:
                print(f"     - {issue}")
        
        # Top categories
        print(f"\n📊 Top Categories:")
        sorted_categories = sorted(results['distribution'].items(), 
                                 key=lambda x: x[1]['total_products'], reverse=True)
        for category, data in sorted_categories[:5]:
            print(f"   {category}: {data['total_products']:,} products ({data['percentage']:.1f}%)")


def main():
    """Main validation script"""
    try:
        validator = MigrationValidator()
        results = validator.run_full_validation()
        
        # Exit with appropriate code
        if results['overall_status'] == 'PASS':
            print(f"\n✅ All validations passed!")
            return 0
        elif results['overall_status'] == 'FAIL':
            print(f"\n⚠️  Validation issues found - see details above")
            return 1
        else:
            print(f"\n❌ Validation error occurred")
            return 2
            
    except Exception as e:
        print(f"❌ Validation script failed: {e}")
        return 2


if __name__ == "__main__":
    import sys
    sys.exit(main())