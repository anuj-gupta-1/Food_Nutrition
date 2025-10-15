import pandas as pd
import os
import re
import json
import uuid
from datetime import datetime, timezone

# --- Configuration ---
SOURCE_FILES = {
    'jiomart': '../Scraping/fmcg_products_jiomart.csv',
    'frugivore': '../Scraping/fmcg_products_frugivore.csv',
    'starquik': '../Scraping/fmcg_products_StarQuik.csv'
}
OUTPUT_FILE_PATH = '../data/products.csv'

# Define the exact schema for the final master CSV file with || separators
FINAL_SCHEMA = [
    'id', 'product_name', 'brand', 'category', 'subcategory', 'size_value', 'size_unit', 
    'price', 'source', 'source_url', 'ingredients', 'nutrition_data', 'image_url', 
    'last_updated', 'search_count', 'llm_fallback_used', 'data_quality_score'
]

# --- Helper Functions ---
def generate_product_id(name, brand, source):
    """Generates a unique product ID from name, brand, and source."""
    if pd.isna(name) or not name:
        return str(uuid.uuid4())
    
    # Try to extract barcode/UPCEAN if available in name
    barcode_match = re.search(r'\b\d{8,14}\b', str(name))
    if barcode_match:
        return barcode_match.group()
    
    # Generate ID from name and brand
    base_string = f"{brand or ''} {name}".strip()
    s = re.sub(r'[^a-zA-Z0-9\s]', '', base_string).lower()
    s = re.sub(r'\s+', '_', s)
    return f"{source}_{s[:100]}"

def normalize_brand(brand):
    """Normalize brand names."""
    if pd.isna(brand) or not brand:
        return "Unknown Brand"
    return str(brand).strip().title()

def normalize_category(category, subcategory):
    """Normalize category and subcategory."""
    if pd.isna(category):
        category = "uncategorized"
    if pd.isna(subcategory):
        subcategory = "general"
    return str(category).strip().lower(), str(subcategory).strip().lower()

def clean_price(price_str):
    """Clean and convert price to numeric value."""
    if pd.isna(price_str) or not price_str:
        return None
    
    # Remove currency symbols and extract numeric value
    price_clean = re.sub(r'[₹$€£,]', '', str(price_str))
    price_match = re.search(r'(\d+\.?\d*)', price_clean)
    
    if price_match:
        return float(price_match.group(1))
    return None

def calculate_data_quality_score(row):
    """Calculate data quality score (0-100) based on available fields."""
    score = 0
    max_score = 100
    
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
    
    return min(score, max_score)

def create_nutrition_data():
    """Create default empty nutrition data structure."""
    return json.dumps({
        "energy_kcal": None,
        "fat_g": None,
        "saturated_fat_g": None,
        "carbs_g": None,
        "sugars_g": None,
        "protein_g": None,
        "salt_g": None,
        "fiber_g": None,
        "sodium_mg": None
    })

def process_source_file(source_name, file_path):
    """Process a single source file and return processed dataframe."""
    print(f"Processing {source_name} source file: {file_path}")
    
    try:
        # Read the source file with appropriate separator and error handling
        if source_name == 'jiomart':
            # For JioMart, manually parse to handle corrupted data
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if not lines:
                return pd.DataFrame(columns=FINAL_SCHEMA)
            
            header = lines[0].strip().split('||')
            data_rows = []
            
            for i, line in enumerate(lines[1:], 1):
                if line.strip():
                    row_data = line.strip().split('||')
                    # Skip rows that don't have the expected number of columns
                    if len(row_data) == len(header):
                        data_rows.append(row_data)
                    else:
                        print(f"  -> Skipping malformed row {i} (expected {len(header)} fields, got {len(row_data)})")
            
            df = pd.DataFrame(data_rows, columns=header)
        else:
            df = pd.read_csv(file_path, sep=',', engine='python', on_bad_lines='skip')
        
        # Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]
        print(f"  -> Found {len(df)} raw products from {source_name}")
        
        # Create processed dataframe
        processed_df = pd.DataFrame(columns=FINAL_SCHEMA)
        
        # Map common fields with safe handling
        processed_df['product_name'] = df.get('name', pd.Series([''] * len(df)))
        processed_df['brand'] = df.get('brand', pd.Series([''] * len(df))).apply(normalize_brand)
        processed_df['size_value'] = df.get('size_value', pd.Series([''] * len(df)))
        processed_df['size_unit'] = df.get('size_unit', pd.Series([''] * len(df)))
        processed_df['price'] = df.get('price', pd.Series([''] * len(df))).apply(clean_price)
        processed_df['source_url'] = df.get('url', pd.Series([''] * len(df)))
        
        # Handle category and subcategory safely
        category_col = df.get('category', pd.Series([''] * len(df)))
        subcategory_col = df.get('subcategory', pd.Series([''] * len(df)))
        
        processed_df['category'] = category_col.apply(lambda x: normalize_category(x, '')[0])
        processed_df['subcategory'] = subcategory_col.apply(lambda x: normalize_category('', x)[1])
        
        # Add metadata
        processed_df['source'] = source_name
        processed_df['last_updated'] = datetime.now(timezone.utc).isoformat()
        processed_df['search_count'] = 0
        processed_df['llm_fallback_used'] = False
        processed_df['ingredients'] = ''
        processed_df['nutrition_data'] = create_nutrition_data()
        processed_df['image_url'] = ''
        
        # Generate IDs
        processed_df['id'] = processed_df.apply(
            lambda row: generate_product_id(row.get('product_name'), row.get('brand'), source_name),
            axis=1
        )
        
        # Calculate data quality scores
        processed_df['data_quality_score'] = processed_df.apply(calculate_data_quality_score, axis=1)
        
        # Clean data
        processed_df.dropna(subset=['product_name', 'id'], inplace=True)
        processed_df.drop_duplicates(subset=['id'], keep='first', inplace=True)
        
        print(f"  -> Processed {len(processed_df)} unique products from {source_name}")
        return processed_df
        
    except FileNotFoundError:
        print(f"  -> Warning: File not found for {source_name}: {file_path}")
        return pd.DataFrame(columns=FINAL_SCHEMA)
    except Exception as e:
        print(f"  -> Error processing {source_name}: {e}")
        return pd.DataFrame(columns=FINAL_SCHEMA)

# --- Main Processing Logic ---
def main():
    """Main function to process all source files and create the master product file."""
    print("Starting data consolidation process...")
    print("=" * 50)
    
    # Process all source files
    all_processed_dfs = []
    
    for source_name, file_path in SOURCE_FILES.items():
        processed_df = process_source_file(source_name, file_path)
        if not processed_df.empty:
            all_processed_dfs.append(processed_df)
    
    if not all_processed_dfs:
        print("No source files could be processed. Exiting.")
        return
    
    # Combine all processed dataframes
    print("\nCombining data from all sources...")
    master_df = pd.concat(all_processed_dfs, ignore_index=True)
    
    # Final deduplication across sources (keep the one with highest quality score)
    print("Performing final deduplication...")
    master_df = master_df.sort_values('data_quality_score', ascending=False)
    master_df = master_df.drop_duplicates(subset=['id'], keep='first')
    
    print(f"  -> Total unique products after final deduplication: {len(master_df)}")
    
    # Save the final file
    print("\nSaving master product file...")
    try:
        # Ensure all columns are in the correct order
        final_df = master_df[FINAL_SCHEMA]
        
        os.makedirs(os.path.dirname(OUTPUT_FILE_PATH), exist_ok=True)
        # Write with custom separator (pandas doesn't support multi-char separators)
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
            # Write header
            f.write('||'.join(FINAL_SCHEMA) + '\n')
            # Write data rows
            for _, row in final_df.iterrows():
                row_values = []
                for col in FINAL_SCHEMA:
                    value = str(row[col]) if pd.notna(row[col]) else ''
                    # Escape any || characters in the data
                    value = value.replace('||', '| |')
                    row_values.append(value)
                f.write('||'.join(row_values) + '\n')
        
        print(f"\n✅ Successfully created master product file!")
        print(f"   Location: {os.path.abspath(OUTPUT_FILE_PATH)}")
        print(f"   Total products: {len(final_df)}")
        print(f"   Sources included: {', '.join(final_df['source'].unique())}")
        
        # Print summary statistics
        print("\n📊 Data Quality Summary:")
        quality_stats = final_df['data_quality_score'].describe()
        print(f"   Average quality score: {quality_stats['mean']:.1f}")
        print(f"   Products by source:")
        for source in final_df['source'].unique():
            count = len(final_df[final_df['source'] == source])
            print(f"     {source}: {count} products")
            
    except Exception as e:
        print(f"\n❌ Error saving final CSV file: {e}")

if __name__ == "__main__":
    main()