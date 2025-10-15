package com.foodnutrition.app

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.foodnutrition.app.data.FirebaseRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.*

class DataManager(private val context: Context, private val dao: ProductDao) {

    companion object {
        private const val TAG = "DataManager"
        private const val PREFS_NAME = "food_nutrition_prefs"
        private const val LAST_FETCH_KEY = "last_fetch"
        private const val CACHE_VALIDITY_DAYS = 1 // Refresh data daily
    }

    private val prefs: SharedPreferences = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
    private val firebaseRepository = FirebaseRepository()

    suspend fun initializeData() = withContext(Dispatchers.IO) {
        Log.d(TAG, "Initializing data...")
        if (shouldRefreshData() || dao.count() == 0) {
            Log.d(TAG, "Refresh needed or DB empty. Fetching from Firestore...")
            fetchFromFirestore()
        } else {
            Log.d(TAG, "Using cached data from Room. ${dao.count()} products available.")
        }
    }

    private suspend fun fetchFromFirestore() {
        val result = firebaseRepository.getAllProducts()
        result.onSuccess { products ->
            if (products.isNotEmpty()) {
                Log.d(TAG, "Successfully fetched ${products.size} products from Firestore.")
                dao.deleteAll()
                dao.insertAll(products)
                prefs.edit().putLong(LAST_FETCH_KEY, System.currentTimeMillis()).apply()
                Log.d(TAG, "Updated Room database and last fetch timestamp.")
            } else {
                Log.d(TAG, "No products from Firestore. Falling back to CSV assets.")
                loadFromAssets()
            }
        }.onFailure { exception ->
            Log.e(TAG, "Error fetching from Firestore. Falling back to CSV assets.", exception)
            loadFromAssets()
        }
    }
    
    private suspend fun loadFromAssets() {
        try {
            Log.d(TAG, "Loading products from CSV assets...")
            val csvParser = CsvParser()
            val products = csvParser.parseProductsFromAssets(context)
            
            if (products.isNotEmpty()) {
                Log.d(TAG, "Successfully loaded ${products.size} products from CSV assets.")
                dao.deleteAll()
                dao.insertAll(products)
                prefs.edit().putLong(LAST_FETCH_KEY, System.currentTimeMillis()).apply()
                Log.d(TAG, "Updated Room database with CSV data.")
            } else {
                Log.w(TAG, "No products loaded from CSV assets.")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error loading from CSV assets", e)
        }
    }

    private fun shouldRefreshData(): Boolean {
        val lastFetch = prefs.getLong(LAST_FETCH_KEY, 0)
        if (lastFetch == 0L) return true

        val daysSinceLastFetch = (System.currentTimeMillis() - lastFetch) / (1000 * 60 * 60 * 24)
        return daysSinceLastFetch >= CACHE_VALIDITY_DAYS
    }

    fun getLastFetchTime(): String {
        val lastFetch = prefs.getLong(LAST_FETCH_KEY, 0)
        if (lastFetch == 0L) return "Never"

        val dateFormat = SimpleDateFormat("MMM dd, yyyy HH:mm", Locale.getDefault())
        return dateFormat.format(Date(lastFetch))
    }
}
