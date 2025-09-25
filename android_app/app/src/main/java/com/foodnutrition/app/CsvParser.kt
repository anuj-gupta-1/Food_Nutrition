package com.foodnutrition.app

import java.io.InputStream
import java.io.InputStreamReader

class CsvParser {
    fun parse(inputStream: InputStream): List<Product> {
        val reader = InputStreamReader(inputStream).buffered()
        val lines = reader.readLines()
        
        if (lines.isEmpty()) {
            println("CSV file is empty")
            return emptyList()
        }
        
        val header = parseCsvLine(lines[0])
        
        return lines.drop(1) // Skip header
            .mapNotNull { line ->
                try {
                    val values = parseCsvLine(line)
                    if (values.size != header.size) {
                        println("Warning: Skipping malformed line - column count mismatch")
                        return@mapNotNull null
                    }
                    
                    val map = header.zip(values).toMap()
                    
                    try {
                        Product(
                            id = map["id"] ?: "",
                            productName = map["product_name"] ?: "",
                            brand = map["brand"] ?: "",
                            category = map["category"] ?: "",
                            ingredients = map["ingredients"] ?: "",
                            servingSize = map["serving_size"] ?: "",
                            nutritionPer = map["nutrition_per"] ?: "",
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
                    } catch (e: Exception) {
                        println("Error creating Product from line: $line\nError: ${e.message}")
                        null
                    }
                } catch (e: Exception) {
                    println("Error parsing CSV line: $line\nError: ${e.message}")
                    null
                }
            }
    }
    
    private fun parseCsvLine(line: String): List<String> {
        val result = mutableListOf<String>()
        val current = StringBuilder()
        var inQuotes = false
        var i = 0
        
        while (i < line.length) {
            when (line[i]) {
                '"' -> {
                    // Check if this is an escaped quote ("")
                    if (i < line.length - 1 && line[i + 1] == '"') {
                        current.append('"')
                        i += 2 // Skip next quote
                        continue
                    } else {
                        inQuotes = !inQuotes
                    }
                }
                ',' -> {
                    if (inQuotes) {
                        current.append(',')
                    } else {
                        result.add(current.toString())
                        current.clear()
                    }
                }
                else -> current.append(line[i])
            }
            i++
        }
        
        // Add the last field
        result.add(current.toString())
        
        return result
    }
}
