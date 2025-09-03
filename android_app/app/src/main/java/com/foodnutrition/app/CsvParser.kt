package com.foodnutrition.app

import java.io.InputStream
import java.io.InputStreamReader

class CsvParser {
    fun parse(inputStream: InputStream): List<Product> {
        val reader = InputStreamReader(inputStream).buffered()
        val header = reader.readLine().split(',')
        return reader.lineSequence()
            .map {
                val map = it.split(',').mapIndexed { index, s -> header[index] to s }.toMap()
                Product(
                    id = map["id"] ?: "",
                    productName = map["product_name"],
                    brand = map["brand"],
                    category = map["category"],
                    ingredients = map["ingredients"],
                    servingSize = map["serving_size"],
                    nutritionPer = map["nutrition_per"],
                    energyKcal100g = map["energy_kcal_100g"]?.toDoubleOrNull(),
                    fat100g = map["fat_100g"]?.toDoubleOrNull(),
                    saturatedFat100g = map["saturated_fat_100g"]?.toDoubleOrNull(),
                    carbs100g = map["carbs_100g"]?.toDoubleOrNull(),
                    sugars100g = map["sugars_100g"]?.toDoubleOrNull(),
                    protein100g = map["protein_100g"]?.toDoubleOrNull(),
                    salt100g = map["salt_100g"]?.toDoubleOrNull(),
                    fiber100g = map["fiber_100g"]?.toDoubleOrNull(),
                    sodium100g = map["sodium_100g"]?.toDoubleOrNull()
                )
            }.toList()
    }
}
