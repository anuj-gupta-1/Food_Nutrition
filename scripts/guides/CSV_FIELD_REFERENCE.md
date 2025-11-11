# CSV Field Reference Guide

## 📋 **Complete Field List (26 Columns)**

### **INPUT COLUMNS (1-11) - READ ONLY**
| Column | Field Name | Description | Example |
|--------|------------|-------------|---------|
| 1 | `batch_id` | Sequential number | 1, 2, 3... |
| 2 | `original_product_id` | Database ID | jiomart_coca_cola_750ml |
| 3 | `product_name` | Product name | Coca Cola 750ml |
| 4 | `brand` | Brand name | Coca Cola |
| 5 | `category` | Product category | beverage |
| 6 | `subcategory` | Subcategory | soft-drink |
| 7 | `size_value` | Package size | 750 |
| 8 | `size_unit` | Size unit | ml |
| 9 | `price` | Price in rupees | 36.0 |
| 10 | `source` | Data source | jiomart |
| 11 | `quality_score` | Quality rating | 5 |

### **OUTPUT COLUMNS (12-26) - FILL THESE**
| Column | Field Name | Data Type | Example | Notes |
|--------|------------|-----------|---------|-------|
| 12 | `ingredients_list` | Text | "Water, Sugar, Natural Flavors" | Comma-separated, most to least |
| 13 | `energy_kcal_per_100g` | Number | 42 | Energy per 100g/100ml |
| 14 | `carbs_g_per_100g` | Number | 10.6 | Total carbohydrates |
| 15 | `total_sugars_g_per_100g` | Number | 10.6 | Total sugars |
| 16 | `protein_g_per_100g` | Number | 0 | Protein content |
| 17 | `fat_g_per_100g` | Number | 0 | Total fat |
| 18 | `saturated_fat_g_per_100g` | Number | 0 | Saturated fat |
| 19 | `fiber_g_per_100g` | Number | 0 | Dietary fiber |
| 20 | `sodium_mg_per_100g` | Number | 4 | Sodium in milligrams |
| 21 | `salt_g_per_100g` | Number | 0.01 | Salt (sodium ÷ 400) |
| 22 | `serving_size` | Text | "250ml" | Typical serving |
| 23 | `servings_per_container` | Number | 3 | Servings in package |
| 24 | `confidence_score` | Number | 0.9 | Your confidence (0.6-1.0) |
| 25 | `data_source` | Text | "Official website" | Primary source used |
| 26 | `processing_notes` | Text | "Indian formulation verified" | Notes/assumptions |

## 🎯 **Key Points**

### **Data Format Requirements**
- **Numbers only** in nutrition columns (no units like "g" or "ml")
- **Decimal values** allowed (e.g., 10.6, 0.01)
- **Text in quotes** for ingredients and notes
- **Per 100g/100ml** for all nutrition values

### **Common Calculations**
- **Salt from Sodium**: salt_g = sodium_mg ÷ 400
- **Servings per Container**: package_size ÷ serving_size
- **Zero Values**: Use 0 for nutrients not present (like protein in water)

### **Quality Thresholds**
- **≥0.8**: Official sources, high confidence
- **0.6-0.8**: Good databases, medium confidence  
- **<0.6**: Skip entire row (too uncertain)

## 📊 **Example by Product Type**

### **Soft Drink (Coca Cola)**
```csv
12,ingredients_list,"Carbonated Water, Sugar, Natural Flavors, Caramel Color, Phosphoric Acid, Caffeine"
13,energy_kcal_per_100g,42
14,carbs_g_per_100g,10.6
15,total_sugars_g_per_100g,10.6
16,protein_g_per_100g,0
17,fat_g_per_100g,0
18,saturated_fat_g_per_100g,0
19,fiber_g_per_100g,0
20,sodium_mg_per_100g,4
21,salt_g_per_100g,0.01
22,serving_size,"250ml"
23,servings_per_container,3
24,confidence_score,0.9
25,data_source,"Coca Cola India official website"
26,processing_notes,"Indian formulation verified"
```

### **Water (Bisleri)**
```csv
12,ingredients_list,"Purified Water"
13,energy_kcal_per_100g,0
14,carbs_g_per_100g,0
15,total_sugars_g_per_100g,0
16,protein_g_per_100g,0
17,fat_g_per_100g,0
18,saturated_fat_g_per_100g,0
19,fiber_g_per_100g,0
20,sodium_mg_per_100g,1
21,salt_g_per_100g,0.0025
22,serving_size,"250ml"
23,servings_per_container,4
24,confidence_score,0.95
25,data_source,"Industry standard for purified water"
26,processing_notes,"Standard purified water composition"
```

### **Fruit Juice (Real)**
```csv
12,ingredients_list,"Water, Apple Juice Concentrate, Sugar, Natural Flavors, Vitamin C"
13,energy_kcal_per_100g,48
14,carbs_g_per_100g,12
15,total_sugars_g_per_100g,11.5
16,protein_g_per_100g,0.1
17,fat_g_per_100g,0
18,saturated_fat_g_per_100g,0
19,fiber_g_per_100g,0.2
20,sodium_mg_per_100g,2
21,salt_g_per_100g,0.005
22,serving_size,"200ml"
23,servings_per_container,5
24,confidence_score,0.8
25,data_source,"Dabur Real official nutrition facts"
26,processing_notes,"Indian market formulation with added Vitamin C"
```

## ✅ **Validation Checklist**

Before submitting, verify:
- [ ] All 15 output columns (12-26) filled for each product
- [ ] Numbers only in nutrition columns
- [ ] Confidence scores between 0.6-1.0
- [ ] Ingredients in order (most to least quantity)
- [ ] Salt calculated from sodium (÷ 400)
- [ ] Serving calculations make sense
- [ ] Data sources noted
- [ ] Processing notes explain assumptions

**This ensures perfect integration into the database!** 🎯