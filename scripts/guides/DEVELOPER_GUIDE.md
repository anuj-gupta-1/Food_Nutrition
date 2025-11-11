# Developer Guide - Food Nutrition Comparison App

**Version**: 1.0  
**Last Updated**: 2025-10-15  
**Target Audience**: Developers, Technical Contributors

---

## 🎯 Overview

This guide provides technical details for developers working on the Food Nutrition Comparison app. It covers architecture, code structure, data flow, and development workflows.

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Sources  │    │   Data Pipeline  │    │  Android App    │
│                 │    │                  │    │                 │
│ • StarQuik      │───▶│ • consolidate_   │───▶│ • Room DB       │
│ • JioMart       │    │   data.py        │    │ • Firebase      │
│ • OpenFoodFacts │    │ • Validation     │    │ • Jetpack       │
│ • Frugivore     │    │ • Quality Score  │    │   Compose       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   Firebase       │
                       │   Firestore      │
                       └──────────────────┘
```

### Data Flow

1. **Data Collection**: Source scrapers collect product data
2. **Processing**: `consolidate_data.py` standardizes and validates data
3. **Storage**: Data stored in CSV and Firebase Firestore
4. **Distribution**: Android app loads data with offline fallback

## 📱 Android App Architecture

### Project Structure

```
android_app/app/src/main/java/com/foodnutrition/app/
├── Product.kt                    # Room entity
├── ProductDao.kt                 # Data access object
├── AppDatabase.kt                # Database configuration
├── CsvParser.kt                  # CSV parsing utility
├── DataManager.kt                # Data management layer
├── MainActivity.kt               # App entry point
├── AppNavigation.kt              # Navigation setup
├── CategoryScreen.kt             # Category listing
├── ProductSelectionScreen.kt     # Product selection UI
├── ComparisonScreen.kt           # Comparison UI
└── data/
    ├── FirebaseRepository.kt     # Firebase integration
    └── Converters.kt             # Type converters
```

### Key Components

#### 1. Product Entity (`Product.kt`)

```kotlin
@Entity(tableName = "products")
data class Product(
    @PrimaryKey val id: String,
    val product_name: String,
    val brand: String,
    val category: String,
    val subcategory: String? = null,
    val size_value: Double? = null,
    val size_unit: String? = null,
    val price: Double? = null,
    val source: String,
    val source_url: String? = null,
    val ingredients: String? = null,
    @Embedded val nutrition_data: NutritionData,
    val image_url: String? = null,
    val last_updated: String? = null,
    val search_count: Int = 0,
    val llm_fallback_used: Boolean = false,
    val data_quality_score: Int = 0,
    @Embedded val metadata: ProductMetadata
)
```

#### 2. Data Access Object (`ProductDao.kt`)

```kotlin
@Dao
interface ProductDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(products: List<Product>)

    @Query("SELECT * FROM products WHERE category = :category")
    fun getProductsByCategory(category: String): Flow<List<Product>>
    
    @Query("SELECT * FROM products WHERE product_name LIKE '%' || :query || '%' OR brand LIKE '%' || :query || '%'")
    fun searchProducts(query: String): Flow<List<Product>>
    
    @Query("SELECT DISTINCT category FROM products")
    fun getAllCategories(): Flow<List<String>>
    
    @Query("SELECT COUNT(*) FROM products")
    suspend fun count(): Int
}
```

#### 3. Data Manager (`DataManager.kt`)

The DataManager handles data loading with the following priority:
1. **Primary**: Load from CSV assets
2. **Fallback**: Fetch from Firebase Firestore
3. **Caching**: Store in local Room database
4. **Refresh**: Daily cache refresh

### UI Architecture

#### Jetpack Compose Structure

```kotlin
@Composable
fun FoodNutritionApp(dao: ProductDao, dataManager: DataManager) {
    AppNavigation(dao = dao, dataManager = dataManager)
}

@Composable
fun AppNavigation(dao: ProductDao, dataManager: DataManager) {
    val navController = rememberNavController()
    
    NavHost(navController = navController, startDestination = "categories") {
        composable("categories") {
            CategoryScreen(dao = dao, onCategorySelected = { ... })
        }
        composable("products/{category}") { backStackEntry ->
            ProductSelectionScreen(dao = dao, category = category, ...)
        }
        composable("comparison") {
            ComparisonScreen(products = selectedProducts, ...)
        }
    }
}
```

## 🔄 Data Pipeline

### Data Processing Flow

#### 1. Source Data Collection

```python
# Example: StarQuik scraper
def scrape_starquik_products():
    # Selenium automation to extract product data
    # Returns CSV with product information
    pass
```

#### 2. Data Consolidation (`consolidate_data.py`)

```python
def process_source_file(source_name, file_path):
    # Read source data with appropriate separator
    if source_name == 'jiomart':
        # Handle || separated data
        df = parse_jiomart_data(file_path)
    else:
        # Handle comma separated data
        df = pd.read_csv(file_path, sep=',')
    
    # Standardize and validate data
    processed_df = standardize_data(df)
    return processed_df

def main():
    # Process all source files
    all_processed_dfs = []
    for source_name, file_path in SOURCE_FILES.items():
        processed_df = process_source_file(source_name, file_path)
        if not processed_df.empty:
            all_processed_dfs.append(processed_df)
    
    # Combine and deduplicate
    master_df = pd.concat(all_processed_dfs, ignore_index=True)
    master_df = deduplicate_products(master_df)
    
    # Save to main database
    save_to_csv(master_df)
```

#### 3. Data Quality Scoring

```python
def calculate_data_quality_score(row):
    score = 0
    
    # Basic fields (60 points)
    if pd.notna(row.get('product_name')) and row.get('product_name').strip():
        score += 20
    if pd.notna(row.get('brand')) and row.get('brand') != "Unknown Brand":
        score += 15
    if pd.notna(row.get('category')):
        score += 10
    if pd.notna(row.get('size_value')) and pd.notna(row.get('size_unit')):
        score += 15
    
    # Enhanced fields (40 points)
    if pd.notna(row.get('price')):
        score += 15
    if pd.notna(row.get('ingredients')) and row.get('ingredients').strip():
        score += 10
    if pd.notna(row.get('nutrition_data')) and row.get('nutrition_data').strip():
        score += 15
    
    return min(score, 100)
```

## 🔥 Firebase Integration

### Firestore Structure

```javascript
// Collection: products
// Document ID: {source}_{product_id}
{
  "id": "starquik_gowardhan_curd_cup_400_gm",
  "product_name": "Gowardhan Curd Cup 400 Gm",
  "brand": "Gowardhan",
  "category": "diary",
  "subcategory": "general",
  "size_value": 400.0,
  "size_unit": "Gm",
  "price": 71.25,
  "source": "starquik",
  "source_url": "https://www.starquik.com/...",
  "ingredients": "Milk, Cultures...",
  "nutrition_data": {
    "available": true,
    "standardUnit": "per100g",
    "nutritionSource": "csv_upload",
    "lastChecked": 1697352133664
  },
  "image_url": null,
  "last_updated": "2025-10-15T05:22:13.664827+00:00",
  "search_count": 0,
  "llm_fallback_used": false,
  "data_quality_score": 90,
  "metadata": {
    "version": 2,
    "createdAt": 1697352133664,
    "updatedAt": 1697352133664,
    "firebase_uploaded": true
  }
}
```

### Firebase Repository

```kotlin
class FirebaseRepository {
    private val db = Firebase.firestore

    suspend fun getAllProducts(): Result<List<Product>> {
        return try {
            val snapshot = db.collection("products").get().await()
            val products = snapshot.toObjects(Product::class.java)
            Result.success(products)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

## 🛠️ Development Workflow

### Setting Up Development Environment

1. **Clone Repository**
   ```bash
   git clone <repository-url>
   cd Food_Nutrition
   ```

2. **Android Development Setup**
   ```bash
   # Open Android Studio
   # File > Open > Select android_app folder
   # Wait for Gradle sync
   ```

3. **Python Environment Setup**
   ```bash
   cd scripts
   pip install pandas firebase-admin
   ```

### Building and Testing

#### Android App

```bash
# Debug build
cd android_app
./gradlew assembleDebug

# Release build
./gradlew assembleRelease

# Run tests
./gradlew test

# Lint check
./gradlew lint
```

#### Data Pipeline

```bash
# Process data
cd scripts
python consolidate_data.py

# Test Firebase upload
python test_firebase_upload.py

# Full upload to Firebase
python upload_to_firestore.py
```

### Code Quality Standards

#### Kotlin Style Guide
- Follow Android Kotlin Style Guide
- Use meaningful variable names
- Add documentation for public APIs
- Handle null safety properly

#### Python Style Guide
- Follow PEP 8
- Use type hints
- Add docstrings for functions
- Handle exceptions gracefully

## 🧪 Testing Strategy

### Current Testing Status

✅ **Implemented:**
- Build verification
- Data pipeline testing
- Firebase integration testing

📋 **Planned:**
- Unit tests for data processing
- UI tests for Android app
- Integration tests for Firebase
- Performance testing

### Test Structure

```
android_app/app/src/test/java/
├── ProductTest.kt                 # Entity tests
├── ProductDaoTest.kt              # Database tests
└── DataManagerTest.kt             # Data management tests

scripts/tests/
├── test_consolidate_data.py       # Data processing tests
└── test_firebase_integration.py   # Firebase tests
```

## 🚀 Deployment

### Android App Deployment

1. **Build Release APK**
   ```bash
   cd android_app
   ./gradlew assembleRelease
   ```

2. **Sign APK** (if needed)
   ```bash
   # Configure signing in build.gradle
   ./gradlew assembleRelease
   ```

3. **Distribute**
   - Upload to Google Play Store
   - Or distribute APK directly

### Data Updates

1. **Process New Data**
   ```bash
   cd scripts
   python consolidate_data.py
   ```

2. **Update Firebase**
   ```bash
   python upload_to_firestore.py
   ```

3. **Update Android App**
   ```bash
   copy ../data/products.csv ../android_app/app/src/main/assets/products.csv
   cd ../android_app
   ./gradlew assembleDebug
   ```

## 🔍 Debugging

### Common Issues

#### 1. Data Parsing Errors
```python
# Check for malformed rows
def debug_csv_parsing(file_path):
    with open(file_path, 'r') as f:
        for i, line in enumerate(f):
            if len(line.split('||')) != expected_columns:
                print(f"Malformed row {i}: {line}")
```

#### 2. Firebase Connection Issues
```kotlin
// Check Firebase configuration
class FirebaseRepository {
    init {
        try {
            FirebaseApp.initializeApp(context)
        } catch (e: Exception) {
            Log.e("Firebase", "Initialization failed", e)
        }
    }
}
```

#### 3. Room Database Issues
```kotlin
// Enable Room debugging
@Database(
    entities = [Product::class],
    version = 2,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    // Add debugging queries
    fun debugQuery(): String {
        return "SELECT COUNT(*) FROM products"
    }
}
```

## 📊 Performance Monitoring

### Key Metrics

- **App Startup Time**: < 2 seconds
- **Database Query Time**: < 100ms
- **Firebase Sync Time**: < 5 seconds
- **Memory Usage**: < 50MB
- **APK Size**: ~15MB

### Monitoring Tools

- **Firebase Analytics**: User behavior tracking
- **Firebase Crashlytics**: Error monitoring
- **Android Studio Profiler**: Performance analysis

## 🏷️ Category Management System

### Overview

The category management system provides centralized configuration for product categories and subcategories with automated migration capabilities.

### Architecture

```
data_cleanup/
├── config/
│   └── category_mapping.yaml     # Category definitions
├── core/
│   ├── category_manager.py       # Configuration management
│   └── migration_engine.py       # Database migration
└── migrations/
    ├── migrate_categories.py     # Migration script
    └── validate_migration.py     # Validation script
```

### Category Structure (v2.0)

#### Current Categories (13 total, 57 subcategories)

```yaml
essentials: [flour, salt, sugar, dry-fruits-nuts, oil, rice, pulses, masala, wheat-soya]
snacks: [breakfast, chips, namkeen, biscuit]
flavourings: [pickles, chutney, sauce]
beverage: [tea, coffee, juice, carbonated, energy-drinks, health-drinks, syrup, other-beverages]
spread: [sauce-ketchup, butter, jam-honey, other-spreads]
noodles_pasta: [noodles, pasta, instant-noodles]
mithai: [chocolate, candy, sweets, mithai, desserts]  # Renamed from 'chocolate'
ready_to_eat: [ready-to-eat, instant-meals]
baby: [baby-food, baby-snacks]
dairy: [milk, curd, cheese, paneer, yogurt, ghee]  # Butter moved to spread
bakery: [cake, bread, pastry, cookies, baking-accessories]
frozen: [ice-cream, kulfi, frozen-foods]  # New category
health: [supplements, protein-powder, vitamins]  # New category
```

### Migration System

#### Running Migrations

```bash
# 1. Analyze migration impact (dry run)
python scripts/data_cleanup/migrations/migrate_categories.py --dry-run

# 2. Apply migration changes
python scripts/data_cleanup/migrations/migrate_categories.py --apply

# 3. Validate results
python scripts/data_cleanup/migrations/validate_migration.py
```

#### Migration Features

- **Automatic Backups**: Created before any changes
- **Dry Run Mode**: Test without modifying data
- **Category Changes**: Direct category/subcategory updates
- **Subcategory Splits**: Split combined subcategories using keyword rules
- **Validation**: Pre and post-migration checks
- **Rollback**: Restore from backup if needed

#### Example Migration Rules

```yaml
migration_rules:
  category_changes:
    - from: "chocolate.chocolate"
      to: "mithai.chocolate"
    - from: "spread.sauce-ketchup-butter"
      to: "spread.sauce-ketchup"

  subcategory_splits:
    - category: "essentials"
      old_subcategory: "salt-sugar"
      new_subcategories: [salt, sugar]
      classification_rules:
        - keywords: ["salt", "namak", "sea salt"]
          target: "salt"
        - keywords: ["sugar", "cheeni", "jaggery"]
          target: "sugar"
```

### Using Category Manager

```python
from scripts.data_cleanup.core.category_manager import CategoryManager

# Initialize manager
manager = CategoryManager()

# Get categories and subcategories
categories = manager.get_all_categories()
subcategories = manager.get_subcategories('essentials')

# Validate category/subcategory
is_valid = manager.is_valid_subcategory('essentials', 'salt')

# Get migration mappings
old_cat, old_subcat = 'chocolate', 'chocolate'
new_cat, new_subcat = manager.find_new_category_mapping(old_cat, old_subcat)
# Returns: ('mithai', 'chocolate')
```

### LLM Integration with Categories

When using LLM for classification, the system automatically loads the latest category configuration:

```python
from scripts.data_cleanup.core.category_manager import CategoryManager

class LLMProductClassifier:
    def __init__(self):
        self.category_manager = CategoryManager()
    
    def get_valid_subcategories(self, category: str) -> List[str]:
        return self.category_manager.get_subcategories(category)
    
    def classify_product(self, product_name: str, category: str) -> str:
        valid_subcategories = self.get_valid_subcategories(category)
        # Pass valid_subcategories to LLM for classification
        return llm_classify(product_name, valid_subcategories)
```

### Updating Categories

#### 1. Edit Configuration

```yaml
# scripts/data_cleanup/config/category_mapping.yaml
categories:
  new_category:
    description: "Description of new category"
    subcategories:
      - new_subcategory1
      - new_subcategory2
```

#### 2. Add Migration Rules (if needed)

```yaml
migration_rules:
  category_changes:
    - from: "old_category.old_subcategory"
      to: "new_category.new_subcategory"
```

#### 3. Test and Apply

```bash
# Test changes
python scripts/data_cleanup/migrations/migrate_categories.py --dry-run

# Apply changes
python scripts/data_cleanup/migrations/migrate_categories.py --apply
```

### Migration Statistics

Recent migration (2025-11-07):
- **Total Products**: 11,302
- **Products Affected**: 4,529 (40.1%)
- **Category Changes**: 1,344 products
- **Subcategory Splits**: 3,185 products

Major changes:
- `chocolate` → `mithai`: 617 products
- `sauce-ketchup-butter` → `sauce-ketchup`: 727 products
- Split `salt-sugar`: 919 products
- Split `chips-namkeen`: 485 products
- Split `pickles-chutney`: 944 products

## 🔮 Future Enhancements

### Planned Features

1. **LLM Integration** ✅ **In Progress**
   - AI-powered nutrition data enhancement
   - Product description generation
   - Category classification with confidence scoring
   - Clean name extraction

2. **Advanced Data Sources**
   - OpenFoodFacts integration
   - Barcode scanning
   - OCR for nutrition labels

3. **Performance Optimizations**
   - Image caching
   - Database indexing
   - Lazy loading

4. **Advanced UI Features**
   - Dark mode support
   - Accessibility improvements
   - Offline-first architecture

5. **Category Management** ✅ **Completed**
   - YAML-based configuration
   - Automated migration system
   - Validation and rollback capabilities

---

**Document Status**: Current and Accurate  
**Last Updated**: 2025-11-07  
**Maintained By**: Development Team