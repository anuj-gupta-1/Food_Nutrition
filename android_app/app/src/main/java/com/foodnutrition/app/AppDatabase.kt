package com.foodnutrition.app

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase

import androidx.room.TypeConverters 
import com.foodnutrition.app.data.Converters 

@Database(entities = [Product::class], version = 2, exportSchema = false)
@TypeConverters(Converters::class) // <-- ADD THIS ANNOTATION

abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "food_nutrition_database"
                )
                .fallbackToDestructiveMigration() // For development - clears DB on schema change
                .build()
                INSTANCE = instance
                instance
            }
        }
    }
}
