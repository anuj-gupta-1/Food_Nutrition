"""
Auto-standardize size units in master product file
"""

import csv
import os
from datetime import datetime

def create_unit_mapping():
    """Create comprehensive unit standardization mapping"""
    
    # Weight unit mappings
    weight_mapping = {
        # Gram variants → g
        'gm': 'g', 'Gm': 'g', 'GM': 'g', 'gram': 'g', 'grams': 'g', 
        'Gram': 'g', 'Grams': 'g', 'GRAM': 'g', 'GRAMS': 'g', 
        'gms': 'g', 'Gms': 'g', 'GMS': 'g', 'GMs': 'g', 'GRMS': 'g',
        'Grms': 'g', 'G': 'g',
        
        # Kilogram variants → kg
        'Kg': 'kg', 'KG': 'kg', 'Kilogram': 'kg', 'kilogram': 'kg'
    }
    
    # Volume unit mappings  
    volume_mapping = {
        # Milliliter variants → ml
        'Ml': 'ml', 'ML': 'ml', 'mL': 'ml', 'milliliter': 'ml',
        
        # Liter variants → L
        'l': 'L', 'Litre': 'L', 'litre': 'L', 'Liter': 'L', 'liter': 'L',
        'LITRE': 'L', 'LITER': 'L', 'Ltr': 'L', 'LTR': 'L', 'ltr': 'L'
    }
    
    # Count unit mappings
    count_mapping = {
        # Pieces variants → pcs
        'Pcs': 'pcs', 'PCS': 'pcs', 'pieces': 'pcs', 'Pieces': 'pcs',
        'Piece': 'pcs', 'piece': 'pcs',
        
        # Pack variants → pack
        'Pack': 'pack',
        
        # Sachets variants → sachets
        'Sachets': 'sachets', 'sachets': 'sachets',
        
        # Bags variants → bags
        'Bags': 'bags', 'bags': 'bags',
        
        # Tea bags variants → teabags
        'Teabags': 'teabags', 'TeaBags': 'teabags', 'teabags': 'teabags'
    }
    
    # Combine all mappings
    unit_mapping = {}
    unit_mapping.update(weight_mapping)
    unit_mapping.update(volume_mapping)
    unit_mapping.update(count_mapping)
    
    return unit_mapping

def analyze_standardization_impact():
    """Analyze what will be changed by standardization"""
    print("🔍 ANALYZING STANDARDIZATION IMPACT")
    print("=" * 60)
    
    unit_mapping = create_unit_mapping()
    
    # Read current data
    with open('data/products.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    header = lines[0].strip().split('||')
    size_unit_idx = header.index('size_unit')
    
    changes = {}
    unchanged_units = set()
    total_products = 0
    
    for line in lines[1:]:
        if line.strip():
            total_products += 1
            row = line.strip().split('||')
            if len(row) > size_unit_idx:
                current_unit = row[size_unit_idx].strip()
                if current_unit in unit_mapping:
                    new_unit = unit_mapping[current_unit]
                    if current_unit != new_unit:
                        if current_unit not in changes:
                            changes[current_unit] = {'new_unit': new_unit, 'count': 0}
                        changes[current_unit]['count'] += 1
                else:
                    unchanged_units.add(current_unit)
    
    print(f"📊 STANDARDIZATION ANALYSIS:")
    print(f"Total products: {total_products}")
    print(f"Units to be changed: {len(changes)}")
    print(f"Units remaining unchanged: {len(unchanged_units)}")
    
    total_changes = sum(change['count'] for change in changes.values())
    print(f"Total products affected: {total_changes} ({total_changes/total_products*100:.1f}%)")
    
    print(f"\n🔄 UNITS TO BE STANDARDIZED:")
    for old_unit, change_info in sorted(changes.items(), key=lambda x: x[1]['count'], reverse=True):
        print(f"  {old_unit:15} → {change_info['new_unit']:10} | {change_info['count']:5} products")
    
    print(f"\n❓ UNITS REMAINING UNCHANGED (Top 20):")
    unchanged_counts = {}
    for line in lines[1:]:
        if line.strip():
            row = line.strip().split('||')
            if len(row) > size_unit_idx:
                unit = row[size_unit_idx].strip()
                if unit in unchanged_units:
                    unchanged_counts[unit] = unchanged_counts.get(unit, 0) + 1
    
    for unit, count in sorted(unchanged_counts.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {unit:15} | {count:5} products")
    
    return changes, unchanged_units

def standardize_units():
    """Perform the actual unit standardization"""
    print(f"\n🔧 PERFORMING UNIT STANDARDIZATION")
    print("=" * 60)
    
    unit_mapping = create_unit_mapping()
    
    # Read original file
    with open('data/products.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Create backup
    backup_filename = f'data/products_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    with open(backup_filename, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"✅ Backup created: {backup_filename}")
    
    header = lines[0].strip().split('||')
    size_unit_idx = header.index('size_unit')
    
    changes_made = 0
    
    # Process each line
    standardized_lines = [lines[0]]  # Keep header as is
    
    for line in lines[1:]:
        if line.strip():
            row = line.strip().split('||')
            if len(row) > size_unit_idx:
                current_unit = row[size_unit_idx].strip()
                if current_unit in unit_mapping:
                    new_unit = unit_mapping[current_unit]
                    if current_unit != new_unit:
                        row[size_unit_idx] = new_unit
                        changes_made += 1
            
            # Reconstruct line
            standardized_line = '||'.join(row) + '\n'
            standardized_lines.append(standardized_line)
    
    # Write standardized file
    with open('data/products.csv', 'w', encoding='utf-8') as f:
        f.writelines(standardized_lines)
    
    print(f"✅ Standardization complete!")
    print(f"   Changes made: {changes_made} products")
    print(f"   Updated file: data/products.csv")
    print(f"   Backup saved: {backup_filename}")
    
    return changes_made

def validate_standardization():
    """Validate the standardization results"""
    print(f"\n✅ VALIDATING STANDARDIZATION RESULTS")
    print("=" * 60)
    
    # Read standardized file
    with open('data/products.csv', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    header = lines[0].strip().split('||')
    size_unit_idx = header.index('size_unit')
    
    unit_counts = {}
    
    for line in lines[1:]:
        if line.strip():
            row = line.strip().split('||')
            if len(row) > size_unit_idx:
                unit = row[size_unit_idx].strip()
                if unit:
                    unit_counts[unit] = unit_counts.get(unit, 0) + 1
    
    print(f"📊 POST-STANDARDIZATION UNIT DISTRIBUTION:")
    
    # Group by type
    weight_units = {}
    volume_units = {}
    count_units = {}
    other_units = {}
    
    standard_weight = ['g', 'kg']
    standard_volume = ['ml', 'L']
    standard_count = ['pcs', 'pack', 'sachets', 'bags', 'teabags']
    
    for unit, count in unit_counts.items():
        if unit in standard_weight:
            weight_units[unit] = count
        elif unit in standard_volume:
            volume_units[unit] = count
        elif unit in standard_count:
            count_units[unit] = count
        else:
            other_units[unit] = count
    
    print(f"\n⚖️  STANDARDIZED WEIGHT UNITS:")
    for unit, count in sorted(weight_units.items(), key=lambda x: x[1], reverse=True):
        print(f"  {unit:10} | {count:5} products")
    
    print(f"\n🥤 STANDARDIZED VOLUME UNITS:")
    for unit, count in sorted(volume_units.items(), key=lambda x: x[1], reverse=True):
        print(f"  {unit:10} | {count:5} products")
    
    print(f"\n🔢 STANDARDIZED COUNT UNITS:")
    for unit, count in sorted(count_units.items(), key=lambda x: x[1], reverse=True):
        print(f"  {unit:10} | {count:5} products")
    
    print(f"\n❓ REMAINING NON-STANDARD UNITS (Top 10):")
    for unit, count in sorted(other_units.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {unit:15} | {count:5} products")
    
    total_standard = sum(weight_units.values()) + sum(volume_units.values()) + sum(count_units.values())
    total_products = sum(unit_counts.values())
    standardization_pct = (total_standard / total_products) * 100
    
    print(f"\n🎯 STANDARDIZATION SUCCESS RATE:")
    print(f"   Standardized units: {total_standard} / {total_products} ({standardization_pct:.1f}%)")
    print(f"   Remaining non-standard: {len(other_units)} unique units")

def main():
    """Main standardization process"""
    print("🔧 UNIT STANDARDIZATION PROCESS")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Analyze impact
    changes, unchanged = analyze_standardization_impact()
    
    # Step 2: Confirm standardization
    total_changes = sum(change['count'] for change in changes.values())
    if total_changes > 0:
        print(f"\n⚠️  This will modify {total_changes} products")
        confirm = input("Proceed with standardization? (y/N): ").lower().strip()
        
        if confirm == 'y':
            # Step 3: Perform standardization
            changes_made = standardize_units()
            
            # Step 4: Validate results
            validate_standardization()
            
            print(f"\n🎉 Unit standardization completed successfully!")
        else:
            print("❌ Standardization cancelled")
    else:
        print("✅ No standardization needed - all units are already standard")

if __name__ == "__main__":
    main()