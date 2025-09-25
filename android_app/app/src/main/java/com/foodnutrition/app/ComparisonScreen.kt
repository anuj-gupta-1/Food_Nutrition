package com.foodnutrition.app

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
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
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults

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
        Text("Please select exactly 2 products to compare.")
        return
    }

    val product1 = products[0]
    val product2 = products[1]

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
    ) {
        // Top App Bar
        TopAppBar(
            title = {
                Text(
                    text = "Nutrition Comparison",
                    fontWeight = FontWeight.Bold
                )
            },
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
                NutritionField(
                    "Energy",
                    "kcal/100g",
                    product1.energyKcal100g?.toString() ?: "N/A",
                    product2.energyKcal100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Fat",
                    "g/100g",
                    product1.fat100g?.toString() ?: "N/A",
                    product2.fat100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Saturated Fat",
                    "g/100g",
                    product1.saturatedFat100g?.toString() ?: "N/A",
                    product2.saturatedFat100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Carbohydrates",
                    "g/100g",
                    product1.carbs100g?.toString() ?: "N/A",
                    product2.carbs100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Sugars",
                    "g/100g",
                    product1.sugars100g?.toString() ?: "N/A",
                    product2.sugars100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Protein",
                    "g/100g",
                    product1.protein100g?.toString() ?: "N/A",
                    product2.protein100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Fiber",
                    "g/100g",
                    product1.fiber100g?.toString() ?: "N/A",
                    product2.fiber100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Salt",
                    "g/100g",
                    product1.salt100g?.toString() ?: "N/A",
                    product2.salt100g?.toString() ?: "N/A"
                ),
                NutritionField(
                    "Sodium",
                    "g/100g",
                    product1.sodium100g?.toString() ?: "N/A",
                    product2.sodium100g?.toString() ?: "N/A"
                )
            )

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
                            modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Text(
                            text = field.value1,
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodyMedium
                        )
                        Text(
                            text = field.value2,
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodyMedium
                        )
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            // Additional product info
            Card(
                modifier = Modifier.fillMaxWidth(),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Product Details",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                    Spacer(modifier = Modifier.height(8.dp))

                    // Brand
                    Row(modifier = Modifier.padding(vertical = 4.dp)) {
                        Text(
                            text = "Brand",
                            modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            text = product1.brand ?: "N/A",
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            text = product2.brand ?: "N/A",
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }

                    // Serving Size
                    Row(modifier = Modifier.padding(vertical = 4.dp)) {
                        Text(
                            text = "Serving Size",
                            modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            text = product1.servingSize ?: "N/A",
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            text = product2.servingSize ?: "N/A",
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }

                    // Nutrition Per
                    Row(modifier = Modifier.padding(vertical = 4.dp)) {
                        Text(
                            text = "Nutrition Per",
                            modifier = Modifier.weight(1f),
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            text = product1.nutritionPer ?: "N/A",
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            text = product2.nutritionPer ?: "N/A",
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 4.dp),
                            textAlign = TextAlign.Center,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
        }
    }
}

