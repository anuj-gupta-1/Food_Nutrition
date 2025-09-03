package com.foodnutrition.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

data class NutritionField(
    val nutrient: String,
    val unit: String,
    val value1: String,
    val value2: String
)

@Composable
fun ComparisonScreen(products: List<Product>) {
    if (products.size != 2) {
        Text("Please select exactly 2 products to compare.")
        return
    }

    val product1 = products[0]
    val product2 = products[1]

    Column(modifier = Modifier.padding(16.dp)) {
        // Header
        Text(
            text = "Nutrition Comparison",
            style = MaterialTheme.typography.headlineMedium,
            fontWeight = FontWeight.Bold,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        // Product names header
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.primaryContainer)
                .padding(12.dp)
        ) {
            Text(
                text = "Nutrient",
                modifier = Modifier.weight(1f),
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Start
            )
            Text(
                text = product1.productName ?: "Product A",
                modifier = Modifier.weight(1f),
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
            Text(
                text = product2.productName ?: "Product B",
                modifier = Modifier.weight(1f),
                fontWeight = FontWeight.Bold,
                textAlign = TextAlign.Center
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        // Health-focused nutrition comparison
        val nutritionFields = listOf(
            NutritionField("Energy", "kcal/100g", product1.energyKcal100g?.toString() ?: "N/A", product2.energyKcal100g?.toString() ?: "N/A"),
            NutritionField("Fat", "g/100g", product1.fat100g?.toString() ?: "N/A", product2.fat100g?.toString() ?: "N/A"),
            NutritionField("Saturated Fat", "g/100g", product1.saturatedFat100g?.toString() ?: "N/A", product2.saturatedFat100g?.toString() ?: "N/A"),
            NutritionField("Carbohydrates", "g/100g", product1.carbs100g?.toString() ?: "N/A", product2.carbs100g?.toString() ?: "N/A"),
            NutritionField("Sugars", "g/100g", product1.sugars100g?.toString() ?: "N/A", product2.sugars100g?.toString() ?: "N/A"),
            NutritionField("Protein", "g/100g", product1.protein100g?.toString() ?: "N/A", product2.protein100g?.toString() ?: "N/A"),
            NutritionField("Fiber", "g/100g", product1.fiber100g?.toString() ?: "N/A", product2.fiber100g?.toString() ?: "N/A"),
            NutritionField("Salt", "g/100g", product1.salt100g?.toString() ?: "N/A", product2.salt100g?.toString() ?: "N/A"),
            NutritionField("Sodium", "g/100g", product1.sodium100g?.toString() ?: "N/A", product2.sodium100g?.toString() ?: "N/A")
        )

        LazyColumn {
            items(nutritionFields) { field ->
                NutritionComparisonRow(
                    nutrient = field.nutrient,
                    unit = field.unit,
                    value1 = field.value1,
                    value2 = field.value2
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Additional product info
        Card(
            modifier = Modifier.fillMaxWidth(),
            elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Product Details",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Spacer(modifier = Modifier.height(8.dp))
                
                CompareRow("Brand", product1.brand, product2.brand)
                CompareRow("Serving Size", product1.servingSize, product2.servingSize)
                CompareRow("Nutrition Per", product1.nutritionPer, product2.nutritionPer)
            }
        }
    }
}

@Composable
fun NutritionComparisonRow(nutrient: String, unit: String, value1: String, value2: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "$nutrient ($unit)",
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodyMedium
        )
        Text(
            text = value1,
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.bodyMedium
        )
        Text(
            text = value2,
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

@Composable
fun CompareRow(label: String, value1: String?, value2: String?) {
    Row(modifier = Modifier.padding(vertical = 4.dp)) {
        Text(
            text = label,
            modifier = Modifier.weight(1f),
            style = MaterialTheme.typography.bodySmall
        )
        Text(
            text = value1 ?: "N/A",
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.bodySmall
        )
        Text(
            text = value2 ?: "N/A",
            modifier = Modifier.weight(1f),
            textAlign = TextAlign.Center,
            style = MaterialTheme.typography.bodySmall
        )
    }
}
