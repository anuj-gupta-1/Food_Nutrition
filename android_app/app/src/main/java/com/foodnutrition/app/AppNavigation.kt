package com.foodnutrition.app

import androidx.compose.runtime.Composable
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController

@Composable
fun AppNavigation(dao: ProductDao, dataManager: DataManager) {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = "categories") {
        composable("categories") {
            CategoryScreen(dao = dao, dataManager = dataManager, onCategorySelected = {
                navController.navigate("products/$it")
            })
        }
        composable("products/{category}") { backStackEntry ->
            val category = backStackEntry.arguments?.getString("category") ?: ""
            ProductSelectionScreen(dao = dao, category = category, onProductsSelected = {
                navController.currentBackStackEntry?.savedStateHandle?.set("products", it)
                navController.navigate("comparison")
            })
        }
        composable("comparison") { 
            val products = navController.previousBackStackEntry?.savedStateHandle?.get<List<Product>>("products") ?: emptyList()
            ComparisonScreen(products = products)
        }
    }
}
