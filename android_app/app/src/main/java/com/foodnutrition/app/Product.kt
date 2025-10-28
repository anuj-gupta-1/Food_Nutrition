package com.foodnutrition.app

import androidx.room.Embedded
import androidx.room.Entity
import androidx.room.Ignore
import androidx.room.PrimaryKey

@Entity(tableName = "products")
data class Product(
    @PrimaryKey val id: String,
    val product_name: String,
    val brand: String,
    val category: String,
    val subcategory: String? = null,
    val size_value: Double? = null,
    val size_unit: String? = null,
    val price: Double? = null,
    val source: String,
    val source_url: String? = null,
    val ingredients: String? = null,
    @Embedded val nutrition_data: NutritionData,
    val image_url: String? = null,
    val last_updated: String? = null,
    val search_count: Int = 0,
    val llm_fallback_used: Boolean = false,
    val data_quality_score: Int = 0,
    @Embedded val metadata: ProductMetadata
)

data class NutritionData(
    val available: Boolean = false,
    val standardUnit: String = "per100g",
    val nutritionSource: String = "csv_upload",
    val lastChecked: Long? = null,
    
    // Actual nutrition values (from LLM or other sources)
    val energy_kcal: Double? = null,
    val fat_g: Double? = null,
    val saturated_fat_g: Double? = null,
    val carbs_g: Double? = null,
    val sugars_g: Double? = null,
    val protein_g: Double? = null,
    val salt_g: Double? = null,
    val fiber_g: Double? = null,
    val sodium_mg: Double? = null,
    
    // LLM enhancement metadata
    val confidence_score: Double? = null,
    val response_time_ms: Long? = null,
    val from_cache: Boolean = false,
    val model_used: String? = null
)

data class NutritionValue(
    val value: Double,
    val unit: String
)

data class ProductMetadata(
    val version: Int = 2,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis(),
    val firebase_uploaded: Boolean = false
)
