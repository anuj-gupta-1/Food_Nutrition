package com.foodnutrition.app

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json
import java.net.HttpURLConnection
import java.net.URL
import android.util.Log

@Serializable
data class NutritionRequest(
    val product_name: String,
    val brand: String,
    val category: String,
    val size_value: Double? = null,
    val size_unit: String? = null
)

@Serializable
data class NutritionResponse(
    val success: Boolean,
    val nutrition_data: Map<String, Double?>? = null,
    val confidence_score: Double? = null,
    val model_used: String? = null,
    val from_cache: Boolean? = null,
    val response_time_seconds: Double? = null,
    val error: String? = null
)

class NutritionApiService {
    companion object {
        private const val TAG = "NutritionApiService"
        private const val BASE_URL = "http://localhost:5000"  // Local API server
        private const val TIMEOUT_MS = 5000  // 5 second timeout
    }
    
    private val json = Json { 
        ignoreUnknownKeys = true
        isLenient = true
    }
    
    suspend fun fetchNutritionData(
        productName: String,
        brand: String,
        category: String,
        sizeValue: Double? = null,
        sizeUnit: String? = null
    ): Result<NutritionData> = withContext(Dispatchers.IO) {
        try {
            Log.d(TAG, "Fetching nutrition data for: $productName")
            
            val request = NutritionRequest(
                product_name = productName,
                brand = brand,
                category = category,
                size_value = sizeValue,
                size_unit = sizeUnit
            )
            
            val requestJson = json.encodeToString(NutritionRequest.serializer(), request)
            
            val url = URL("$BASE_URL/nutrition")
            val connection = url.openConnection() as HttpURLConnection
            
            connection.apply {
                requestMethod = "POST"
                setRequestProperty("Content-Type", "application/json")
                setRequestProperty("Accept", "application/json")
                doOutput = true
                connectTimeout = TIMEOUT_MS
                readTimeout = TIMEOUT_MS
            }
            
            // Send request
            connection.outputStream.use { outputStream ->
                outputStream.write(requestJson.toByteArray())
            }
            
            val responseCode = connection.responseCode
            val responseText = if (responseCode == HttpURLConnection.HTTP_OK) {
                connection.inputStream.bufferedReader().use { it.readText() }
            } else {
                connection.errorStream?.bufferedReader()?.use { it.readText() } ?: "Unknown error"
            }
            
            Log.d(TAG, "API Response ($responseCode): $responseText")
            
            if (responseCode == HttpURLConnection.HTTP_OK) {
                val response = json.decodeFromString(NutritionResponse.serializer(), responseText)
                
                if (response.success && response.nutrition_data != null) {
                    val nutritionData = NutritionData(
                        available = true,
                        standardUnit = "per100g",
                        nutritionSource = "llm_${response.model_used}",
                        lastChecked = System.currentTimeMillis(),
                        energy_kcal = response.nutrition_data["energy_kcal"],
                        fat_g = response.nutrition_data["fat_g"],
                        saturated_fat_g = response.nutrition_data["saturated_fat_g"],
                        carbs_g = response.nutrition_data["carbs_g"],
                        sugars_g = response.nutrition_data["sugars_g"],
                        protein_g = response.nutrition_data["protein_g"],
                        salt_g = response.nutrition_data["salt_g"],
                        fiber_g = response.nutrition_data["fiber_g"],
                        sodium_mg = response.nutrition_data["sodium_mg"],
                        confidence_score = response.confidence_score ?: 0.5,
                        response_time_ms = ((response.response_time_seconds ?: 0.0) * 1000).toLong(),
                        from_cache = response.from_cache ?: false
                    )
                    
                    Log.d(TAG, "Successfully fetched nutrition data in ${response.response_time_seconds}s")
                    Result.success(nutritionData)
                } else {
                    Log.w(TAG, "API returned unsuccessful response: ${response.error}")
                    Result.failure(Exception(response.error ?: "Unknown API error"))
                }
            } else {
                Log.e(TAG, "HTTP error $responseCode: $responseText")
                Result.failure(Exception("HTTP $responseCode: $responseText"))
            }
            
        } catch (e: Exception) {
            Log.e(TAG, "Error fetching nutrition data", e)
            Result.failure(e)
        }
    }
    
    suspend fun isApiAvailable(): Boolean = withContext(Dispatchers.IO) {
        try {
            val url = URL("$BASE_URL/health")
            val connection = url.openConnection() as HttpURLConnection
            connection.apply {
                requestMethod = "GET"
                connectTimeout = 2000  // 2 second timeout for health check
                readTimeout = 2000
            }
            
            val responseCode = connection.responseCode
            Log.d(TAG, "Health check response: $responseCode")
            responseCode == HttpURLConnection.HTTP_OK
            
        } catch (e: Exception) {
            Log.d(TAG, "API not available: ${e.message}")
            false
        }
    }
}

// Enhanced NutritionData with LLM fields
data class EnhancedNutritionData(
    val available: Boolean = false,
    val standardUnit: String = "per100g",
    val nutritionSource: String = "csv_upload",
    val lastChecked: Long? = null,
    
    // Nutrition values
    val energy_kcal: Double? = null,
    val fat_g: Double? = null,
    val saturated_fat_g: Double? = null,
    val carbs_g: Double? = null,
    val sugars_g: Double? = null,
    val protein_g: Double? = null,
    val salt_g: Double? = null,
    val fiber_g: Double? = null,
    val sodium_mg: Double? = null,
    
    // LLM-specific fields
    val confidence_score: Double? = null,
    val response_time_ms: Long? = null,
    val from_cache: Boolean = false,
    val model_used: String? = null
)