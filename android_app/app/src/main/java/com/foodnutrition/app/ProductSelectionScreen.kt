package com.foodnutrition.app

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Checkbox
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.ExperimentalComposeUiApi
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class, ExperimentalComposeUiApi::class)
@Composable
fun ProductSelectionScreen(
    dao: ProductDao, 
    category: String, 
    onProductsSelected: (List<Product>) -> Unit
) {
    val keyboardController = LocalSoftwareKeyboardController.current
    val products by dao.getProductsByCategory(category)
        .collectAsState(initial = emptyList())
    
    var selectedProducts by remember { mutableStateOf<List<Product>>(emptyList()) }
    var searchQuery by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        println("Loaded ${products.size} products for category: $category")
        if (products.isNotEmpty()) {
            println("First product: ${products[0].productName} (${products[0].brand})")
        }
    }

    val filteredProducts = remember(products, searchQuery) {
        if (products.isEmpty()) return@remember emptyList<Product>()
        if (searchQuery.isBlank()) return@remember products

        val query = searchQuery.trim().lowercase()
        products
            .filter { product ->
                listOf(
                    product.productName?.lowercase(),
                    product.brand?.lowercase(),
                    product.id.lowercase()
                ).any { it?.contains(query) == true }
            }
            .sortedBy { product ->
                val nameMatch = product.productName?.lowercase() ?: ""
                val brandMatch = product.brand?.lowercase() ?: ""
                
                when {
                    nameMatch == query -> 0
                    brandMatch == query -> 1
                    nameMatch.isNotEmpty() && nameMatch.startsWith(query) -> 2
                    brandMatch.isNotEmpty() && brandMatch.startsWith(query) -> 3
                    nameMatch.isNotEmpty() && nameMatch.contains(query) -> 4
                    brandMatch.isNotEmpty() && brandMatch.contains(query) -> 5
                    else -> 6
                }
            }
    }

    Column(modifier = Modifier.fillMaxSize()) {
        TopAppBar(
            title = { 
                Text(
                    text = "Select Products",
                    fontWeight = FontWeight.Bold
                )
            },
            navigationIcon = {
                IconButton(onClick = { onProductsSelected(emptyList()) }) {
                    Icon(
                        imageVector = Icons.Default.ArrowBack,
                        contentDescription = "Back"
                    )
                }
            },
            colors = TopAppBarDefaults.smallTopAppBarColors(
                containerColor = MaterialTheme.colorScheme.primaryContainer
            )
        )

        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp)
        ) {
            Text(
                text = "Category: $category",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Medium,
                modifier = Modifier.padding(bottom = 8.dp)
            )

            OutlinedTextField(
                value = searchQuery,
                onValueChange = { searchQuery = it },
                label = { Text("Search products or brands") },
                leadingIcon = { 
                    Icon(
                        imageVector = Icons.Default.Search,
                        contentDescription = "Search"
                    ) 
                },
                modifier = Modifier.fillMaxWidth(),
                keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
                keyboardActions = KeyboardActions(
                    onSearch = { keyboardController?.hide() }
                )
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "Selected: ${selectedProducts.size}/2 products",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(16.dp))

            when {
                products.isEmpty() -> {
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .fillMaxWidth()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "No products found. Please check your internet connection and try again.",
                            textAlign = TextAlign.Center,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                filteredProducts.isEmpty() && searchQuery.isNotBlank() -> {
                    Box(
                        modifier = Modifier
                            .weight(1f)
                            .fillMaxWidth()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(
                            text = "No products match your search. Try different keywords.",
                            textAlign = TextAlign.Center,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
                else -> {
                    LazyColumn(
                        modifier = Modifier.weight(1f),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        items(filteredProducts) { product ->
                            ProductSelectionCard(
                                product = product,
                                isSelected = selectedProducts.contains(product),
                                onToggleSelection = {
                                    selectedProducts = if (selectedProducts.contains(product)) {
                                        selectedProducts - product
                                    } else if (selectedProducts.size < 2) {
                                        selectedProducts + product
                                    } else {
                                        selectedProducts
                                    }
                                }
                            )
                        }
                    }
                }
            }

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = { onProductsSelected(selectedProducts) },
                enabled = selectedProducts.size == 2,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text(
                    text = if (selectedProducts.size == 2) {
                        "Compare Products"
                    } else {
                        "Select 2 products to compare"
                    }
                )
            }
        }
    }
}

@Composable
fun ProductSelectionCard(
    product: Product,
    isSelected: Boolean,
    onToggleSelection: () -> Unit
) {
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
                    text = product.productName ?: "Unknown Product",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Medium
                )
                
                if (!product.brand.isNullOrBlank()) {
                    Text(
                        text = product.brand,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                // Show key nutrition info
                Row {
                    product.energyKcal100g?.let { energy ->
                        Text(
                            text = "${energy.toInt()} kcal/100g",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    
                    if (product.energyKcal100g != null && product.fat100g != null) {
                        Text(
                            text = " • ",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    
                    product.fat100g?.let { fat ->
                        Text(
                            text = "${fat.toInt()}g fat/100g",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                }
            }
        }
    }
}
