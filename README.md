# Food Nutrition Comparison App

A comprehensive Android application for comparing food nutrition information, specifically designed for the Indian market. This app helps consumers make informed dietary choices by providing standardized, comparable nutrition data.

## 🚀 Current Status: Production Ready

- ✅ **Android App**: Fully functional with Jetpack Compose UI
- ✅ **Data Pipeline**: Operational with 45 dairy products from StarQuik
- ✅ **Firebase Integration**: Real-time data sync with Firestore
- ✅ **Offline Support**: Local database with Room
- ✅ **Product Comparison**: Side-by-side nutrition comparison

## 📱 App Features

### Current Features
- **Category Browsing**: Browse products by category (currently "diary")
- **Product Selection**: Select up to 2 products for comparison
- **Nutrition Comparison**: Side-by-side comparison of nutrition data
- **Search Functionality**: Search products by name or brand
- **Offline Mode**: Works without internet connection
- **Firebase Sync**: Real-time data updates from cloud

### Data Coverage
- **Products**: 45 dairy products from StarQuik
- **Categories**: Dairy products with comprehensive nutrition data
- **Quality Score**: Average 83.3/100 data quality rating
- **Source Tracking**: Full traceability of data sources

## 🏗️ Architecture

```
Data Sources → Processing → Main DB → Firebase → Android App
     ↓            ↓          ↓         ↓          ↓
  StarQuik    consolidate_  CSV    Firestore   Kotlin App
  (Future)      data.py    Database   Cloud     (Compose)
```

## 🛠️ Technical Stack

### Android App
- **Language**: Kotlin
- **UI Framework**: Jetpack Compose
- **Database**: Room (SQLite)
- **Navigation**: Jetpack Navigation Component
- **Cloud**: Firebase Firestore
- **Build**: Gradle

### Backend
- **Language**: Python
- **Data Processing**: Pandas
- **Cloud**: Firebase Admin SDK
- **Storage**: CSV + Firestore

## 📊 Data Schema

The main product database uses `||` separated values with 17 comprehensive fields:

| Field | Description | Example |
|-------|-------------|---------|
| `id` | Unique identifier | `starquik_gowardhan_curd_cup_400_gm` |
| `product_name` | Product name | `Gowardhan Curd Cup 400 Gm` |
| `brand` | Brand name | `Gowardhan` |
| `category` | Main category | `diary` |
| `source` | Data source | `starquik` |
| `nutrition_data` | JSON nutrition info | `{"energy_kcal": 42, ...}` |
| `data_quality_score` | Quality rating (0-100) | `90` |

## 🚀 Quick Start

### Prerequisites
- Android Studio Arctic Fox+
- Python 3.8+
- Firebase project setup

### Running the Android App

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Food_Nutrition
   ```

2. **Open in Android Studio**
   ```bash
   # Open the android_app directory in Android Studio
   # File > Open > Select android_app folder
   ```

3. **Build and Run**
   ```bash
   cd android_app
   ./gradlew assembleDebug
   # Install the APK from: android_app/app/build/outputs/apk/debug/app-debug.apk
   ```

### Updating Data

1. **Process new data**
   ```bash
   cd scripts
   python consolidate_data.py
   ```

2. **Upload to Firebase**
   ```bash
   python upload_to_firestore.py
   ```

3. **Update Android app**
   ```bash
   copy ../data/products.csv ../android_app/app/src/main/assets/products.csv
   cd ../android_app
   ./gradlew assembleDebug
   ```

## 📁 Project Structure

```
Food_Nutrition/
├── android_app/              # Android Studio project
│   ├── app/src/main/java/    # Kotlin source code
│   ├── app/src/main/assets/  # App data (products.csv)
│   └── build.gradle          # Build configuration
├── data/
│   └── products.csv          # Main product database
├── scripts/
│   ├── consolidate_data.py   # Data processing pipeline
│   └── upload_to_firestore.py # Firebase integration
├── Scraping/
│   └── fmcg_products_*.csv   # Source data files
└── Product_Specs.md          # Detailed documentation
```

## 🔄 Data Pipeline

### Current Sources
- ✅ **StarQuik**: 45 dairy products (active)
- ⚠️ **JioMart**: Data corruption issues (being fixed)
- 📋 **OpenFoodFacts**: Integration planned

### Data Processing
1. **Collection**: Source scrapers collect product data
2. **Consolidation**: `consolidate_data.py` processes and standardizes
3. **Validation**: Quality scoring and error handling
4. **Storage**: CSV database + Firebase Firestore
5. **Distribution**: Android app with offline support

## 🎯 Roadmap

### Short Term (2-4 weeks)
- **LLM Integration**: AI-powered nutrition data enhancement
- **Additional Sources**: Fix JioMart data, add OpenFoodFacts
- **UI Improvements**: Better nutrition visualization

### Medium Term (1-3 months)
- **Advanced Features**: Barcode scanning, user accounts
- **Analytics**: Search patterns, popular categories
- **Performance**: Optimization and caching

### Long Term (3-6 months)
- **Scalability**: Microservices, real-time streaming
- **Advanced AI**: Health recommendations, ingredient analysis
- **Social Features**: Reviews, sharing, community

## 📈 Performance

- **App Size**: ~15MB APK
- **Startup Time**: < 2 seconds
- **Database Queries**: < 100ms
- **Memory Usage**: < 50MB
- **Offline Support**: Full functionality without internet

## 🔧 Development

### Building the App
```bash
cd android_app
./gradlew assembleDebug
```

### Data Processing
```bash
cd scripts
python consolidate_data.py
```

### Firebase Upload
```bash
python upload_to_firestore.py
```

## 📋 Documentation

- **Product Specifications**: `Product_Specs.md` - Comprehensive technical documentation
- **API Documentation**: Available in the Android app source code
- **Data Schema**: Detailed in Product_Specs.md

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 📞 Support

For technical support or questions:
- Check the documentation in `Product_Specs.md`
- Review the source code in `android_app/app/src/main/java/`
- Open an issue for bugs or feature requests

---

**Last Updated**: 2025-10-15  
**Version**: 3.0  
**Status**: Production Ready ✅