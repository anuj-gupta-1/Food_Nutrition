# Data Cleanup System

Comprehensive system for cleaning up and improving product data quality with category management and LLM-based classification.

## 📁 Folder Structure

```
data_cleanup/
├── config/                    # Configuration files
│   └── category_mapping.yaml  # Category and subcategory definitions
├── core/                      # Core functionality
│   ├── category_manager.py    # Category configuration management
│   └── migration_engine.py    # Database migration engine
├── migrations/                # Migration scripts
│   ├── migrate_categories.py  # Main migration script
│   └── validate_migration.py  # Validation script
├── llm/                       # LLM classification (future)
│   ├── llm_classification_service.py
│   ├── product_classifier.py
│   └── run_trial.py
└── utils/                     # Utility functions (future)
```

## 🎯 Purpose

### 1. Category Management
- Centralized category and subcategory configuration
- Version-controlled category mappings
- Easy updates without code changes

### 2. Database Migration
- Automated category updates
- Safe migration with backups
- Dry-run testing before applying changes
- Validation and rollback capabilities

### 3. LLM Classification (Future)
- Intelligent product classification
- Clean name extraction
- Confidence scoring

## 🚀 Quick Start

### 1. View Current Category Structure
```bash
python scripts/data_cleanup/core/category_manager.py
```

### 2. Analyze Migration Impact (Dry Run)
```bash
python scripts/data_cleanup/migrations/migrate_categories.py --dry-run
```

### 3. Apply Migration
```bash
python scripts/data_cleanup/migrations/migrate_categories.py --apply
```

### 4. Validate Results
```bash
python scripts/data_cleanup/migrations/validate_migration.py
```

## 📋 Category Structure (v2.0)

### Essentials
flour, salt, sugar, dry-fruits-nuts, oil, rice, pulses, masala, wheat-soya

### Snacks
breakfast, chips, namkeen, biscuit

### Flavourings
pickles, chutney, sauce

### Beverage
tea, coffee, juice, carbonated, energy-drinks, health-drinks, syrup, other-beverages

### Spread
sauce-ketchup, butter, jam-honey, other-spreads

### Noodles/Pasta
noodles, pasta, instant-noodles

### Mithai (Sweets)
chocolate, candy, sweets, mithai, desserts

### Ready to Eat
ready-to-eat, instant-meals

### Baby
baby-food, baby-snacks

### Dairy
milk, curd, cheese, paneer, yogurt, ghee

### Bakery
cake, bread, pastry, cookies, baking-accessories

### Frozen
ice-cream, kulfi, frozen-foods

### Health
supplements, protein-powder, vitamins

## 🔄 Migration Workflow

### Phase 1: Analysis
1. Load current category configuration
2. Analyze migration impact
3. Preview changes (dry run)
4. Review statistics

### Phase 2: Backup
1. Create timestamped backup
2. Store in `data/backups/`
3. Enable rollback if needed

### Phase 3: Migration
1. Apply category changes
2. Split combined subcategories
3. Classify products using rules
4. Update database

### Phase 4: Validation
1. Validate all categories
2. Check subcategory mappings
3. Verify data integrity
4. Generate distribution report

## 🛠️ Configuration Management

### Updating Categories

Edit `config/category_mapping.yaml`:

```yaml
categories:
  new_category:
    description: "Description of category"
    subcategories:
      - subcategory1
      - subcategory2
```

### Adding Migration Rules

```yaml
migration_rules:
  category_changes:
    - from: "old_category.old_subcategory"
      to: "new_category.new_subcategory"
  
  subcategory_splits:
    - category: "category_name"
      old_subcategory: "combined-subcategory"
      new_subcategories: [subcat1, subcat2]
      classification_rules:
        - keywords: ["keyword1", "keyword2"]
          target: "subcat1"
```

## 📊 Migration Statistics

The system tracks:
- Total products processed
- Categories changed
- Subcategories split
- Unchanged products
- Errors encountered
- Change rate percentage

## ✅ Validation Checks

- Invalid categories detection
- Invalid subcategories detection
- Missing data identification
- Duplicate ID detection
- Data quality scoring
- Distribution analysis

## 🔐 Safety Features

- **Automatic Backups**: Created before any changes
- **Dry Run Mode**: Test without modifying data
- **Validation**: Pre and post-migration checks
- **Rollback**: Restore from backup if needed
- **User Confirmation**: Required for live migrations

## 📝 Best Practices

1. **Always run dry-run first**
2. **Review migration statistics**
3. **Validate after migration**
4. **Keep backups for rollback**
5. **Update configuration in version control**
6. **Test with small batches first**

## 🐛 Troubleshooting

### Migration fails
- Check YAML syntax in config file
- Verify CSV file is accessible
- Review error messages in output

### Validation issues
- Run validation script for details
- Check invalid categories/subcategories
- Review migration rules

### Rollback needed
- Locate backup in `data/backups/`
- Copy backup to `data/products.csv`
- Re-run validation

## 📚 API Reference

### CategoryManager
```python
from scripts.data_cleanup.core.category_manager import CategoryManager

manager = CategoryManager()
categories = manager.get_all_categories()
subcategories = manager.get_subcategories('essentials')
```

### MigrationEngine
```python
from scripts.data_cleanup.core.migration_engine import MigrationEngine

engine = MigrationEngine()
engine.run_full_migration(dry_run=True)
```

## 🔮 Future Enhancements

- LLM-based classification
- Clean name extraction
- Automated quality scoring
- Real-time validation
- Web-based configuration UI
