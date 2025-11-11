#!/usr/bin/env python3
"""
Migration Engine - Handles database migration for category changes
Applies category and subcategory updates to the product database
"""

import pandas as pd
import os
import sys
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import shutil

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'core'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

from csv_handler import load_products_csv, save_products_csv
from category_manager import CategoryManager


class MigrationEngine:
    """Handles migration of product categories and subcategories"""
    
    def __init__(self, category_manager: CategoryManager = None):
        self.category_manager = category_manager or CategoryManager()
        self.migration_stats = {
            'total_products': 0,
            'categories_changed': 0,
            'subcategories_changed': 0,
            'subcategories_split': 0,
            'errors': 0,
            'unchanged': 0
        }
    
    def create_backup(self, backup_suffix: str = None) -> str:
        """Create backup of current products.csv"""
        if backup_suffix is None:
            backup_suffix = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        backup_dir = 'data/backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        source = 'data/products.csv'
        backup_path = f'{backup_dir}/products_pre_migration_{backup_suffix}.csv'
        
        shutil.copy2(source, backup_path)
        print(f"✅ Backup created: {backup_path}")
        return backup_path
    
    def analyze_migration_impact(self, df: pd.DataFrame) -> Dict:
        """Analyze what changes will be made during migration"""
        analysis = {
            'category_changes': {},
            'subcategory_splits': {},
            'total_affected': 0,
            'by_category': {}
        }
        
        # Analyze category changes
        for _, row in df.iterrows():
            current_category = str(row.get('category', ''))
            current_subcategory = str(row.get('subcategory', ''))
            
            # Check for direct category changes
            new_category, new_subcategory = self.category_manager.find_new_category_mapping(
                current_category, current_subcategory
            )
            
            if (new_category != current_category or new_subcategory != current_subcategory):
                change_key = f"{current_category}.{current_subcategory} → {new_category}.{new_subcategory}"
                analysis['category_changes'][change_key] = analysis['category_changes'].get(change_key, 0) + 1
                analysis['total_affected'] += 1
            
            # Check for subcategory splits
            split_rules = self.category_manager.get_subcategory_splits()
            for split_rule in split_rules:
                if (split_rule['category'] == current_category and 
                    split_rule['old_subcategory'] == current_subcategory):
                    
                    split_key = f"{current_category}.{current_subcategory} (split)"
                    analysis['subcategory_splits'][split_key] = analysis['subcategory_splits'].get(split_key, 0) + 1
                    analysis['total_affected'] += 1
            
            # Count by category
            analysis['by_category'][current_category] = analysis['by_category'].get(current_category, 0) + 1
        
        return analysis
    
    def migrate_product_categories(self, df: pd.DataFrame, dry_run: bool = True) -> pd.DataFrame:
        """
        Migrate product categories and subcategories
        
        Args:
            df: Products DataFrame
            dry_run: If True, don't modify data, just analyze
            
        Returns:
            Updated DataFrame (if not dry_run)
        """
        print(f"\n{'='*80}")
        print(f"CATEGORY MIGRATION {'(DRY RUN)' if dry_run else '(APPLYING CHANGES)'}")
        print(f"{'='*80}")
        
        if dry_run:
            df_work = df.copy()
        else:
            df_work = df
        
        self.migration_stats = {
            'total_products': len(df_work),
            'categories_changed': 0,
            'subcategories_changed': 0,
            'subcategories_split': 0,
            'errors': 0,
            'unchanged': 0
        }
        
        # Process each product
        for idx, row in df_work.iterrows():
            try:
                current_category = str(row.get('category', ''))
                current_subcategory = str(row.get('subcategory', ''))
                product_name = str(row.get('product_name', ''))
                
                # Step 1: Apply direct category changes
                new_category, new_subcategory = self.category_manager.find_new_category_mapping(
                    current_category, current_subcategory
                )
                
                category_changed = False
                if new_category != current_category or new_subcategory != current_subcategory:
                    if not dry_run:
                        df_work.at[idx, 'category'] = new_category
                        df_work.at[idx, 'subcategory'] = new_subcategory
                    
                    self.migration_stats['categories_changed'] += 1
                    category_changed = True
                    
                    if idx < 5:  # Show first 5 changes
                        print(f"  Category Change: {current_category}.{current_subcategory} → {new_category}.{new_subcategory}")
                
                # Step 2: Handle subcategory splits
                final_subcategory = self.category_manager.classify_split_subcategory(
                    new_category, new_subcategory, product_name
                )
                
                if final_subcategory != new_subcategory:
                    if not dry_run:
                        df_work.at[idx, 'subcategory'] = final_subcategory
                    
                    self.migration_stats['subcategories_split'] += 1
                    
                    if idx < 5:  # Show first 5 splits
                        print(f"  Subcategory Split: {product_name[:50]}... → {final_subcategory}")
                
                if not category_changed and final_subcategory == new_subcategory:
                    self.migration_stats['unchanged'] += 1
                
            except Exception as e:
                print(f"  ❌ Error processing product {idx}: {e}")
                self.migration_stats['errors'] += 1
        
        # Print migration statistics
        self.print_migration_stats()
        
        return df_work
    
    def print_migration_stats(self) -> None:
        """Print migration statistics"""
        stats = self.migration_stats
        
        print(f"\n📊 MIGRATION STATISTICS:")
        print(f"   Total Products: {stats['total_products']:,}")
        print(f"   Categories Changed: {stats['categories_changed']:,}")
        print(f"   Subcategories Split: {stats['subcategories_split']:,}")
        print(f"   Unchanged: {stats['unchanged']:,}")
        print(f"   Errors: {stats['errors']:,}")
        
        total_changed = stats['categories_changed'] + stats['subcategories_split']
        if stats['total_products'] > 0:
            change_percentage = (total_changed / stats['total_products']) * 100
            print(f"   Change Rate: {change_percentage:.1f}%")
    
    def validate_migration_results(self, df: pd.DataFrame) -> List[str]:
        """Validate migration results"""
        issues = []
        
        # Check for invalid categories
        valid_categories = self.category_manager.get_all_categories()
        invalid_categories = df[~df['category'].isin(valid_categories)]['category'].unique()
        
        if len(invalid_categories) > 0:
            issues.append(f"Invalid categories found: {list(invalid_categories)}")
        
        # Check for invalid subcategories
        for category in valid_categories:
            valid_subcategories = self.category_manager.get_subcategories(category)
            category_products = df[df['category'] == category]
            invalid_subcategories = category_products[
                ~category_products['subcategory'].isin(valid_subcategories)
            ]['subcategory'].unique()
            
            if len(invalid_subcategories) > 0:
                issues.append(f"Invalid subcategories in {category}: {list(invalid_subcategories)}")
        
        return issues
    
    def run_full_migration(self, dry_run: bool = True) -> bool:
        """
        Run complete migration process
        
        Args:
            dry_run: If True, analyze only without making changes
            
        Returns:
            True if successful, False if errors
        """
        try:
            print(f"\n🚀 STARTING CATEGORY MIGRATION")
            print(f"Mode: {'DRY RUN (Analysis Only)' if dry_run else 'LIVE MIGRATION'}")
            
            # Load current data
            df = load_products_csv()
            print(f"✅ Loaded {len(df):,} products")
            
            # Analyze migration impact
            analysis = self.analyze_migration_impact(df)
            print(f"\n📋 MIGRATION IMPACT ANALYSIS:")
            print(f"   Total products affected: {analysis['total_affected']:,}")
            
            if analysis['category_changes']:
                print(f"   Category changes:")
                for change, count in analysis['category_changes'].items():
                    print(f"     - {change}: {count:,} products")
            
            if analysis['subcategory_splits']:
                print(f"   Subcategory splits:")
                for split, count in analysis['subcategory_splits'].items():
                    print(f"     - {split}: {count:,} products")
            
            if not dry_run and analysis['total_affected'] > 0:
                # Create backup before migration
                backup_path = self.create_backup()
                print(f"✅ Backup created: {backup_path}")
            
            # Run migration
            df_migrated = self.migrate_product_categories(df, dry_run=dry_run)
            
            if not dry_run:
                # Validate results
                validation_issues = self.validate_migration_results(df_migrated)
                if validation_issues:
                    print(f"\n⚠️  VALIDATION ISSUES:")
                    for issue in validation_issues:
                        print(f"   - {issue}")
                    return False
                
                # Save migrated data
                save_products_csv(df_migrated)
                print(f"✅ Migration completed and saved to products.csv")
            
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            return False


def main():
    """Test the MigrationEngine"""
    try:
        # Initialize
        category_manager = CategoryManager()
        migration_engine = MigrationEngine(category_manager)
        
        # Run dry run first
        print("Running migration analysis...")
        success = migration_engine.run_full_migration(dry_run=True)
        
        if success:
            print(f"\n✅ Migration analysis completed successfully")
            print(f"Run with dry_run=False to apply changes")
        else:
            print(f"\n❌ Migration analysis failed")
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()