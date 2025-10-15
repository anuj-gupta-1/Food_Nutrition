package com.foodnutrition.app

import android.content.Context
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader

class CsvParser {
    
    companion object {
        private const val TAG = "CsvParser"
    }

    suspend fun parseProductsFromAssets(context: Context): List<Product> = withContext(Dispatchers.IO) {
        try {
            val inputStream = context.assets.open("products.csv")
            val reader = BufferedReader(InputStreamReader(inputStream))
            
            val products = mutableListOf<Product>()
            var lineNumber = 0
            
            reader.use { br ->
                var line: String?
                while (br.readLine().also { line = it } != null) {
                    lineNumber++
                    
                    if (lineNumber == 1) {
                        // Skip header
                        continue
                    }
                    
                    try {
                        val product = parseLineToProduct(line ?: continue)
                        if (product != null) {
                            products.add(product)
                        }
                    } catch (e: Exception) {
                        Log.w(TAG, "Error parsing line $lineNumber: ${e.message}")
                    }
                }
            }
            
            Log.d(TAG, "Successfully parsed ${products.size} products from CSV")
            products
            
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing CSV from assets", e)
            emptyList()
        }
    }
    
    private fun parseLineToProduct(line: String): Product? {
        try {
            val fields = line.split("||")
            
            if (fields.size < 17) {
                Log.w(TAG, "Insufficient fields in line: ${fields.size}")
                return null
            }
            
            val id = fields[0].trim()
            val product_name = fields[1].trim()
            val brand = fields[2].trim()
            val category = fields[3].trim()
            val subcategory = fields[4].trim().takeIf { it.isNotEmpty() }
            val size_value = fields[5].trim().toDoubleOrNull()
            val size_unit = fields[6].trim().takeIf { it.isNotEmpty() }
            val price = fields[7].trim().toDoubleOrNull()
            val source = fields[8].trim()
            val source_url = fields[9].trim().takeIf { it.isNotEmpty() }
            val ingredients = fields[10].trim().takeIf { it.isNotEmpty() }
            val nutrition_data_json = fields[11].trim()
            val image_url = fields[12].trim().takeIf { it.isNotEmpty() }
            val last_updated = fields[13].trim().takeIf { it.isNotEmpty() }
            val search_count = fields[14].trim().toIntOrNull() ?: 0
            val llm_fallback_used = fields[15].trim().toBoolean()
            val data_quality_score = fields[16].trim().toIntOrNull() ?: 0
            
            // Parse nutrition data from JSON
            val nutritionData = parseNutritionData(nutrition_data_json)
            
            return Product(
                id = id,
                product_name = product_name,
                brand = brand,
                category = category,
                subcategory = subcategory,
                size_value = size_value,
                size_unit = size_unit,
                price = price,
                source = source,
                source_url = source_url,
                ingredients = ingredients,
                nutrition_data = nutritionData,
                image_url = image_url,
                last_updated = last_updated,
                search_count = search_count,
                llm_fallback_used = llm_fallback_used,
                data_quality_score = data_quality_score,
                metadata = ProductMetadata(
                    version = 2,
                    createdAt = System.currentTimeMillis(),
                    updatedAt = System.currentTimeMillis(),
                    firebase_uploaded = false
                )
            )
            
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing line to product: ${e.message}")
            return null
        }
    }
    
    private fun parseNutritionData(jsonString: String): NutritionData {
        return try {
            if (jsonString.isEmpty() || jsonString == "{}") {
                return NutritionData(
                    available = false,
                    standardUnit = "per100g",
                    nutritionSource = "csv_upload",
                    lastChecked = System.currentTimeMillis()
                )
            }
            
            val json = JSONObject(jsonString)
            val values = mutableMapOf<String, NutritionValue>()
            
            // Parse nutrition values from JSON
            val nutritionFields = mapOf(
                "energy_kcal" to "kcal",
                "fat_g" to "g",
                "saturated_fat_g" to "g",
                "carbs_g" to "g",
                "sugars_g" to "g",
                "protein_g" to "g",
                "salt_g" to "g",
                "fiber_g" to "g",
                "sodium_mg" to "mg"
            )
            
            var hasAnyNutritionData = false
            
            nutritionFields.forEach { (field, unit) ->
                json.optDouble(field, Double.NaN).let { value ->
                    if (!value.isNaN()) {
                        values[field] = NutritionValue(value, unit)
                        hasAnyNutritionData = true
                    }
                }
            }
            
            NutritionData(
                available = hasAnyNutritionData,
                standardUnit = "per100g",
                nutritionSource = "csv_upload",
                lastChecked = System.currentTimeMillis()
            )
            
        } catch (e: Exception) {
            Log.w(TAG, "Error parsing nutrition data JSON: ${e.message}")
            NutritionData(
                available = false,
                standardUnit = "per100g",
                nutritionSource = "csv_upload",
                lastChecked = System.currentTimeMillis()
            )
        }
    }
}
