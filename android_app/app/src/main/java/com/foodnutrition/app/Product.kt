package com.foodnutrition.app

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "products")
data class Product(
    @PrimaryKey val id: String,
    val productName: String?,
    val brand: String?,
    val category: String?,
    val ingredients: String?,
    val servingSize: String?,
    val nutritionPer: String?,
    val energyKcal100g: Double?,
    val fat100g: Double?,
    val saturatedFat100g: Double?,
    val carbs100g: Double?,
    val sugars100g: Double?,
    val protein100g: Double?,
    val salt100g: Double?,
    val fiber100g: Double?,
    val sodium100g: Double?
)
