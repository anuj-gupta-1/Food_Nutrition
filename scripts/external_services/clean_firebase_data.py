import firebase_admin
from firebase_admin import credentials, firestore
import os

def initialize_firebase():
    """Initialize Firebase Admin SDK"""
    try:
        service_account_path = os.getenv(
            "SERVICE_ACCOUNT_KEY_PATH",
            r"C:/Users/anujg/Desktop/AI/FireBase_Keys/food-nutririon-firebase-adminsdk-fbsvc-15e01706f9.json"
        )
        cred = credentials.Certificate(service_account_path)
        firebase_admin.initialize_app(cred)
        print("Firebase Admin SDK initialized successfully.")
        return firestore.client()
    except Exception as e:
        print(f"Error initializing Firebase: {e}")
        return None

def clean_old_categories(db, categories_to_remove=None):
    """Remove products from old/unwanted categories"""
    if categories_to_remove is None:
        categories_to_remove = ['oil', 'beverages', 'oils']  # Old categories to remove
    
    print(f"Cleaning Firebase data - removing categories: {categories_to_remove}")
    
    # Get all products
    products_ref = db.collection('products')
    docs = products_ref.stream()
    
    deleted_count = 0
    total_count = 0
    
    for doc in docs:
        total_count += 1
        data = doc.to_dict()
        category = data.get('category', '').lower()
        
        if category in categories_to_remove:
            print(f"  -> Deleting: {data.get('product_name', 'Unknown')} (category: {category})")
            doc.reference.delete()
            deleted_count += 1
    
    print(f"\n✅ Cleanup complete:")
    print(f"   Total products checked: {total_count}")
    print(f"   Products deleted: {deleted_count}")
    print(f"   Products remaining: {total_count - deleted_count}")

def list_categories(db):
    """List all categories currently in Firebase"""
    products_ref = db.collection('products')
    docs = products_ref.stream()
    
    categories = {}
    for doc in docs:
        data = doc.to_dict()
        category = data.get('category', 'unknown')
        categories[category] = categories.get(category, 0) + 1
    
    print("\n📊 Current categories in Firebase:")
    for category, count in sorted(categories.items()):
        print(f"   {category}: {count} products")
    
    return categories

def main():
    """Main cleanup function"""
    db = initialize_firebase()
    if not db:
        return
    
    print("=== Firebase Data Cleanup ===\n")
    
    # List current categories
    categories = list_categories(db)
    
    # Ask user which categories to remove
    print(f"\nFound categories: {list(categories.keys())}")
    categories_input = input("\nEnter categories to remove (comma-separated, or 'oil,beverages' for default): ").strip()
    
    if not categories_input:
        categories_to_remove = ['oil', 'beverages', 'oils']
    else:
        categories_to_remove = [cat.strip().lower() for cat in categories_input.split(',')]
    
    # Confirm deletion
    confirm = input(f"\n⚠️  This will DELETE all products in categories: {categories_to_remove}\nContinue? (y/N): ").lower().strip()
    
    if confirm == 'y':
        clean_old_categories(db, categories_to_remove)
        
        # Show updated categories
        print("\n" + "="*50)
        list_categories(db)
    else:
        print("Cleanup cancelled.")

if __name__ == "__main__":
    main()