# Enhanced Nutrition Data Prompt Template

## Category-Agnostic Indian Food Product Nutrition Analysis

### Input Product Information:
- **Product Name**: {product_name}
- **Brand**: {brand}
- **Category**: {category}
- **Subcategory**: {subcategory}
- **Size**: {size_value} {size_unit}
- **Price**: ₹{price}
- **Source**: {source}

### Task:
You are processing a CSV batch file for Indian food product nutrition enhancement. Each row contains basic product information (name, brand, category, size, price) and you need to add comprehensive nutrition data and ingredients information.

**IMPORTANT**: The output will be used to create an enhanced CSV file with additional columns for nutrition data, ingredients, and quality metadata that will be integrated into our main food database.

### Data Sources Priority (Use in order):
1. **Official Brand Websites** (Nestle India, Britannia, Parle, ITC, etc.)
2. **FSSAI (Food Safety and Standards Authority of India)** nutrition databases
3. **Government nutrition databases** (NIN-ICMR, Indian Food Composition Tables)
4. **Verified retailer nutrition labels** (BigBasket, Amazon India, Flipkart)
5. **International databases** (USDA, only for similar products)
6. **Typical Indian market standards** for the category

### Required CSV Fields for Database Integration:

You need to provide data for these **EXACT FIELDS** that will be added to our food database:

#### Nutrition Data (per 100g/100ml):
- `energy_kcal_per_100g` - Energy in kilocalories
- `carbs_g_per_100g` - Total carbohydrates in grams  
- `total_sugars_g_per_100g` - Total sugars in grams
- `protein_g_per_100g` - Protein in grams
- `fat_g_per_100g` - Total fat in grams
- `saturated_fat_g_per_100g` - Saturated fat in grams
- `fiber_g_per_100g` - Dietary fiber in grams
- `sodium_mg_per_100g` - Sodium in milligrams
- `salt_g_per_100g` - Salt equivalent in grams

#### Product Information:
- `ingredients_list` - Comma-separated ingredients (e.g., "Water, Sugar, Orange Juice, Natural Flavors")
- `serving_size` - Typical serving size (e.g., "250ml", "30g", "4 biscuits")
- `servings_per_container` - Number of servings per package

#### Quality Metadata:
- `confidence_score` - Your confidence in data accuracy (0.6 to 1.0)
- `data_source` - Primary source used (e.g., "Nestle India official website", "FSSAI database")  
- `processing_notes` - Brief quality note (e.g., "Verified from official Indian nutrition label")

### Response Format:
Provide the data as simple field-value pairs, one per line:

```
energy_kcal_per_100g: 456
carbs_g_per_100g: 75.8
total_sugars_g_per_100g: 9.8
protein_g_per_100g: 7.1
fat_g_per_100g: 13.2
saturated_fat_g_per_100g: 6.1
fiber_g_per_100g: 2.1
sodium_mg_per_100g: 312
salt_g_per_100g: 0.78
ingredients_list: Wheat Flour, Sugar, Edible Vegetable Oil, Invert Sugar Syrup, Baking Powder, Salt, Milk Solids, Emulsifiers
serving_size: 4 biscuits (25g)
servings_per_container: 32
confidence_score: 0.95
data_source: Parle Products official nutrition label
processing_notes: Verified from official Indian product packaging
```

### Category-Specific Guidelines:

#### For All Categories:
- Use **Indian food composition standards**
- Consider **Indian cooking methods** and **local ingredients**
- Account for **Indian climate** and **storage conditions**
- Reference **FSSAI regulations** and **BIS standards**

#### Specific Considerations:
- **Dairy**: Consider Indian milk fat content (3.5-4.5%)
- **Snacks**: Account for Indian oil types (mustard, coconut, groundnut)
- **Spices/Flavourings**: Use Indian spice nutrition profiles
- **Ready-to-eat**: Consider Indian preservation methods
- **Beverages**: Account for Indian sugar content preferences
- **Essentials (flour/pulses)**: Use Indian grain varieties nutrition

### Quality Assurance:
1. **Cross-reference** with at least 2 sources
2. **Validate** against typical Indian product ranges
3. **Check** for FSSAI compliance requirements
4. **Verify** serving sizes match Indian market standards
5. **Ensure** ingredients list reflects Indian formulations

### Confidence Scoring:
- **0.9-1.0**: Official brand/FSSAI data available
- **0.8-0.9**: Government nutrition database match
- **0.7-0.8**: Verified retailer nutrition label
- **0.6-0.7**: Industry standard for similar Indian products
- **0.5-0.6**: International database with Indian adjustments
- **Below 0.5**: Estimated based on category averages

### Image Sources (if available):
- Product packaging nutrition labels
- Official brand website images
- Verified retailer product images
- FSSAI approved product listings

### Database Integration Process:
1. **Input**: CSV row with basic product info (name, brand, category, size, price)
2. **Research**: Find nutrition data using prioritized Indian sources  
3. **Extract**: Get nutrition values per 100g/100ml + ingredients + serving info
4. **Validate**: Ensure data matches Indian market standards and FSSAI requirements
5. **Output**: Field-value pairs for database integration
6. **Database**: Data will be converted and stored in our food nutrition database

### Example Processing:
**Input Product:**
- Product: "Parle-G Glucose Biscuits 800g"
- Brand: "Parle" 
- Category: "snacks"
- Size: 800g
- Price: ₹82

**Expected Output:**
```
energy_kcal_per_100g: 456
carbs_g_per_100g: 75.8
total_sugars_g_per_100g: 9.8
protein_g_per_100g: 7.1
fat_g_per_100g: 13.2
saturated_fat_g_per_100g: 6.1
fiber_g_per_100g: 2.1
sodium_mg_per_100g: 312
salt_g_per_100g: 0.78
ingredients_list: Wheat Flour, Sugar, Edible Vegetable Oil, Invert Sugar Syrup, Baking Powder, Salt, Milk Solids, Emulsifiers
serving_size: 4 biscuits (25g)
servings_per_container: 32
confidence_score: 0.95
data_source: Parle Products official nutrition label
processing_notes: Verified from official Indian product packaging
```

### Critical Requirements:
- **Use EXACT field names** as specified (with _per_100g suffix for nutrition)
- **Prioritize accuracy over completeness** - use "null" for uncertain values
- **Focus on Indian market formulations** - not international variants  
- **Include realistic serving sizes** for Indian consumption patterns
- **Provide confidence scores** based on source reliability (0.6-1.0)
- **Use comma-separated ingredients** (not bullet points or arrays)

### Output Format:
Provide ONLY the field-value pairs as shown above. No additional text, explanations, or formatting.