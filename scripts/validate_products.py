"""
Validate processed product data against schema requirements.
"""
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

def validate_size(size: Dict[str, Any]) -> List[str]:
    """Validate size field of a product."""
    errors = []
    required_fields = ["value", "unit"]
    
    for field in required_fields:
        if field not in size:
            errors.append(f"Missing required size field: {field}")
    
    if "value" in size:
        if not isinstance(size["value"], (int, float)):
            errors.append("Size value must be a number")
        elif size["value"] <= 0:
            errors.append("Size value must be positive")
    
    if "unit" in size and not isinstance(size["unit"], str):
        errors.append("Size unit must be a string")
    
    return errors

def validate_nutrient_value(value: Dict[str, Any], name: str) -> List[str]:
    """Validate a nutrient value object."""
    errors = []
    
    if "value" not in value:
        errors.append(f"Missing value in {name}")
    elif not isinstance(value["value"], (int, float)):
        errors.append(f"{name} value must be a number")
    elif value["value"] < 0:
        errors.append(f"{name} value cannot be negative")
    
    if "unit" not in value:
        errors.append(f"Missing unit in {name}")
    elif not isinstance(value["unit"], str):
        errors.append(f"{name} unit must be a string")
    
    return errors

def validate_nutrition(nutrition: Dict[str, Any]) -> List[str]:
    """Validate nutrition information of a product."""
    errors = []
    
    if "per_100g" not in nutrition:
        errors.append("Missing per_100g section in nutrition")
        return errors
    
    per_100g = nutrition["per_100g"]
    
    # Validate energy
    if "energy" in per_100g:
        energy = per_100g["energy"]
        for field in ["kcal", "kj"]:
            if field in energy and not isinstance(energy[field], (int, float)):
                errors.append(f"Energy {field} must be a number")
    
    # Validate macronutrients
    if "macronutrients" in per_100g:
        macros = per_100g["macronutrients"]
        
        # Check protein
        if "protein" in macros:
            errors.extend(validate_nutrient_value(macros["protein"], "Protein"))
        
        # Check carbohydrates
        if "carbohydrates" in macros:
            carbs = macros["carbohydrates"]
            for field in ["total", "sugars", "fiber"]:
                if field in carbs:
                    errors.extend(validate_nutrient_value(carbs[field], f"Carbohydrates {field}"))
        
        # Check fats
        if "fats" in macros:
            fats = macros["fats"]
            for field in ["total", "saturated"]:
                if field in fats:
                    errors.extend(validate_nutrient_value(fats[field], f"Fats {field}"))
    
    # Validate minerals
    if "minerals" in per_100g:
        minerals = per_100g["minerals"]
        if "sodium" in minerals:
            errors.extend(validate_nutrient_value(minerals["sodium"], "Sodium"))
    
    return errors

def validate_source_data(source_data: Dict[str, Any]) -> List[str]:
    """Validate source data information."""
    errors = []
    required_fields = ["primary_source", "sources"]
    
    for field in required_fields:
        if field not in source_data:
            errors.append(f"Missing required source_data field: {field}")
    
    if "sources" in source_data:
        if not isinstance(source_data["sources"], list):
            errors.append("sources must be a list")
        else:
            for i, source in enumerate(source_data["sources"]):
                if not isinstance(source, dict):
                    errors.append(f"Source {i} must be an object")
                    continue
                
                for field in ["id", "name", "fields_used"]:
                    if field not in source:
                        errors.append(f"Missing required field {field} in source {i}")
                
                if "fields_used" in source and not isinstance(source["fields_used"], list):
                    errors.append(f"fields_used in source {i} must be a list")
    
    return errors

def validate_product(product_data: Dict[str, Any]) -> List[str]:
    """Validate a product against the schema requirements."""
    errors = []
    
    # Check required fields
    required_fields = [
        "master_product_id",
        "name",
        "brand",
        "size",
        "category",
        "nutrition",
        "source_data",
        "last_updated"
    ]
    
    for field in required_fields:
        if field not in product_data:
            errors.append(f"Missing required field: {field}")
    
    # Validate ID format
    if "master_product_id" in product_data:
        product_id = product_data["master_product_id"]
        if not isinstance(product_id, str):
            errors.append("master_product_id must be a string")
        elif not product_id.startswith("P"):
            errors.append("master_product_id must start with 'P'")
        elif len(product_id) != 6:
            errors.append("master_product_id must be 6 characters long (P + 5 digits)")
    
    # Validate size
    if "size" in product_data:
        errors.extend(validate_size(product_data["size"]))
    
    # Validate nutrition
    if "nutrition" in product_data:
        errors.extend(validate_nutrition(product_data["nutrition"]))
    
    # Validate source data
    if "source_data" in product_data:
        errors.extend(validate_source_data(product_data["source_data"]))
    
    return errors

def validate_directory(dir_path: Path) -> List[Tuple[str, List[str]]]:
    """Validate all product files in a directory."""
    validation_results = []
    
    for file_path in dir_path.glob("*.json"):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                product_data = json.load(f)
            
            errors = validate_product(product_data)
            if errors:
                validation_results.append((str(file_path), errors))
                
        except Exception as e:
            validation_results.append((str(file_path), [f"Error reading/parsing file: {str(e)}"]))
    
    return validation_results

def main():
    base_dir = Path(__file__).parent.parent
    master_products_dir = base_dir / "data" / "master_products"
    
    # Categories to validate
    categories = ["oils", "beverages"]
    
    print("Starting data validation...")
    
    for category in categories:
        category_dir = master_products_dir / category
        if not category_dir.exists():
            print(f"\nSkipping {category} - directory not found")
            continue
            
        print(f"\nValidating {category}...")
        results = validate_directory(category_dir)
        
        if not results:
            print(f"All {category} products passed validation!")
        else:
            print(f"Found validation errors in {len(results)} {category} products:")
            for file_path, errors in results:
                print(f"\n{file_path}:")
                for error in errors:
                    print(f"  - {error}")

if __name__ == "__main__":
    main()