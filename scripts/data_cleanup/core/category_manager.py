#!/usr/bin/env python3
"""
Category Manager - Handles category and subcategory configuration
Provides centralized management of product categorization rules
"""

import yaml
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class CategoryManager:
    """Manages product category and subcategory configuration"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Default path relative to this file
            config_dir = os.path.join(os.path.dirname(__file__), '..', 'config')
            config_path = os.path.join(config_dir, 'category_mapping.yaml')
        
        self.config_path = config_path
        self.config = None
        self.load_config()
    
    def load_config(self) -> None:
        """Load category configuration from YAML file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            print(f"✅ Loaded category config from {self.config_path}")
        except FileNotFoundError:
            raise FileNotFoundError(f"Category config file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in config file: {e}")
    
    def get_all_categories(self) -> List[str]:
        """Get list of all available categories"""
        return list(self.config['categories'].keys())
    
    def get_subcategories(self, category: str) -> List[str]:
        """Get list of subcategories for a given category"""
        category_config = self.config['categories'].get(category)
        if not category_config:
            return []
        return category_config.get('subcategories', [])
    
    def get_category_description(self, category: str) -> str:
        """Get description for a category"""
        category_config = self.config['categories'].get(category, {})
        return category_config.get('description', '')
    
    def is_valid_category(self, category: str) -> bool:
        """Check if category exists in configuration"""
        return category in self.config['categories']
    
    def is_valid_subcategory(self, category: str, subcategory: str) -> bool:
        """Check if subcategory is valid for given category"""
        valid_subcategories = self.get_subcategories(category)
        return subcategory in valid_subcategories
    
    def get_migration_rules(self) -> Dict:
        """Get migration rules for updating existing data"""
        return self.config.get('migration_rules', {})
    
    def get_category_changes(self) -> List[Dict]:
        """Get list of category change rules"""
        migration_rules = self.get_migration_rules()
        return migration_rules.get('category_changes', [])
    
    def get_subcategory_splits(self) -> List[Dict]:
        """Get list of subcategory split rules"""
        migration_rules = self.get_migration_rules()
        return migration_rules.get('subcategory_splits', [])
    
    def find_new_category_mapping(self, old_category: str, old_subcategory: str) -> Tuple[str, str]:
        """
        Find new category/subcategory mapping for old values
        Returns: (new_category, new_subcategory)
        """
        # Check direct category changes
        for change in self.get_category_changes():
            old_path = change['from']
            new_path = change['to']
            
            if old_path == f"{old_category}.{old_subcategory}":
                new_category, new_subcategory = new_path.split('.')
                return new_category, new_subcategory
        
        # If no direct mapping found, return original
        return old_category, old_subcategory
    
    def classify_split_subcategory(self, category: str, old_subcategory: str, 
                                  product_name: str) -> str:
        """
        Classify product into new subcategory when splitting combined subcategories
        """
        # Find split rule for this category and subcategory
        for split_rule in self.get_subcategory_splits():
            if (split_rule['category'] == category and 
                split_rule['old_subcategory'] == old_subcategory):
                
                # Check classification rules
                for rule in split_rule['classification_rules']:
                    keywords = rule['keywords']
                    target = rule['target']
                    
                    # Check if any keyword matches product name
                    product_lower = product_name.lower()
                    for keyword in keywords:
                        if keyword.lower() in product_lower:
                            return target
                
                # If no keyword matches, return first new subcategory as default
                return split_rule['new_subcategories'][0]
        
        # If no split rule found, return original subcategory
        return old_subcategory
    
    def get_config_metadata(self) -> Dict:
        """Get configuration metadata"""
        return self.config.get('metadata', {})
    
    def get_validation_rules(self) -> Dict:
        """Get validation rules"""
        return self.config.get('validation', {})
    
    def validate_category_structure(self) -> List[str]:
        """
        Validate the category structure and return list of issues
        """
        issues = []
        validation_rules = self.get_validation_rules()
        
        # Check each category
        for category, config in self.config['categories'].items():
            subcategories = config.get('subcategories', [])
            
            # Check subcategory count limits
            max_subcat = validation_rules.get('category_constraints', {}).get('max_subcategories_per_category', 15)
            min_subcat = validation_rules.get('category_constraints', {}).get('min_subcategories_per_category', 1)
            
            if len(subcategories) > max_subcat:
                issues.append(f"Category '{category}' has too many subcategories ({len(subcategories)} > {max_subcat})")
            
            if len(subcategories) < min_subcat:
                issues.append(f"Category '{category}' has too few subcategories ({len(subcategories)} < {min_subcat})")
            
            # Check for duplicate subcategories
            if len(subcategories) != len(set(subcategories)):
                issues.append(f"Category '{category}' has duplicate subcategories")
        
        return issues
    
    def export_flat_mapping(self) -> Dict[str, List[str]]:
        """
        Export category mapping as flat dictionary for easy use
        Returns: {category: [subcategory1, subcategory2, ...]}
        """
        flat_mapping = {}
        for category, config in self.config['categories'].items():
            flat_mapping[category] = config.get('subcategories', [])
        return flat_mapping
    
    def get_stats(self) -> Dict:
        """Get statistics about the category configuration"""
        categories = self.get_all_categories()
        total_subcategories = sum(len(self.get_subcategories(cat)) for cat in categories)
        
        return {
            'total_categories': len(categories),
            'total_subcategories': total_subcategories,
            'avg_subcategories_per_category': round(total_subcategories / len(categories), 2),
            'categories': categories,
            'config_version': self.get_config_metadata().get('version', 'unknown'),
            'last_updated': self.get_config_metadata().get('last_updated', 'unknown')
        }
    
    def print_structure(self) -> None:
        """Print the complete category structure"""
        print("\n" + "="*80)
        print("CATEGORY STRUCTURE")
        print("="*80)
        
        for category in self.get_all_categories():
            subcategories = self.get_subcategories(category)
            description = self.get_category_description(category)
            
            print(f"\n📁 {category.upper()} ({len(subcategories)} subcategories)")
            if description:
                print(f"   {description}")
            
            for subcat in subcategories:
                print(f"   └── {subcat}")
        
        # Print stats
        stats = self.get_stats()
        print(f"\n📊 STATISTICS:")
        print(f"   Total Categories: {stats['total_categories']}")
        print(f"   Total Subcategories: {stats['total_subcategories']}")
        print(f"   Average per Category: {stats['avg_subcategories_per_category']}")
        print(f"   Config Version: {stats['config_version']}")


def main():
    """Test the CategoryManager"""
    try:
        manager = CategoryManager()
        
        # Print structure
        manager.print_structure()
        
        # Validate structure
        issues = manager.validate_category_structure()
        if issues:
            print(f"\n⚠️  VALIDATION ISSUES:")
            for issue in issues:
                print(f"   - {issue}")
        else:
            print(f"\n✅ Category structure is valid")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()