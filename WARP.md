# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

Project overview
- Android Kotlin app (Jetpack Compose) in android_app, backed by Room (SQLite) with Firebase Firestore sync and CSV fallback. Supporting Python data pipeline in scripts/ generating data/products.csv.
- Key dirs: android_app/ (Gradle project), data/ (master CSV), scripts/ (ETL + Firebase upload), Scraping/ (raw sources).

Prerequisites
- Android Studio (or Android SDK + Gradle Wrapper) and Java 17+.
- Python 3.8+ for scripts/.
- Firebase: google-services.json placed at android_app/app/google-services.json and Firestore enabled (collection products). The Android app uses the Google Services Gradle plugin.

Common commands
- Build (Debug):
```bash path=null start=null
# Unix/macOS
cd android_app && ./gradlew :app:assembleDebug
```
```powershell path=null start=null
# Windows PowerShell
cd android_app; .\gradlew.bat :app:assembleDebug
```
- Build (Release):
```bash path=null start=null
cd android_app && ./gradlew :app:assembleRelease
```
```powershell path=null start=null
cd android_app; .\gradlew.bat :app:assembleRelease
```
- Clean:
```bash path=null start=null
cd android_app && ./gradlew clean
```
```powershell path=null start=null
cd android_app; .\gradlew.bat clean
```
- Lint (Android Lint):
```bash path=null start=null
cd android_app && ./gradlew :app:lint
```
```powershell path=null start=null
cd android_app; .\gradlew.bat :app:lint
```
- Unit tests (local JVM):
```bash path=null start=null
cd android_app && ./gradlew :app:testDebugUnitTest
```
```powershell path=null start=null
cd android_app; .\gradlew.bat :app:testDebugUnitTest
```
- Run a single unit test:
```bash path=null start=null
cd android_app && ./gradlew :app:testDebugUnitTest --tests "com.foodnutrition.app.<TestClassName>"
```
```powershell path=null start=null
cd android_app; .\gradlew.bat :app:testDebugUnitTest --tests "com.foodnutrition.app.<TestClassName>"
```
- Instrumented tests (device/emulator required):
```bash path=null start=null
cd android_app && ./gradlew :app:connectedDebugAndroidTest
```
```powershell path=null start=null
cd android_app; .\gradlew.bat :app:connectedDebugAndroidTest
```

Data pipeline (Python)
- Consolidate sources into master CSV (writes data/products.csv):
```bash path=null start=null
python scripts/consolidate_data.py
```
- Upload master CSV to Firestore (requires service account key):
```bash path=null start=null
# Edit scripts/upload_to_firestore.py to set SERVICE_ACCOUNT_KEY_PATH, or parameterize via env var before running
python scripts/upload_to_firestore.py
```
- Quick test upload of 5 docs to products_test:
```bash path=null start=null
python scripts/test_firebase_upload.py
```

High-level architecture
- UI (Compose):
  - Entry: MainActivity sets up Room (AppDatabase.getDatabase), obtains ProductDao and DataManager, launches initializeData(), and composes FoodNutritionApp.
  - Navigation (AppNavigation): NavHost with routes categories → products/{category} → comparison, passing selected products via savedStateHandle.
  - Screens: CategoryScreen (hardcoded categories), ProductSelectionScreen (select up to 2 products), ComparisonScreen (tabular side-by-side view). Core nutrient rendering is currently stubbed; values are shown as N/A until persisted fields are wired up.
- Data layer:
  - Persistence: Room with entity Product and DAO ProductDao (category queries, search, counts, wipes). Database version=2 with fallbackToDestructiveMigration.
  - Sync: DataManager orchestrates startup sync; checks last fetch time in SharedPreferences and either fetches Firestore or falls back to CSV assets (products.csv embedded under app/src/main/assets/). On successful fetch/parse, it truncates and repopulates Room.
  - Firestore: FirebaseRepository reads collection products into Product objects using KTX and coroutines.
  - CSV ingestion: CsvParser reads data/products.csv schema (||-separated, 17 columns), parses nutrition_data JSON, builds Product records. NutritionData currently tracks availability/metadata; Converters for NutritionValue maps exist but the Product/NutritionData types don’t yet persist a values map.
- Build/Config:
  - Gradle (android_app): AGP 8.2.2, Kotlin 1.9.22, Compose Compiler 1.5.8, Room 2.6.1 (KSP), Navigation 2.7.7, Firebase BOM 32.7.0. Google Services plugin is applied to :app.
  - Packaging: minSdk 21, target/compileSdk 34, Material3, compose enabled, standard exclusions.

Operational notes
- Ensure android_app/app/google-services.json matches the Firestore project that scripts upload to. The upload scripts expect Firestore documents keyed by id in collection products with the schema emitted by consolidate_data.py.
- To bundle offline data, copy data/products.csv to android_app/app/src/main/assets/products.csv before building; DataManager will use Firestore first and fall back to this asset.
- CategoryScreen currently uses hardcoded categories ("Carbonated Drinks", "Vegetable Oils"). Update DAO/querying if you want dynamic categories from Room.

Key README highlights
- Production-ready Android app with offline Room, real-time Firestore sync, and comparison UI.
- Data pipeline: consolidate_data.py → data/products.csv → upload_to_firestore.py → app fetch/sync; scripts/ also include OpenFoodFacts scraping utilities.
