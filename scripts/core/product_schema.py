from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class NutritionFacts:
    # All values per 100g/100ml base unit
    calories: float
    protein_g: float
    carbohydrates_g: float
    fat_g: float
    fiber_g: float
    sugar_g: float
    sodium_mg: float

@dataclass
class ServingInfo:
    size: float
    unit: str  # g, ml, pieces
    description: str  # e.g. "1 biscuit", "1 packet"

@dataclass
class ProductVariant:
    id: str  # e.g. "parle_g_standard"
    name: str  # e.g. "Parle-G Original"
    size: float
    size_unit: str  # g, ml, pieces
    pack_size: Optional[int]  # Number of units in pack
    pack_description: Optional[str]  # e.g. "Family Pack", "Single Serve"
    nutrition_per_100: NutritionFacts
    serving_info: ServingInfo
    attributes: Dict[str, str]  # For flavor, type etc.

@dataclass
class Product:
    base_id: str  # e.g. "parle_g"
    brand: str  # e.g. "Parle"
    name: str  # e.g. "Parle-G"
    category: str  # e.g. "Biscuits"
    subcategory: str  # e.g. "Glucose"
    base_unit: str  # g, ml, pieces
    variants: List[ProductVariant]

# Example usage:
example_product = {
    "base_id": "parle_g",
    "brand": "Parle",
    "name": "Parle-G",
    "category": "Biscuits",
    "subcategory": "Glucose",
    "base_unit": "g",
    "variants": [
        {
            "id": "parle_g_standard",
            "name": "Parle-G Original",
            "size": 80,
            "size_unit": "g",
            "pack_size": 1,
            "pack_description": "Standard Pack",
            "nutrition_per_100": {
                "calories": 438,
                "protein_g": 7.0,
                "carbohydrates_g": 72.3,
                "fat_g": 12.4,
                "fiber_g": 1.5,
                "sugar_g": 24.2,
                "sodium_mg": 185
            },
            "serving_info": {
                "size": 20,
                "unit": "g",
                "description": "4 biscuits (20g)"
            },
            "attributes": {
                "type": "original",
                "flavor": "classic"
            }
        },
        {
            "id": "parle_g_gold",
            "name": "Parle-G Gold",
            "size": 120,
            "size_unit": "g",
            "pack_size": 1,
            "pack_description": "Premium Pack",
            "nutrition_per_100": {
                "calories": 442,
                "protein_g": 7.2,
                "carbohydrates_g": 71.8,
                "fat_g": 12.8,
                "fiber_g": 1.6,
                "sugar_g": 23.9,
                "sodium_mg": 182
            },
            "serving_info": {
                "size": 25,
                "unit": "g",
                "description": "4 biscuits (25g)"
            },
            "attributes": {
                "type": "premium",
                "flavor": "classic"
            }
        }
    ]
}