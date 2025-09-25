package com.foodnutrition.app

import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument

@Composable
fun AppNavigation(dao: ProductDao, dataManager: DataManager) {
    val navController = rememberNavController()
    val context = LocalContext.current

    NavHost(
        navController = navController,
        startDestination = "categories"
    ) {
        composable("categories") {
            CategoryScreen(
                dao = dao,
                dataManager = dataManager,
                onCategorySelected = { category ->
                    navController.navigate("products/${category}")
                }
            )
        }
        
        composable(
            "products/{category}",
            arguments = listOf(navArgument("category") { type = NavType.StringType })
        ) { backStackEntry ->
            val category = backStackEntry.arguments?.getString("category") ?: return@composable
            
            ProductSelectionScreen(
                dao = dao,
                category = category,
                onProductsSelected = { products ->
                    if (products.isNotEmpty()) {
                        navController.currentBackStackEntry?.savedStateHandle?.set("products", products)
                        navController.navigate("comparison")
                    } else {
                        navController.popBackStack()
                    }
                }
            )
        }
        
        composable("comparison") {
            val products = navController.previousBackStackEntry?.savedStateHandle?.get<List<Product>>("products") ?: emptyList()
            ComparisonScreen(
                products = products,
                onBack = { navController.popBackStack() }
            )
        }
    }
}
