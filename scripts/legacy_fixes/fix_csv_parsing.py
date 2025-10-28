#!/usr/bin/env python3
"""
Fix CSV Parsing Issues
Create a robust CSV reader for the products file
"""

import pandas as pd
import json
import csv
from io import StringIO

def safe_csv_read(file_path):
    """Safely read the products CSV with proper handling of complex data"""
    
    print("🔧 FIXING CSV PARSING ISSUES")
    print("=" * 50)
    
    try:
        # Method 1: Try with quoting
        print("📝 Trying Method 1: Standard pandas with quoting...")
        df = pd.read_csv(file_path, sep='||', engine='python', quoting=csv.QUOTE_NONE, encoding='utf-8')
        print(f"✅ Success! Loaded {len(df)} rows with {len(df.columns)} columns")
        return df, "method1"
    except Exception as e:
        print(f"❌ Method 1 failed: {e}")
    
    try:
        # Method 2: Manual parsing
        print("📝 Trying Method 2: Manual line parsing...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Parse header
        header = lines[0].strip().split('||')
        print(f"📋 Header has {len(header)} columns: {header[:5]}...")
        
        # Parse data lines
        data_rows = []
        problem_lines = []
        
        for i, line in enumerate(lines[1:], 2):
            fields = line.strip().split('||')
            
            if len(fields) == len(header):
                data_rows.append(fields)
            else:
                problem_lines.append((i, len(fields), line[:100]))
                
                # Try to fix by padding or truncating
                if len(fields) < len(header):
                    # Pad with empty strings
                    fields.extend([''] * (len(header) - len(fields)))
                else:
                    # Truncate extra fields
                    fields = fields[:len(header)]
                
                data_rows.append(fields)
        
        if problem_lines:
            print(f"⚠️  Fixed {len(problem_lines)} problematic lines")
            for line_num, count, preview in problem_lines[:3]:
                print(f"   Line {line_num}: {count} fields - {preview}...")
        
        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=header)
        print(f"✅ Success! Loaded {len(df)} rows with {len(df.columns)} columns")
        return df, "method2"
        
    except Exception as e:
        print(f"❌ Method 2 failed: {e}")
    
    try:
        # Method 3: Use different separator detection
        print("📝 Trying Method 3: Auto-detect separator...")
        
        # Read first few lines to detect pattern
        with open(file_path, 'r', encoding='utf-8') as f:
            sample = f.read(10000)
        
        # Count different separators
        separators = ['||', '|', '\t', ',', ';']
        sep_counts = {sep: sample.count(sep) for sep in separators}
        best_sep = max(sep_counts, key=sep_counts.get)
        
        print(f"🔍 Detected separator: '{best_sep}' (count: {sep_counts[best_sep]})")
        
        df = pd.read_csv(file_path, sep=best_sep, engine='python', encoding='utf-8', on_bad_lines='skip')
        print(f"✅ Success! Loaded {len(df)} rows with {len(df.columns)} columns")
        return df, "method3"
        
    except Exception as e:
        print(f"❌ Method 3 failed: {e}")
    
    print("❌ All methods failed!")
    return None, "failed"

def test_csv_operations(df):
    """Test basic operations on the loaded DataFrame"""
    
    print("\n🧪 TESTING CSV OPERATIONS")
    print("=" * 30)
    
    try:
        # Basic info
        print(f"📊 Shape: {df.shape}")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Check for beverages
        if 'category' in df.columns:
            beverages = df[df['category'] == 'beverage']
            print(f"🥤 Beverages: {len(beverages)}")
        
        # Check for enhanced products
        if 'llm_fallback_used' in df.columns:
            enhanced = df[df['llm_fallback_used'] == True]
            print(f"🤖 Enhanced: {len(enhanced)}")
        
        # Sample data
        print(f"\n📝 Sample product:")
        if len(df) > 0:
            sample = df.iloc[0]
            print(f"   Name: {sample.get('product_name', 'N/A')}")
            print(f"   Brand: {sample.get('brand', 'N/A')}")
            print(f"   Category: {sample.get('category', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Testing failed: {e}")
        return False

if __name__ == "__main__":
    # Test the CSV reading
    df, method = safe_csv_read('data/products.csv')
    
    if df is not None:
        success = test_csv_operations(df)
        
        if success:
            print(f"\n✅ CSV parsing fixed using {method}")
            print("🎯 Ready to continue with LLM enhancement!")
        else:
            print(f"\n⚠️  CSV loaded but operations failed")
    else:
        print(f"\n❌ Could not fix CSV parsing issues")