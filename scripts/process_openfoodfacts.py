"""
Process raw OpenFoodFacts data files and convert them to our standardized format.
"""
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

def read_json_file(file_path: str) -> Dict[str, Any]:
    """Read a JSON file and return its contents."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_nutrients(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract and standardize nutrition information."""
    nutrients = {
        "per_100g": {
            "energy": {},
            "macronutrients": {
                "protein": {},
                "carbohydrates": {
                    "total": {},
                    "sugars": {},
                    "fiber": {}
                },
                "fats": {
                    "total": {},
                    "saturated": {}
                }
            },
            "minerals": {
                "sodium": {}
            }
        }
    }
    
    # Extract nutriments data if available
    if "nutriments" in product_data:
        nutr = product_data["nutriments"]
        
        # Energy
        if "energy-kcal_100g" in nutr:
            nutrients["per_100g"]["energy"]["kcal"] = nutr["energy-kcal_100g"]
        if "energy-kj_100g" in nutr:
            nutrients["per_100g"]["energy"]["kj"] = nutr["energy-kj_100g"]
            
        # Macronutrients
        if "proteins_100g" in nutr:
            nutrients["per_100g"]["macronutrients"]["protein"] = {
                "value": nutr["proteins_100g"],
                "unit": "g"
            }
            
        if "carbohydrates_100g" in nutr:
            nutrients["per_100g"]["macronutrients"]["carbohydrates"]["total"] = {
                "value": nutr["carbohydrates_100g"],
                "unit": "g"
            }
            
        if "sugars_100g" in nutr:
            nutrients["per_100g"]["macronutrients"]["carbohydrates"]["sugars"] = {
                "value": nutr["sugars_100g"],
                "unit": "g"
            }
            
        if "fiber_100g" in nutr:
            nutrients["per_100g"]["macronutrients"]["carbohydrates"]["fiber"] = {
                "value": nutr["fiber_100g"],
                "unit": "g"
            }
            
        if "fat_100g" in nutr:
            nutrients["per_100g"]["macronutrients"]["fats"]["total"] = {
                "value": nutr["fat_100g"],
                "unit": "g"
            }
            
        if "saturated-fat_100g" in nutr:
            nutrients["per_100g"]["macronutrients"]["fats"]["saturated"] = {
                "value": nutr["saturated-fat_100g"],
                "unit": "g"
            }
            
        if "sodium_100g" in nutr:
            nutrients["per_100g"]["minerals"]["sodium"] = {
                "value": nutr["sodium_100g"],
                "unit": "g"
            }
            
        # Add serving size if available
        if "serving_size" in product_data:
            nutrients["serving_size"] = product_data["serving_size"]
            
    return nutrients

def standardize_product(product_data: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Convert OpenFoodFacts product data to our standard format."""
    # Extract product ID and ensure it's properly formatted
    raw_id = product_data.get('_id', 'UNKNOWN')
    product_id = f"P{int(raw_id):05d}" if raw_id.isdigit() else f"P{hash(raw_id) % 100000:05d}"
    
    # Extract quantity and unit from the quantity string
    quantity_str = product_data.get("quantity", "")
    size = {"value": 100, "unit": "g"}  # Default values
    
    # Try to parse quantity string (e.g., "500 g", "1 L", etc.)
    if quantity_str:
        parts = quantity_str.split()
        if len(parts) >= 2:
            try:
                size["value"] = float(parts[0])
                size["unit"] = parts[1].lower()
            except ValueError:
                pass
    
    standardized = {
        "master_product_id": product_id,
        "name": product_data.get("product_name", ""),
        "brand": product_data.get("brands", ""),
        "size": size,
        "category": category,
        "subcategory": "",  # To be determined based on detailed categorization
        "nutrition": extract_nutrients(product_data),
        "source_data": {
            "primary_source": "openfoodfacts",
            "sources": [{
                "id": product_data.get("_id", ""),
                "name": "openfoodfacts",
                "fields_used": ["nutrition", "product_info"],
                "url": product_data.get("url", "")
            }]
        },
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }
    
    return standardized

def process_category(input_dir: Path, output_dir: Path, category: str) -> None:
    """Process all files in a category directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for file_path in input_dir.glob("*.json"):
        try:
            # Read source data
            product_data = read_json_file(str(file_path))
            
            # Convert to standard format
            standardized = standardize_product(product_data, category)
            
            # Save to output directory
            output_file = output_dir / f"{standardized['master_product_id']}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(standardized, f, indent=2, ensure_ascii=False)
                
            print(f"Processed: {file_path.name} -> {output_file.name}")
            
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")

def find_files_by_prefix(directory: Path, prefix: str) -> List[Path]:
    """Find all files in directory that start with the given prefix."""
    return [f for f in directory.iterdir() if f.is_file() and f.name.startswith(prefix)]

def process_all_categories():
    """Process all product categories."""
    base_dir = Path(__file__).parent.parent
    raw_data_dir = base_dir / "raw_data" / "openfoodfacts"
    master_products_dir = base_dir / "data" / "master_products"
    
    # Define categories to process
    categories = {
        "oils": ("oils_", "Oils"),
        "beverages": ("sweetened-beverages_", "Beverages")
    }
    
    # Process each category
    for category, (prefix, category_name) in categories.items():
        print(f"\nProcessing {category_name}...")
        output_dir = master_products_dir / category
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all files for this category
        input_files = find_files_by_prefix(raw_data_dir, prefix)
        
        for input_file in input_files:
            try:
                product_data = read_json_file(str(input_file))
                standardized = standardize_product(product_data, category_name)
                
                output_file = output_dir / f"{standardized['master_product_id']}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(standardized, f, indent=2, ensure_ascii=False)
                    
                print(f"Processed: {input_file.name} -> {output_file.name}")
                
            except Exception as e:
                print(f"Error processing {input_file}: {str(e)}")

if __name__ == "__main__":
    process_all_categories()