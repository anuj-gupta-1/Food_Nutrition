package com.foodnutrition.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.lifecycle.lifecycleScope
import com.foodnutrition.app.ui.theme.FoodNutritionTheme
import kotlinx.coroutines.launch

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val db = AppDatabase.getDatabase(this)
        val dao = db.productDao()
        val dataManager = DataManager(this, dao)

        lifecycleScope.launch {
            // Initialize data from Firebase CSV with background refresh
            dataManager.initializeData()
        }

        setContent {
            FoodNutritionTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    FoodNutritionApp(dao = dao, dataManager = dataManager)
                }
            }
        }
    }
}

@Composable
fun FoodNutritionApp(dao: ProductDao, dataManager: DataManager) {
    AppNavigation(dao = dao, dataManager = dataManager)
}
