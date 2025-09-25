package com.foodnutrition.app

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.*
import java.net.HttpURLConnection
import java.net.URL
import java.text.SimpleDateFormat
import java.util.*
import android.content.res.AssetManager

class DataManager(private val context: Context, private val dao: ProductDao) {
    
    companion object {
        private const val TAG = "DataManager"
        private const val PREFS_NAME = "food_nutrition_prefs"
        private const val LAST_FETCH_KEY = "last_fetch"
        private const val CACHE_FILE_NAME = "products_cache.csv"
        private const val CSV_URL = "https://food-nutririon.firebaseapp.com/products.csv"
        private const val CACHE_VALIDITY_DAYS = 7
        
        private fun logd(message: String) {
            println("$TAG: $message")
            Log.d(TAG, message)
        }
        
        private fun loge(message: String, e: Exception? = null) {
            println("$TAG ERROR: $message")
            if (e != null) {
                println("${e.message}")
                Log.e(TAG, message, e)
            } else {
                Log.e(TAG, message)
            }
        }
    }
    
    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val csvParser = CsvParser()
    
    suspend fun initializeData() = withContext(Dispatchers.IO) {
        logd("Initializing data...")
        try {
            logd("Checking if data needs refresh...")
            // Always try to fetch fresh data first if we should refresh
            if (shouldRefreshData()) {
                logd("Data refresh needed, attempting to fetch from network...")
                try {
                    fetchAndUpdateData()
                } catch (e: Exception) {
                    loge("Failed to fetch data from network, trying cache", e)
                    loadFromCache()
                }
            } else {
                logd("Using cached data (still valid)")
                loadFromCache()
            }
            
            // If we still don't have data, try loading from assets
            if (dao.count() == 0) {
                logd("No data in database, trying assets...")
                try {
                    val assetManager: AssetManager = context.assets
                    val inputStream = assetManager.open("products.csv")
                    val products = csvParser.parse(inputStream)
                    dao.insertAll(products)
                    logd("Successfully loaded ${products.size} products from assets")
                } catch (e: Exception) {
                    loge("Error loading from assets", e)
                }
            } else {
                logd("Database contains ${dao.count()} products")
            }
        } catch (e: Exception) {
            loge("Error initializing data", e)
            throw e
        }
    }
    
    private fun shouldRefreshData(): Boolean {
        val lastFetch = prefs.getLong(LAST_FETCH_KEY, 0)
        if (lastFetch == 0L) return true
        
        val daysSinceLastFetch = (System.currentTimeMillis() - lastFetch) / (1000 * 60 * 60 * 24)
        return daysSinceLastFetch >= CACHE_VALIDITY_DAYS
    }
    
    private suspend fun fetchAndUpdateData() = withContext(Dispatchers.IO) {
        logd("Starting network fetch from: $CSV_URL")
        try {
            val url = URL(CSV_URL)
            val connection = url.openConnection() as HttpURLConnection
            connection.apply {
                requestMethod = "GET"
                setRequestProperty("User-Agent", "FoodNutritionApp/1.0")
                setRequestProperty("Accept", "text/csv")
                connectTimeout = 15000 // 15 seconds
                readTimeout = 30000 // 30 seconds
                useCaches = false
                logd("Connection properties set")
            }
            
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
            
            logd("Server responded with code: $responseCode")
            if (responseCode == HttpURLConnection.HTTP_OK) {
                // Get content length for logging (using contentLength for API level 21+ compatibility)
                val contentLength = connection.contentLength
                logd("Downloading content, size: $contentLength bytes")
                
                // Download and cache the file
                val inputStream = connection.inputStream
                val cacheFile = File(context.cacheDir, CACHE_FILE_NAME)
                
                try {
                    // Read the content with progress logging
                    val content = StringBuilder()
                    val reader = BufferedReader(InputStreamReader(inputStream))
                    var line: String?
                    var lineCount = 0
                    
                    while (reader.readLine().also { line = it } != null) {
                        content.append(line).append("\n")
                        lineCount++
                        if (lineCount % 100 == 0) {
                            logd("Downloaded $lineCount lines...")
                        }
                    }
                    
                    if (content.isEmpty()) {
                        throw Exception("Downloaded content is empty")
                    }
                    
                    logd("Download complete. Total lines: $lineCount, Total size: ${content.length} bytes")
                    
                    // Write to cache file
                    FileOutputStream(cacheFile).use { output ->
                        output.write(content.toString().toByteArray())
                    }
                    logd("Successfully cached data to ${cacheFile.absolutePath}")
                    
                    // Parse and update database
                    parseAndUpdateDatabase(cacheFile)
                    
                } catch (e: Exception) {
                    loge("Error processing downloaded content", e)
                    // Delete potentially corrupted cache file
                    if (cacheFile.exists()) {
                        cacheFile.delete()
                    }
                    throw e
                }
                
                // Save ETag and timestamp
                val etag = connection.getHeaderField("ETag")
                if (etag != null) {
                    logd("Saving ETag: $etag")
                    prefs.edit().putString("etag", etag).apply()
                }
                
                val timestamp = System.currentTimeMillis()
                logd("Saving last fetch timestamp: $timestamp")
                prefs.edit().putLong(LAST_FETCH_KEY, timestamp).apply()
                logd("Successfully updated data from network")
            }
        } catch (e: Exception) {
            // Network error, try to load from cache
            loadFromCache()
        }
    }
    
    private suspend fun loadFromCache() = withContext(Dispatchers.IO) {
        logd("Attempting to load from cache...")
        val cacheFile = File(context.cacheDir, CACHE_FILE_NAME)
        if (cacheFile.exists()) {
            logd("Cache file found at ${cacheFile.absolutePath}, size: ${cacheFile.length()} bytes")
            try {
                parseAndUpdateDatabase(cacheFile)
                logd("Successfully loaded data from cache")
            } catch (e: Exception) {
                loge("Error loading from cache", e)
                // Try to delete corrupted cache
                if (cacheFile.exists()) {
                    cacheFile.delete()
                    logd("Deleted corrupted cache file")
                }
                throw e
            }
        } else {
            logd("No cache file found at ${cacheFile.absolutePath}")
            // No cache available, check if database is empty
            val count = dao.count()
            if (count == 0) {
                logd("Database is empty, trying assets...")
                // Fallback to assets if available
                try {
                    val assetManager: AssetManager = context.assets
                    val inputStream = assetManager.open("products.csv")
                    val products = csvParser.parse(inputStream)
                    dao.insertAll(products)
                    logd("Successfully loaded ${products.size} products from assets")
                } catch (e: Exception) {
                    loge("Error loading from assets", e)
                    // No assets available, database remains empty
                    logd("No data available in cache or assets")
                }
            } else {
                logd("Using existing database with $count products")
            }
        }
    }
    
    private suspend fun parseAndUpdateDatabase(file: File) = withContext(Dispatchers.IO) {
        logd("Parsing data from file: ${file.name}")
        try {
            val startTime = System.currentTimeMillis()
            val products = csvParser.parse(FileInputStream(file))
            logd("Parsed ${products.size} products in ${System.currentTimeMillis() - startTime}ms")
            
            dao.deleteAll()
            logd("Deleted existing database records")
            
            val insertStart = System.currentTimeMillis()
            dao.insertAll(products)
            logd("Inserted ${products.size} products in ${System.currentTimeMillis() - insertStart}ms")
            
        } catch (e: Exception) {
            loge("Error parsing CSV file", e)
            throw e
        }
    }
    
    fun getLastFetchTime(): String {
        val lastFetch = prefs.getLong(LAST_FETCH_KEY, 0)
        if (lastFetch == 0L) return "Never"
        
        val dateFormat = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
        return dateFormat.format(Date(lastFetch))
    }
}
