package com.foodnutrition.app.data

import android.util.Log
import com.foodnutrition.app.Product
import com.google.firebase.firestore.ktx.firestore
import com.google.firebase.ktx.Firebase
import kotlinx.coroutines.tasks.await

class FirebaseRepository {

    private val db = Firebase.firestore

    suspend fun getAllProducts(): Result<List<Product>> {
        return try {
            val snapshot = db.collection("products").get().await()
            val products = snapshot.toObjects(Product::class.java)
            Log.d("FirebaseRepository", "Fetched ${products.size} products from Firestore.")
            Result.success(products)
        } catch (e: Exception) {
            Log.e("FirebaseRepository", "Error fetching products from Firestore", e)
            Result.failure(e)
        }
    }
}
