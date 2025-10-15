package com.foodnutrition.app

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import kotlinx.coroutines.flow.Flow

@Dao
interface ProductDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(products: List<Product>)

    @Query("SELECT * FROM products WHERE category = :category")
    fun getProductsByCategory(category: String): Flow<List<Product>>
    
    @Query("SELECT * FROM products WHERE product_name LIKE '%' || :query || '%' OR brand LIKE '%' || :query || '%'")
    fun searchProducts(query: String): Flow<List<Product>>
    
    @Query("SELECT * FROM products WHERE source = :source")
    fun getProductsBySource(source: String): Flow<List<Product>>

    @Query("SELECT DISTINCT category FROM products")
    fun getAllCategories(): Flow<List<String>>

    @Query("SELECT COUNT(*) FROM products")
    suspend fun count(): Int

    @Query("DELETE FROM products")
    suspend fun deleteAll()
}
