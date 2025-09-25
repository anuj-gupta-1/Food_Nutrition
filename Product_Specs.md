# Food Nutrition Comparison Android App - Product Specifications

**Document Version**: 2.0  
**Last Updated**: 2025-07-25

---

## 1. Project Overview

-   **Project Type**: Native Android Application (MVP Phase)
-   **Target Market**: India
-   **Vision**: To build a comprehensive food nutrition comparison platform that helps Indian consumers make informed dietary choices by providing standardized, comparable nutrition data.
-   **Constraint**: Use only open-source and free tools.
-   **Current Status**: MVP development complete. The app is ready for testing and refinement.

## 2. System Architecture

The project follows a simple, scalable architecture:

```
Data Sources → Scraping Scripts → Raw Data → Processing → Standardized CSV → Android App
     ↓              ↓              ↓           ↓              ↓              ↓
OpenFoodFacts   scrape_*.py    raw_data/   standardize.py    data/        Native App
(and others)    (Python)       images/     (Python)      products.csv   (Kotlin)
```

## 3. Data Collection & Processing Journey

### 3.1 Data Sources Exploration

#### OpenFoodFacts
- Primary and most reliable source
- Well-structured JSON data
- Standardized nutrition information
- Comprehensive product images
- Implementation: `scripts/scrape_openfoodfacts.py`

#### E-commerce Platforms

**StarQuik**
- Successfully implemented
- Clean data structure
- Limited product categories
- Implementation: `Scraping/fmcg_scraper_selenium_StarQuik.py`

**Frugivore**
- Successfully implemented
- Product data extracted using Selenium
- Nutrition information available in structured format
- Good coverage for organic products
- Implementation: `Scraping/fmcg_scraper_selenium_frugivore.py`

**JioMart**
- Attempted but faced challenges
- Strong anti-bot measures prevented automated scraping
- Attempted approaches:
  - Basic Selenium automation
  - Headless browsing
  - Anti-detection measures
  - Browser fingerprint randomization
- Current status: On hold due to technical limitations

### 3.2 Data Collection Challenges

1. **Anti-Bot Measures**
   - Dynamic page loading
   - CAPTCHAs
   - IP-based rate limiting
   - Browser fingerprinting detection
   - JavaScript-based bot detection

2. **Data Consistency**
   - Different units (per 100g vs per serving)
   - Varying nutrition label formats
   - Inconsistent product categorization
   - Multiple variations of same product

3. **Image Processing**
   - Attempted OCR on nutrition labels
   - Challenges with image quality
   - Varying label formats
   - Multi-language content

### 3.3 Data Processing Pipeline

1. **Raw Data Collection**
   - JSON data stored in `raw_data/`
   - Images saved in `images/`
   - Source-specific CSV files in `Scraping/`:
     - `fmcg_products_frugivore.csv` (from Frugivore scraper)
     - `fmcg_products_StarQuik.csv` (from StarQuik scraper)
     - `fmcg_products_jiomart.csv` (from JioMart scraper)

2. **Data Standardization** (`scripts/standardize_nutrition.py`)
   - Unit conversion to per 100g/ml
   - Nutrient value normalization
   - Category standardization
   - Brand name normalization
   - Serving size standardization

3. **Data Quality Checks**
   - Validation of nutrient values
   - Removal of duplicates
   - Missing data handling
   - Outlier detection

4. **Output**
   - Final, clean dataset stored in `data/products.csv`
   - Standardized image references
   - Validated nutrition information

### Data Schema

The `products.csv` file and the corresponding Room `Product` entity in the app use the following schema:

| Field Name           | Type  | Description                  | Example             |
| -------------------- | ----- | ---------------------------- | ------------------- |
| id                   | Text  | Unique product identifier    | 5449000054227       |
| productName          | Text  | Product name                 | "Original Taste"    |
| brand                | Text  | Brand name                   | "Coca-Cola"         |
| category             | Text  | Product category             | "Carbonated Drinks" |
| ingredients          | Text  | Ingredients list             | "Water, fructose..."|
| servingSize          | Text  | Serving size information     | "250 ml"            |
| energyKcal100g       | Float | Energy per 100g (kcal)       | 42.0                |
| fat100g              | Float | Fat per 100g                 | 0.0                 |
| saturatedFat100g     | Float | Saturated fat per 100g       | 0.0                 |
| carbs100g            | Float | Carbohydrates per 100g       | 10.6                |
| sugars100g           | Float | Sugars per 100g              | 10.6                |
| protein100g          | Float | Protein per 100g             | 0.0                 |
| salt100g             | Float | Salt per 100g                | 0.0                 |
| fiber100g            | Float | Fiber per 100g               | (varies)            |
| sodium100g           | Float | Sodium per 100g              | 0.0                 |

*(Note: The original scraping script captures more fields, which are backed up in `raw_data/` for future use.)*

## 4. Android App MVP (Completed ✅)

The Minimum Viable Product (MVP) for the Android app has been fully implemented.

### Technical Stack
-   **Language**: Kotlin
-   **UI**: Jetpack Compose
-   **Database**: Room (over SQLite) for local data storage.
-   **Navigation**: Jetpack Navigation Component.
-   **Dependencies**: All managed via `build.gradle`.

### Data Flow in App
1.  **Asset Loading**: On first launch, the app copies `products.csv` from its assets into the local Room database.
2.  **Offline First**: All subsequent reads are performed directly from the local database, ensuring offline functionality.

### Core Components
-   `Product.kt`: The Room `@Entity` data class.
-   `ProductDao.kt`: Data Access Object for all database queries.
-   `AppDatabase.kt`: The Room database singleton.
-   `CsvParser.kt`: A utility to parse the CSV file.
-   `MainActivity.kt`: The app's entry point, which initializes the database and UI.

### UI Screens & Navigation
-   `AppNavigation.kt`: Defines the navigation graph between screens.
-   `CategoryScreen.kt`: Displays a list of hardcoded categories.
-   `ProductSelectionScreen.kt`: Allows the user to select exactly two products from a chosen category.
-   `ComparisonScreen.kt`: Shows a side-by-side comparison of the selected products' nutrition data.

## 5. How to Run the App

1.  **Open Android Studio**.
2.  Select **File > Open**.
3.  Navigate to and select the `c:\Users\anujg\Desktop\AI\Food_Nutrition\android_app` directory.
4.  Wait for Android Studio to sync the Gradle project.
5.  Select a target emulator or connect a physical device.
6.  Click the **Run 'app'** button.

## 6. Final Project File Structure

```
Food_Nutrition/
├── android_app/      # Complete Android Studio project source
│   └── app/
│       ├── src/
│       └── build.gradle
├── data/
│   └── products.csv  # Standardized, clean data for the app
├── images/           # Product images downloaded by the scraper
├── raw_data/         # Raw JSON data from scraping
├── scripts/          # Python scripts for data processing
│   ├── scrape_openfoodfacts.py
│   └── standardize_nutrition.py
└── Product_Specs.md  # This document
```

## 7. Next Steps & Future Work

### Short Term (Refinement)
-   Thoroughly test the app on different devices and screen sizes.
-   Refine the UI/UX for clarity and ease of use.
-   Add loading indicators and error handling for a smoother experience.
-   Enhance the comparison table UI to better highlight differences.

### Medium Term (Post-MVP)
-   **Expand Data**: Scrape more categories and products from OpenFoodFacts.
-   **New Data Sources**: Integrate scrapers for e-commerce sites (e.g., BigBasket, Amazon.in).
-   **Image OCR**: Implement an OCR pipeline to extract nutrition data from images.

### Long Term (Advanced Features)
-   **AI/ML**: Use AI for dynamic categorization, ingredient analysis, and health scoring.
-   **User Features**: Implement search, filtering, barcode scanning, and user accounts.

## 8. To Be Covered in Future Updates
- User personas
- Success metrics
- Competitive analysis
- Risk assessment
- Privacy considerations
- Compliance requirements (FSSAI, etc.)

## Data Distribution (Firebase Hosting)
- The standardized dataset is published as `products.csv` on Firebase Hosting.
- Clients (e.g., Android app) fetch the CSV from the public Hosting URL on user-triggered refresh.
- Deployments are automated via GitHub Actions when changes are pushed to `main`.
