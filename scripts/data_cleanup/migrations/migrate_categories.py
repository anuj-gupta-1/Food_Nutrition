#!/usr/bin/env python3
"""
Category Migration Script
Main script to migrate product categories and subcategories
"""

import sys
import os
import argparse
from datetime import datetime

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from category_manager import CategoryManager
from migration_engine import MigrationEngine


def main():
    """Main migration script"""
    parser = argparse.ArgumentParser(description='Migrate product categories and subcategories')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Analyze migration impact without making changes')
    parser.add_argument('--apply', action='store_true',
                       help='Apply migration changes to database')
    parser.add_argument('--force', action='store_true',
                       help='Force migration even if validation issues exist')
    parser.add_argument('--backup-suffix', type=str,
                       help='Custom suffix for backup file')
    
    args = parser.parse_args()
    
    # Default to dry-run if no action specified
    if not args.dry_run and not args.apply:
        args.dry_run = True
        print("No action specified, defaulting to --dry-run")
    
    try:
        print("="*80)
        print("PRODUCT CATEGORY MIGRATION TOOL")
        print("="*80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize managers
        print("\n🔧 Initializing migration system...")
        category_manager = CategoryManager()
        migration_engine = MigrationEngine(category_manager)
        
        # Show current category structure
        print("\n📋 Current Category Structure:")
        category_manager.print_structure()
        
        # Validate category configuration
        print("\n🔍 Validating category configuration...")
        issues = category_manager.validate_category_structure()
        if issues:
            print("⚠️  Configuration issues found:")
            for issue in issues:
                print(f"   - {issue}")
            
            if not args.force:
                print("\nUse --force to proceed despite issues")
                return 1
        else:
            print("✅ Category configuration is valid")
        
        # Run migration
        if args.dry_run:
            print("\n🔍 Running migration analysis (dry run)...")
            success = migration_engine.run_full_migration(dry_run=True)
            
            if success:
                print("\n" + "="*80)
                print("DRY RUN COMPLETED SUCCESSFULLY")
                print("="*80)
                print("To apply these changes, run:")
                print("python scripts/data_cleanup/migrations/migrate_categories.py --apply")
            else:
                print("\n❌ Dry run failed - check errors above")
                return 1
        
        elif args.apply:
            print("\n🚀 Applying migration changes...")
            
            # Confirm with user
            response = input("\n⚠️  This will modify your product database. Continue? (y/N): ")
            if response.lower() != 'y':
                print("Migration cancelled by user")
                return 0
            
            success = migration_engine.run_full_migration(dry_run=False)
            
            if success:
                print("\n" + "="*80)
                print("MIGRATION COMPLETED SUCCESSFULLY")
                print("="*80)
                print("✅ Product categories have been updated")
                print("✅ Backup created for rollback if needed")
                print("\nNext steps:")
                print("1. Test your application with updated categories")
                print("2. Update LLM classifier with new category mappings")
                print("3. Run validation tests")
            else:
                print("\n❌ Migration failed - check errors above")
                print("Your original data is safe (backup created)")
                return 1
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Migration interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Migration failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)