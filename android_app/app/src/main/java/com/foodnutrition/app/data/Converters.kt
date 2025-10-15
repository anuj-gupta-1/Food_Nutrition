package com.foodnutrition.app.data

import androidx.room.TypeConverter
import com.foodnutrition.app.NutritionValue
import com.google.gson.Gson
import com.google.gson.reflect.TypeToken

class Converters {
    @TypeConverter
    fun fromNutritionValueMap(value: Map<String, NutritionValue>?): String {
        return Gson().toJson(value)
    }

    @TypeConverter
    fun toNutritionValueMap(value: String): Map<String, NutritionValue>? {
        val mapType = object : TypeToken<Map<String, NutritionValue>?>() {}.type
        return Gson().fromJson(value, mapType)
    }

    @TypeConverter
    fun fromNutritionValueList(value: List<NutritionValue>?): String {
        return Gson().toJson(value)
    }

    @TypeConverter
    fun toNutritionValueList(value: String): List<NutritionValue>? {
        val listType = object : TypeToken<List<NutritionValue>?>() {}.type
        return Gson().fromJson(value, listType)
    }
}
