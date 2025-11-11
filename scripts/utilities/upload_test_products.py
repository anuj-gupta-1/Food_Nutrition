#!/usr/bin/env python3
"""
Upload specific test products to Firebase to verify nutrition data fix
"""

import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import time
import json
import os
import sys

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))
from csv_handler import load_products_csv

# Firebase configuration
SERVICE_ACCOUNT_KEY_PATH = r"C:/Users/anujg/Desktop/AI/FireBase_Keys/food-nutririon-firebase-adminsdk-fbsvc-15e01706f9.json"
COLLECTION_NAME = "products"

def initialize_firebase():
    """Initialize Firebase Admin SDK."""
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

def to_float(value):
    """Convert value to float, return None if invalid."""
    if pd.isna(value) or value == '' or value == 'nan':
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

def upload_test_products():
    """Upload specific test products to Firebase."""
    db = initialize_firebase()
    if not db:
        return

    # Load CSV data
    df = load_products_csv()
    
    # Test product IDs
    test_ids = [
        'jiomart_coca_cola_coca_cola_750_ml',
        'jiomart_maaza_maaza_mango_drink_12_l'
    ]
    
    print(f"Uploading {len(test_ids)} test products to Firebase...")
    
    for product_id in test_ids:
        # Find the product in CSV
        product_row = df[df['id'] == product_id]
        
        if len(product_row) == 0:
            print(f"❌ Product {product_id} not found in CSV")
            continue
            
        row = product_row.iloc[0]
        
        # Parse nutrition data from JSON
        nutrition_data = {}
        try:
            nutrition_json = str(row.get('nutrition_data', '{}'))
            if nutrition_json and nutrition_json != 'nan':
                nutrition_data = json.loads(nutrition_json)
        except (json.JSONDecodeError, TypeError):
            nutrition_data = {}
        
        # Create document with individual nutrition columns
        document = {
            'id': str(row.get('id', '')).strip(),
            'product_name': str(row.get('product_name', '')).strip(),
            'brand': str(row.get('brand', '')).strip(),
            'category': str(row.get('category', '')).strip(),
            'subcategory': str(row.get('subcategory', '')).strip(),
            'size_value': to_float(row.get('size_value')),
            'size_unit': str(row.get('size_unit', '')).strip(),
            'price': to_float(row.get('price')),
            'source': str(row.get('source', '')).strip(),
            'source_url': str(row.get('source_url', '')).strip(),
            'ingredients': str(row.get('ingredients', '')).strip() or None,
            'nutrition_data': nutrition_data,
            'image_url': str(row.get('image_url', '')).strip() or None,
            'last_updated': str(row.get('last_updated', '')).strip(),
            # Individual nutrition columns for app compatibility
            'energy_kcal_per_100g': to_float(row.get('energy_kcal_per_100g')),
            'carbs_g_per_100g': to_float(row.get('carbs_g_per_100g')),
            'protein_g_per_100g': to_float(row.get('protein_g_per_100g')),
            'fat_g_per_100g': to_float(row.get('fat_g_per_100g')),
            'total_sugars_g_per_100g': to_float(row.get('total_sugars_g_per_100g')),
            'saturated_fat_g_per_100g': to_float(row.get('saturated_fat_g_per_100g')),
            'fiber_g_per_100g': to_float(row.get('fiber_g_per_100g')),
            'sodium_mg_per_100g': to_float(row.get('sodium_mg_per_100g')),
            'salt_g_per_100g': to_float(row.get('salt_g_per_100g')),
            'metadata': {
                'version': 2,
                'createdAt': int(time.time() * 1000),
                'updatedAt': int(time.time() * 1000),
                'firebase_uploaded': True,
                'test_upload': True
            }
        }
        
        try:
            # Upload to Firebase
            doc_ref = db.collection(COLLECTION_NAME).document(product_id)
            doc_ref.set(document)
            
            print(f"✅ Uploaded: {row['product_name']}")
            print(f"   Energy: {document['energy_kcal_per_100g']} kcal/100g")
            print(f"   Carbs: {document['carbs_g_per_100g']} g/100g")
            print(f"   Protein: {document['protein_g_per_100g']} g/100g")
            print(f"   Fat: {document['fat_g_per_100g']} g/100g")
            print()
            
        except Exception as e:
            print(f"❌ Error uploading {product_id}: {e}")
    
    print("Test upload complete!")

if __name__ == "__main__":
    upload_test_products()