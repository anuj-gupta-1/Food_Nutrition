import pandas as pd
import firebase_admin
from firebase_admin import credentials, firestore
import time
import json

# --- Configuration ---
SERVICE_ACCOUNT_KEY_PATH = r"C:/Users/anujg/Desktop/AI/FireBase_Keys/food-nutririon-firebase-adminsdk-fbsvc-15e01706f9.json"
CSV_FILE_PATH = "../data/products.csv"
COLLECTION_NAME = "products_test"

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
        return None

def test_upload():
    """Test upload with just 5 products"""
    db = initialize_firebase()
    if not db:
        return

    # Read just first 5 rows for testing
    try:
        with open(CSV_FILE_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        header = lines[0].strip().split('||')
        test_rows = []
        
        for line in lines[1:6]:  # Just first 5 data rows
            if line.strip():
                row_data = line.strip().split('||')
                while len(row_data) < len(header):
                    row_data.append('')
                test_rows.append(row_data[:len(header)])
        
        df = pd.DataFrame(test_rows, columns=header)
        df = df.astype(str)
        print(f"Testing with {len(df)} products")
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    # Upload test documents
    for index, row in df.iterrows():
        doc_id = str(row.get('id', '')).strip()
        if not doc_id:
            continue
            
        # Simple document structure for testing
        document = {
            'id': doc_id,
            'product_name': str(row.get('product_name', '')).strip(),
            'brand': str(row.get('brand', '')).strip(),
            'source': str(row.get('source', '')).strip(),
            'test_upload': True,
            'timestamp': int(time.time() * 1000)
        }
        
        try:
            doc_ref = db.collection(COLLECTION_NAME).document(doc_id)
            doc_ref.set(document)
            print(f"✅ Uploaded: {doc_id} - {document['product_name']}")
        except Exception as e:
            print(f"❌ Error uploading {doc_id}: {e}")

    print(f"\nTest upload complete!")

if __name__ == "__main__":
    test_upload()

