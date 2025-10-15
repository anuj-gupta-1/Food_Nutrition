package com.foodnutrition.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

data class NutritionField(
    val nutrient: String,
    val unit: String,
    val value1: String,
    val value2: String
)

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ComparisonScreen(products: List<Product>, onBack: () -> Unit) {
    if (products.size != 2) {
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            Text("Please select exactly 2 products to compare.")
        }
        return
    }

    val product1 = products[0]
    val product2 = products[1]

    // Define the order of core nutrients to display
    val coreNutrients = remember {
        listOf("energy", "protein", "totalFat", "saturatedFat", "carbohydrates", "sugar", "fiber", "sodium")
    }

    // Helper to safely get a nutrient value
    fun getNutrientValue(product: Product, key: String): String {
        // For now, return N/A since we removed the values map
        // This can be enhanced later with proper nutrition data storage
        return "N/A"
    }

    // Dynamically build the list of fields to display
    val nutritionFields = remember(product1, product2) {
        // For now, use empty list since we removed the values map
        // This can be enhanced later with proper nutrition data storage
        val allKeys = emptyList<String>()
        val core = coreNutrients.map { key ->
            val unit = ""
            NutritionField(
                nutrient = key.replaceFirstChar { it.uppercase() },
                unit = unit,
                value1 = getNutrientValue(product1, key),
                value2 = getNutrientValue(product2, key)
            )
        }
        val additional = (allKeys - coreNutrients.toSet()).sorted().map { key ->
            val unit = "" // Simplified for now since we removed values map
            NutritionField(
                nutrient = key.replaceFirstChar { it.uppercase() },
                unit = unit,
                value1 = getNutrientValue(product1, key),
                value2 = getNutrientValue(product2, key)
            )
        }
        core + additional
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        TopAppBar(
            title = { Text("Nutrition Comparison", fontWeight = FontWeight.Bold) },
            navigationIcon = {
                IconButton(onClick = onBack) {
                    Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                }
            },
            colors = TopAppBarDefaults.topAppBarColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        )

        Column(modifier = Modifier.padding(16.dp)) {
            // Product names header
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .background(MaterialTheme.colorScheme.primaryContainer.copy(alpha = 0.1f))
                    .padding(12.dp)
            ) {
                Text("Nutrient", modifier = Modifier.weight(1.5f), fontWeight = FontWeight.Bold)
                Text(product1.product_name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
                Text(product2.product_name, modifier = Modifier.weight(1f), fontWeight = FontWeight.Bold, textAlign = TextAlign.Center)
            }

            Spacer(modifier = Modifier.height(8.dp))

            // Nutrition table
            LazyColumn {
                items(nutritionFields) { field ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "${field.nutrient} (${field.unit})",
                            modifier = Modifier.weight(1.5f),
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Text(
                            text = field.value1,
                            modifier = Modifier.weight(1f).padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Text(
                            text = field.value2,
                            modifier = Modifier.weight(1f).padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }
        }
    }
}
