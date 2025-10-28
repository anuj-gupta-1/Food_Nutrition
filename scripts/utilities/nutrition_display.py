from typing import Dict, Optional
from dataclasses import dataclass
from product_schema import Product, ProductVariant, NutritionFacts

class NutritionDisplay:
    @staticmethod
    def calculate_nutrition_for_size(
        nutrition_per_100: NutritionFacts,
        target_size: float,
        target_unit: str,
        base_unit: str
    ) -> NutritionFacts:
        # Convert to common unit if needed (e.g., g to ml for liquids)
        conversion_factor = target_size / 100
        
        return NutritionFacts(
            calories=nutrition_per_100.calories * conversion_factor,
            protein_g=nutrition_per_100.protein_g * conversion_factor,
            carbohydrates_g=nutrition_per_100.carbohydrates_g * conversion_factor,
            fat_g=nutrition_per_100.fat_g * conversion_factor,
            fiber_g=nutrition_per_100.fiber_g * conversion_factor,
            sugar_g=nutrition_per_100.sugar_g * conversion_factor,
            sodium_mg=nutrition_per_100.sodium_mg * conversion_factor
        )

    @staticmethod
    def format_nutrition_display(
        variant: ProductVariant,
        display_size: Optional[float] = None,
        display_unit: Optional[str] = None
    ) -> Dict:
        # Default to serving size if no display size provided
        size = display_size or variant.serving_info.size
        unit = display_unit or variant.serving_info.unit
        
        # Calculate nutrition for target size
        nutrition = NutritionDisplay.calculate_nutrition_for_size(
            variant.nutrition_per_100,
            size,
            unit,
            variant.size_unit
        )
        
        return {
            "product_info": {
                "name": variant.name,
                "size": f"{variant.size}{variant.size_unit}",
                "pack_info": f"{variant.pack_size} {variant.pack_description}" if variant.pack_size else None,
                "attributes": variant.attributes
            },
            "display_size": {
                "amount": size,
                "unit": unit,
                "description": variant.serving_info.description
            },
            "nutrition_facts": {
                "per_serving": {
                    "calories": f"{nutrition.calories:.1f} kcal",
                    "protein": f"{nutrition.protein_g:.1f}g",
                    "carbohydrates": f"{nutrition.carbohydrates_g:.1f}g",
                    "fat": f"{nutrition.fat_g:.1f}g",
                    "fiber": f"{nutrition.fiber_g:.1f}g",
                    "sugar": f"{nutrition.sugar_g:.1f}g",
                    "sodium": f"{nutrition.sodium_mg:.0f}mg"
                },
                "per_100": {
                    "calories": f"{variant.nutrition_per_100.calories:.1f} kcal",
                    "protein": f"{variant.nutrition_per_100.protein_g:.1f}g",
                    "carbohydrates": f"{variant.nutrition_per_100.carbohydrates_g:.1f}g",
                    "fat": f"{variant.nutrition_per_100.fat_g:.1f}g",
                    "fiber": f"{variant.nutrition_per_100.fiber_g:.1f}g",
                    "sugar": f"{variant.nutrition_per_100.sugar_g:.1f}g",
                    "sodium": f"{variant.nutrition_per_100.sodium_mg:.0f}mg"
                }
            }
        }

# Example usage
"""
# Display nutrition for a serving
display = NutritionDisplay.format_nutrition_display(product.variants[0])

# Display nutrition for custom size (e.g., whole packet)
display = NutritionDisplay.format_nutrition_display(
    product.variants[0],
    display_size=80,
    display_unit="g"
)
"""