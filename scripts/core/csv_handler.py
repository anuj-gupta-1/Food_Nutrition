#!/usr/bin/env python3
"""
Robust CSV Handler for Products Data
Handles the complex CSV format with || separators and embedded JSON/URLs
"""

import pandas as pd
import csv

def load_products_csv(file_path='data/products.csv'):
    """
    Safely load the products CSV file with proper handling of complex data
    
    Returns:
        pandas.DataFrame: The loaded products data
    """
    
    try:
        # Manual parsing method (most reliable)
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse header
        header = lines[0].strip().split('||')
        
        # Parse data lines
        data_rows = []
        
        for line in lines[1:]:
            fields = line.strip().split('||')
            
            # Handle field count mismatches
            if len(fields) < len(header):
                # Pad with empty strings
                fields.extend([''] * (len(header) - len(fields)))
            elif len(fields) > len(header):
                # Truncate extra fields (usually from URLs with || in them)
                fields = fields[:len(header)]
            
            data_rows.append(fields)
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=header)
        
        # Convert data types
        if 'size_value' in df.columns:
            df['size_value'] = pd.to_numeric(df['size_value'], errors='coerce')
        if 'price' in df.columns:
            df['price'] = pd.to_numeric(df['price'], errors='coerce')
        if 'search_count' in df.columns:
            df['search_count'] = pd.to_numeric(df['search_count'], errors='coerce')
        if 'data_quality_score' in df.columns:
            df['data_quality_score'] = pd.to_numeric(df['data_quality_score'], errors='coerce')
        
        # Handle boolean columns
        if 'llm_fallback_used' in df.columns:
            df['llm_fallback_used'] = df['llm_fallback_used'].map({
                'True': True, 'False': False, True: True, False: False
            }).fillna(False)
        
        return df
        
    except Exception as e:
        raise Exception(f"Failed to load CSV: {e}")

def save_products_csv(df, file_path='data/products.csv'):
    """
    Safely save the products DataFrame to CSV with proper formatting
    
    Args:
        df (pandas.DataFrame): The products data to save
        file_path (str): Path to save the CSV file
    """
    
    try:
        # Convert boolean columns to string for CSV
        df_copy = df.copy()
        
        if 'llm_fallback_used' in df_copy.columns:
            df_copy['llm_fallback_used'] = df_copy['llm_fallback_used'].astype(str)
        
        # Save with || separator using manual method
        with open(file_path, 'w', encoding='utf-8') as f:
            # Write header
            f.write('||'.join(df_copy.columns) + '\n')
            
            # Write data rows
            for _, row in df_copy.iterrows():
                row_data = []
                for col in df_copy.columns:
                    value = str(row[col]) if pd.notna(row[col]) else ''
                    row_data.append(value)
                f.write('||'.join(row_data) + '\n')
        
    except Exception as e:
        raise Exception(f"Failed to save CSV: {e}")

def get_enhanced_products_count():
    """Get count of LLM enhanced products"""
    try:
        df = load_products_csv()
        enhanced = df[df['llm_fallback_used'] == True]
        return len(enhanced)
    except:
        return 0

def get_beverage_stats():
    """Get beverage category statistics"""
    try:
        df = load_products_csv()
        beverages = df[df['category'] == 'beverage']
        enhanced_beverages = beverages[beverages['llm_fallback_used'] == True]
        
        return {
            'total_beverages': len(beverages),
            'enhanced_beverages': len(enhanced_beverages),
            'enhancement_rate': len(enhanced_beverages) / len(beverages) * 100 if len(beverages) > 0 else 0
        }
    except:
        return {'total_beverages': 0, 'enhanced_beverages': 0, 'enhancement_rate': 0}

if __name__ == "__main__":
    # Test the CSV handler
    print("🧪 TESTING CSV HANDLER")
    print("=" * 30)
    
    try:
        df = load_products_csv()
        print(f"✅ Loaded {len(df)} products")
        
        stats = get_beverage_stats()
        print(f"🥤 Beverages: {stats['total_beverages']}")
        print(f"🤖 Enhanced: {stats['enhanced_beverages']} ({stats['enhancement_rate']:.1f}%)")
        
        enhanced_count = get_enhanced_products_count()
        print(f"📊 Total enhanced products: {enhanced_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")