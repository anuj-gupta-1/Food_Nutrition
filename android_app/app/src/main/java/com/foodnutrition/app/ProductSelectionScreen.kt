package com.foodnutrition.app

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.runtime.collectAsState

@Composable
fun ProductSelectionCard(
    product: Product,
    isSelected: Boolean,
    onToggleSelection: () -> Unit
) {
    // Helper to safely get a nutrient value as a string
    fun getNutrientString(key: String, unit: String): String? {
        // For now, return null since we removed the values map
        // This can be enhanced later with proper nutrition data storage
        return null
    }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onToggleSelection() },
        elevation = CardDefaults.cardElevation(
            defaultElevation = if (isSelected) 4.dp else 2.dp
        ),
        colors = CardDefaults.cardColors(
            containerColor = if (isSelected) 
                MaterialTheme.colorScheme.primaryContainer 
            else 
                MaterialTheme.colorScheme.surface
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Checkbox(
                checked = isSelected,
                onCheckedChange = { onToggleSelection() }
            )
            
            Spacer(modifier = Modifier.padding(horizontal = 8.dp))
            
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = product.product_name,
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
                
                if (!product.brand.isBlank()) {
                    Text(
                        text = product.brand,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Show key nutrition info
                Row {
                    val energyString = getNutrientString("energy", " kcal")
                    val fatString = getNutrientString("totalFat", "g fat")

                    if (energyString != null) {
                        Text(
                            text = energyString,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    
                    if (energyString != null && fatString != null) {
                        Text(
                            text = " • ",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    
                    if (fatString != null) {
                        Text(
                            text = fatString,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProductSelectionScreen(
    dao: ProductDao,
    category: String,
    onProductsSelected: (List<Product>) -> Unit
) {
    val products by dao.getProductsByCategory(category).collectAsState(initial = emptyList())
    var selectedProducts by remember { mutableStateOf(setOf<String>()) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Select Products - $category") },
                navigationIcon = {
                    IconButton(onClick = { /* Handle back navigation */ }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            if (selectedProducts.size >= 2) {
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.primaryContainer
                    )
                ) {
                    Column(
                        modifier = Modifier.padding(16.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(
                            text = "Selected ${selectedProducts.size} products",
                            style = MaterialTheme.typography.titleMedium
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Button(
                            onClick = {
                                val selected = products.filter { it.id in selectedProducts }
                                onProductsSelected(selected)
                            }
                        ) {
                            Text("Compare Products")
                        }
                    }
                }
            }

            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                items(products) { product ->
                    ProductSelectionCard(
                        product = product,
                        isSelected = product.id in selectedProducts,
                        onToggleSelection = {
                            selectedProducts = if (product.id in selectedProducts) {
                                selectedProducts - product.id
                            } else {
                                if (selectedProducts.size < 2) {
                                    selectedProducts + product.id
                                } else {
                                    // Replace the first selected product
                                    val newSelection = selectedProducts.toMutableSet()
                                    newSelection.remove(newSelection.first())
                                    newSelection + product.id
                                }
                            }
                        }
                    )
                }
            }
        }
    }
}
