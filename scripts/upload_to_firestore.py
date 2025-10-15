import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import time
import math
import json

# --- Configuration ---
SERVICE_ACCOUNT_KEY_PATH = r"C:/Users/anujg/Desktop/AI/FireBase_Keys/food-nutririon-firebase-adminsdk-fbsvc-15e01706f9.json"
CSV_FILE_PATH = "../data/products.csv"  # Relative path to the CSV file
COLLECTION_NAME = "products"

# --- Firebase Initialization ---
def initialize_firebase():
    """Initializes the Firebase Admin SDK."""
    try:
        cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        print("Please ensure your service account key path is correct and the file is accessible.")
        return None

# --- Data Transformation ---
def transform_row_to_document(row):
    """Transforms a CSV row (Pandas Series) into a Firestore document dictionary."""
    doc_id = str(row.get('id', '')).strip()
    if not doc_id:
        return None, None

    # Helper to convert values to appropriate types
    def to_float(value):
        if pd.isna(value) or value == '' or value == 'nan':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    def to_bool(value):
        if pd.isna(value) or value == '' or value == 'nan':
            return False
        return str(value).lower() in ['true', '1', 'yes']

    def to_int(value):
        if pd.isna(value) or value == '' or value == 'nan':
            return 0
        try:
            return int(value)
        except (ValueError, TypeError):
            return 0

    # Parse nutrition data from JSON string
    nutrition_data = {}
    try:
        nutrition_json = str(row.get('nutrition_data', '{}'))
        if nutrition_json and nutrition_json != 'nan':
            nutrition_data = json.loads(nutrition_json)
    except (json.JSONDecodeError, TypeError):
        nutrition_data = {}

    # Construct the document with new schema
    document = {
        'id': doc_id,
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
        'search_count': to_int(row.get('search_count')),
        'llm_fallback_used': to_bool(row.get('llm_fallback_used')),
        'data_quality_score': to_int(row.get('data_quality_score')),
        'metadata': {
            'version': 2,
            'createdAt': int(time.time() * 1000),
            'updatedAt': int(time.time() * 1000),
            'firebase_uploaded': True
        }
    }
    return doc_id, document

# --- Main Execution ---
def main():
    """Main function to run the upload process."""
    db = initialize_firebase()
    if not db:
        return

    try:
        # Read CSV with custom || separator
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if not lines:
            print("Error: CSV file is empty")
            return
            
        # Parse header and data manually
        header = lines[0].strip().split('||')
        data_rows = []
        
        for line in lines[1:]:
            if line.strip():
                row_data = line.strip().split('||')
                # Ensure all rows have the same number of columns as header
                while len(row_data) < len(header):
                    row_data.append('')
                data_rows.append(row_data[:len(header)])  # Truncate if too many columns
        
        df = pd.DataFrame(data_rows, columns=header)
        df = df.astype(str)  # Convert all to string for consistent handling
        print(f"Successfully read {len(df)} rows from {CSV_FILE_PATH}")
        print(f"Columns: {list(df.columns)}")
        
    except FileNotFoundError:
        print(f"Error: The file was not found at {CSV_FILE_PATH}")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    batch = db.batch()
    commit_count = 0
    total_uploads = 0
    batch_size = 100  # Smaller batches to avoid quota issues

    print("Starting upload process...")
    print("Note: Using smaller batches to avoid quota limits...")
    
    for index, row in df.iterrows():
        doc_id, document_data = transform_row_to_document(row)

        if doc_id and document_data:
            doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
            batch.set(doc_ref, document_data)
            commit_count += 1
            total_uploads += 1

            # Use smaller batches to avoid quota issues
            if commit_count >= batch_size:
                try:
                    print(f"Committing batch of {commit_count} documents... (Total: {total_uploads})")
                    batch.commit()
                    batch = db.batch() # Start a new batch
                    commit_count = 0
                    
                    # Add delay to avoid quota issues
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"Error committing batch: {e}")
                    print("Continuing with next batch...")
                    batch = db.batch() # Start a new batch
                    commit_count = 0
                    time.sleep(2)  # Longer delay on error

    # Commit any remaining documents in the last batch
    if commit_count > 0:
        try:
            print(f"Committing final batch of {commit_count} documents...")
            batch.commit()
        except Exception as e:
            print(f"Error committing final batch: {e}")

    print(f"\nUpload complete. Total documents processed: {total_uploads}")
    print("Note: Some documents may not have been uploaded due to quota limits.")
    print("You can run the script again to continue uploading remaining documents.")

if __name__ == "__main__":
    main()
