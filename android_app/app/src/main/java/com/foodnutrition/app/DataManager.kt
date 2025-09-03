package com.foodnutrition.app

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.File
import java.io.FileOutputStream
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*

class DataManager(private val context: Context, private val dao: ProductDao) {
    
    companion object {
        private const val PREFS_NAME = "food_nutrition_prefs"
        private const val LAST_FETCH_KEY = "last_fetch"
        private const val CACHE_FILE_NAME = "products_cache.csv"
        private const val CSV_URL = "https://food-nutririon.firebaseapp.com/products.csv"
        private const val CACHE_VALIDITY_DAYS = 7
    }
    
    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val csvParser = CsvParser()
    
    suspend fun initializeData() = withContext(Dispatchers.IO) {
        try {
            // Check if we need to refresh data
            if (shouldRefreshData()) {
                fetchAndUpdateData()
            } else {
                // Load from cache if available
                loadFromCache()
            }
        } catch (e: Exception) {
            // Fallback to cache or assets if network fails
            loadFromCache()
        }
    }
    
    private fun shouldRefreshData(): Boolean {
        val lastFetch = prefs.getLong(LAST_FETCH_KEY, 0)
        if (lastFetch == 0L) return true
        
        val daysSinceLastFetch = (System.currentTimeMillis() - lastFetch) / (1000 * 60 * 60 * 24)
        return daysSinceLastFetch >= CACHE_VALIDITY_DAYS
    }
    
    private suspend fun fetchAndUpdateData() = withContext(Dispatchers.IO) {
        try {
            val url = URL(CSV_URL)
            val connection = url.openConnection() as HttpURLConnection
            connection.requestMethod = "GET"
            connection.setRequestProperty("User-Agent", "FoodNutritionApp/1.0")
            
            // Check if file was modified using ETag
            val cachedETag = prefs.getString("etag", null)
            if (cachedETag != null) {
                connection.setRequestProperty("If-None-Match", cachedETag)
            }
            
            val responseCode = connection.responseCode
            
            if (responseCode == HttpURLConnection.HTTP_NOT_MODIFIED) {
                // File hasn't changed, use cache
                loadFromCache()
                return@withContext
            }
            
            if (responseCode == HttpURLConnection.HTTP_OK) {
                // Download and cache the file
                val inputStream = connection.inputStream
                val cacheFile = File(context.cacheDir, CACHE_FILE_NAME)
                
                FileOutputStream(cacheFile).use { output ->
                    inputStream.copyTo(output)
                }
                
                // Save ETag and timestamp
                val etag = connection.getHeaderField("ETag")
                if (etag != null) {
                    prefs.edit().putString("etag", etag).apply()
                }
                
                prefs.edit().putLong(LAST_FETCH_KEY, System.currentTimeMillis()).apply()
                
                // Parse and update database
                parseAndUpdateDatabase(cacheFile)
            }
        } catch (e: Exception) {
            // Network error, try to load from cache
            loadFromCache()
        }
    }
    
    private suspend fun loadFromCache() = withContext(Dispatchers.IO) {
        val cacheFile = File(context.cacheDir, CACHE_FILE_NAME)
        if (cacheFile.exists()) {
            parseAndUpdateDatabase(cacheFile)
        } else {
            // No cache available, check if database is empty
            if (dao.count() == 0) {
                // Fallback to assets if available
                try {
                    val inputStream = context.assets.open("products.csv")
                    val products = csvParser.parse(inputStream)
                    dao.insertAll(products)
                } catch (e: Exception) {
                    // No assets available, database remains empty
                }
            }
        }
    }
    
    private suspend fun parseAndUpdateDatabase(file: File) = withContext(Dispatchers.IO) {
        try {
            val products = csvParser.parse(file.inputStream())
            // Clear existing data and insert new data
            dao.deleteAll()
            dao.insertAll(products)
        } catch (e: Exception) {
            // Parsing error, keep existing data
        }
    }
    
    fun getLastFetchTime(): String {
        val lastFetch = prefs.getLong(LAST_FETCH_KEY, 0)
        if (lastFetch == 0L) return "Never"
        
        val dateFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
        return dateFormat.format(Date(lastFetch))
    }
}
