import json
from typing import Dict, Optional
from dataclasses import dataclass
from product_schema import Product, ProductVariant, NutritionFacts, ServingInfo

class ProductHandler:
    def __init__(self, data_file: str):
        with open(data_file, 'r') as f:
            self.raw_data = json.load(f)
    
    def get_product_variant(self, product_id: str, variant_id: str) -> Optional[Dict]:
        """Get specific product variant"""
        if product_id not in self.raw_data:
            return None
            
        product = self.raw_data[product_id]
        for variant in product['variants']:
            if variant['id'] == variant_id:
                return variant
        return None

    def calculate_nutrition(self, variant: Dict, target_size: float) -> Dict:
        """Calculate nutrition for a specific size"""
        factor = target_size / 100
        nutrition = variant['nutrition_per_100']
        
        return {
            key: value * factor
            for key, value in nutrition.items()
        }

    def format_display(self, product_id: str, variant_id: str, display_size: Optional[float] = None) -> Dict:
        """Format product data for display"""
        variant = self.get_product_variant(product_id, variant_id)
        if not variant:
            return None
            
        # Use serving size if no display size provided
        size = display_size or variant['serving_info']['size']
        
        # Calculate nutrition for target size
        nutrition = self.calculate_nutrition(variant, size)
        
        return {
            "product_info": {
                "name": variant['name'],
                "brand": self.raw_data[product_id]['brand'],
                "pack_size": f"{variant['size']}{variant['size_unit']}",
                "pack_type": variant['pack_description'],
                "attributes": variant['attributes']
            },
            "nutrition_display": {
                "size_info": {
                    "amount": size,
                    "unit": variant['size_unit'],
                    "description": f"Per {variant['serving_info']['description']}" if size == variant['serving_info']['size'] else f"Per {size}{variant['size_unit']}"
                },
                "values": {
                    "calories": f"{nutrition['calories']:.1f} kcal",
                    "protein": f"{nutrition['protein_g']:.1f}g",
                    "carbohydrates": f"{nutrition['carbohydrates_g']:.1f}g",
                    "fat": f"{nutrition['fat_g']:.1f}g",
                    "fiber": f"{nutrition['fiber_g']:.1f}g",
                    "sugar": f"{nutrition['sugar_g']:.1f}g",
                    "sodium": f"{nutrition['sodium_mg']:.0f}mg"
                },
                "reference_values": {
                    "per_100g": variant['nutrition_per_100'],
                    "per_serving": self.calculate_nutrition(
                        variant, 
                        variant['serving_info']['size']
                    )
                }
            }
        }

# Example usage
if __name__ == "__main__":
    handler = ProductHandler('raw_products.json')
    
    # Display nutrition for regular pack serving
    print("\nRegular Pack - Per Serving:")
    print(json.dumps(
        handler.format_display('parle_g', 'parle_g_standard'),
        indent=2
    ))
    
    # Display nutrition for whole packet
    print("\nRegular Pack - Whole Packet:")
    print(json.dumps(
        handler.format_display('parle_g', 'parle_g_standard', 70),
        indent=2
    ))
    
    # Display nutrition for Gold variant serving
    print("\nGold Variant - Per Serving:")
    print(json.dumps(
        handler.format_display('parle_g', 'parle_g_gold'),
        indent=2
    ))