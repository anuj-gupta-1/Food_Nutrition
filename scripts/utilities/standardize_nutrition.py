# standardize_nutrition.py
"""
Read data/products.csv, parse nutrition_json, and add standardized columns for key nutrients per 100g/ml.
Write the updated data (with new columns) back to data/products.csv, preserving all original columns.
"""
import csv
import json
import os

INPUT_CSV = 'data/products.csv'
OUTPUT_CSV = 'data/products.csv'  # Overwrite for simplicity

STANDARD_FIELDS = [
    ('energy_kcal_100g', ['energy-kcal_100g', 'energy-kcal_value', 'energy-kcal']),
    ('fat_100g', ['fat_100g', 'fat-value', 'fat']),
    ('saturated_fat_100g', ['saturated-fat_100g', 'saturated-fat-value', 'saturated-fat']),
    ('carbs_100g', ['carbohydrates_100g', 'carbohydrates-value', 'carbohydrates']),
    ('sugars_100g', ['sugars_100g', 'sugars-value', 'sugars']),
    ('protein_100g', ['proteins_100g', 'proteins-value', 'proteins']),
    ('salt_100g', ['salt_100g', 'salt-value', 'salt']),
    ('fiber_100g', ['fiber_100g', 'fiber-value', 'fiber']),
    ('sodium_100g', ['sodium_100g', 'sodium-value', 'sodium']),
]

def extract_value(nutrition, keys):
    for key in keys:
        val = nutrition.get(key)
        if val is not None and val != '':
            try:
                return float(val)
            except Exception:
                continue
    return ''

def main():
    with open(INPUT_CSV, newline='', encoding='utf-8') as infile:
        reader = list(csv.DictReader(infile))
        fieldnames = reader[0].keys()
        # Add new columns if not present
        new_fields = [f[0] for f in STANDARD_FIELDS if f[0] not in fieldnames]
        all_fields = list(fieldnames) + new_fields

    # Prepare new rows
    new_rows = []
    for row in reader:
        nutrition = {}
        try:
            nutrition = json.loads(row.get('nutrition_json', '{}'))
        except Exception:
            pass
        for out_col, keys in STANDARD_FIELDS:
            row[out_col] = extract_value(nutrition, keys)
        new_rows.append(row)

    # Write back to CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=all_fields)
        writer.writeheader()
        for row in new_rows:
            writer.writerow(row)
    print(f"Standardized nutrition columns added to {OUTPUT_CSV}")

if __name__ == '__main__':
    main() 