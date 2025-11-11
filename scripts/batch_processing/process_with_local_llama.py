#!/usr/bin/env python3
"""
Process batch with local Llama via Ollama
"""

import pandas as pd
import requests
import json
import sys
import os
from datetime import datetime
import re

# Add parent directories to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

class LocalLlamaProcessor:
    def __init__(self, model="llama3.2:3b"):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = model
        self.processed_count = 0
        self.failed_count = 0
        
    def check_ollama_status(self):
        """Check if Ollama is running and model is available"""
        try:
            # Check if Ollama is running
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                print(f"✅ Ollama is running")
                print(f"📋 Available models: {available_models}")
                
                # Check if our model is available
                model_available = any(self.model in model for model in available_models)
                if model_available:
                    print(f"✅ Model {self.model} is available")
                    return True
                else:
                    print(f"❌ Model {self.model} not found")
                    print(f"💡 Run: ollama pull {self.model}")
                    return False
            else:
                print(f"❌ Ollama not responding")
                return False
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            print(f"💡 Make sure Ollama is running: ollama serve")
            return False
    
    def create_nutrition_prompt(self, product_name, brand, category, subcategory, size_value, size_unit, price, source):
        """Create nutrition extraction prompt for local Llama"""
        
        prompt = f"""INDIAN FOOD NUTRITION DATA EXTRACTION

Product: {product_name}
Brand: {brand}
Category: {category}
Subcategory: {subcategory}
Size: {size_value} {size_unit}
Price: ₹{price}
Source: {source}

TASK: Extract nutrition data for this Indian food product. Focus on Indian market formulations and FSSAI standards.

DATA SOURCES (use in priority order):
1. Official brand websites (Nestle India, Britannia, Parle, ITC, etc.)
2. FSSAI nutrition databases
3. Indian Food Composition Tables (NIN-ICMR)
4. Verified Indian retailer nutrition labels
5. Typical Indian market standards for {category}

REQUIRED FIELDS - Provide as field-value pairs:

NUTRITION (per 100g/100ml):
energy_kcal_per_100g: <number>
carbs_g_per_100g: <number>
total_sugars_g_per_100g: <number>
protein_g_per_100g: <number>
fat_g_per_100g: <number>
saturated_fat_g_per_100g: <number>
fiber_g_per_100g: <number>
sodium_mg_per_100g: <number>
salt_g_per_100g: <number>

PRODUCT INFO:
ingredients_list: ingredient1, ingredient2, ingredient3
serving_size: 30g
servings_per_container: 7

QUALITY:
confidence_score: 0.85
data_source: Brand official website
processing_notes: Verified from Indian nutrition label

GUIDELINES:
- Use Indian formulations (not international variants)
- Consider Indian ingredients (mustard oil, jaggery, Indian spices)
- Apply Indian serving size standards
- Use realistic values for Indian {category} products
- Use "null" for uncertain values
- Confidence: 0.9+ (official), 0.8+ (govt DB), 0.7+ (retailer), 0.6+ (standard)

Return ONLY the field-value pairs as shown above. No additional text or explanations."""

        return prompt
    
    def query_ollama(self, prompt):
        """Query local Ollama with prompt"""
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_predict": 500
                }
            }
            
            print(f"  🤖 Querying {self.model}...")
            response = requests.post(
                self.ollama_url,
                json=payload,
                timeout=60  # Increased timeout for local processing
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                print(f"  ❌ Ollama error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"  ❌ Ollama query failed: {e}")
            return None
    
    def parse_llama_response(self, response_text):
        """Parse Llama response to extract field-value pairs"""
        try:
            if not response_text:
                return None
            
            # Clean the response text
            response_text = response_text.strip()
            
            # Extract field-value pairs using line-by-line parsing
            result = {}
            lines = response_text.split('\n')
            
            for line in lines:
                line = line.strip()
                if ':' in line and not line.startswith('#') and not line.startswith('//'):
                    try:
                        field, value = line.split(':', 1)
                        field = field.strip()
                        value = value.strip()
                        
                        # Skip empty or invalid fields
                        if not field or not value:
                            continue
                        
                        # Convert numeric values
                        if field.endswith('_per_100g') or field in ['confidence_score', 'servings_per_container']:
                            try:
                                if value.lower() in ['null', 'none', 'n/a', '']:
                                    result[field] = None
                                else:
                                    # Extract first number from the value
                                    number_match = re.search(r'[\d.]+', value)
                                    if number_match:
                                        num_str = number_match.group()
                                        result[field] = float(num_str) if '.' in num_str else int(float(num_str))
                                    else:
                                        result[field] = None
                            except:
                                result[field] = None
                        else:
                            # Text fields
                            result[field] = value if value.lower() not in ['null', 'none', 'n/a', ''] else None
                    
                    except ValueError:
                        # Skip malformed lines
                        continue
            
            if not result:
                print(f"  ⚠️ No valid field-value pairs found")
                return None
            
            # Validate we have some nutrition data
            nutrition_fields = [f for f in result.keys() if f.endswith('_per_100g')]
            if len(nutrition_fields) < 3:
                print(f"  ⚠️ Insufficient nutrition data: {len(nutrition_fields)} fields")
                return None
            
            print(f"  📊 Extracted {len(result)} fields, {len(nutrition_fields)} nutrition values")
            return result
            
        except Exception as e:
            print(f"  ❌ Parse error: {e}")
            return None
    
    def process_product(self, row):
        """Process a single product"""
        try:
            product_name = row['product_name']
            brand = row['brand']
            category = row['category']
            subcategory = row.get('subcategory', '')
            size_value = row.get('size_value', '')
            size_unit = row.get('size_unit', '')
            price = row.get('price', '')
            source = row.get('source', '')
            
            print(f"🔍 Processing: {product_name[:50]}...")
            
            # Create prompt
            prompt = self.create_nutrition_prompt(
                product_name, brand, category, subcategory, 
                size_value, size_unit, price, source
            )
            
            # Query Ollama
            response = self.query_ollama(prompt)
            if not response:
                self.failed_count += 1
                return None
            
            # Parse response
            nutrition_data = self.parse_llama_response(response)
            if nutrition_data:
                self.processed_count += 1
                print(f"  ✅ Success! Confidence: {nutrition_data.get('confidence_score', 'N/A')}")
                return nutrition_data
            else:
                self.failed_count += 1
                print(f"  ❌ Failed to extract valid data")
                return None
                
        except Exception as e:
            print(f"  ❌ Error processing {row.get('product_name', 'unknown')}: {e}")
            self.failed_count += 1
            return None
    
    def process_batch(self, input_file, max_products=None):
        """Process batch file with local Llama"""
        
        if not os.path.exists(input_file):
            print(f"❌ Input file not found: {input_file}")
            return False
        
        # Check Ollama status
        if not self.check_ollama_status():
            return False
        
        # Load batch
        df = pd.read_csv(input_file)
        print(f"\n📥 Loaded {len(df)} products from batch")
        
        if max_products:
            df = df.head(max_products)
            print(f"🔢 Processing first {len(df)} products")
        
        # Show category breakdown
        if 'category' in df.columns:
            category_counts = df['category'].value_counts()
            print(f"\n📋 Categories to process:")
            for cat, count in category_counts.items():
                print(f"   {cat}: {count} products")
        
        # Process each product
        enhanced_products = []
        for idx, row in df.iterrows():
            print(f"\n[{idx+1}/{len(df)}]", end=" ")
            
            # Create enhanced row with original data
            enhanced_row = row.to_dict()
            
            # Get nutrition data
            nutrition_data = self.process_product(row)
            if nutrition_data:
                # Add nutrition fields to row
                enhanced_row.update(nutrition_data)
            
            enhanced_products.append(enhanced_row)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        output_file = f"llm_batches/output/llama_enhanced_{len(df)}products_{timestamp}.csv"
        
        enhanced_df = pd.DataFrame(enhanced_products)
        enhanced_df.to_csv(output_file, index=False)
        
        print(f"\n🎉 LOCAL LLAMA PROCESSING COMPLETE!")
        print(f"📤 Results saved to: {output_file}")
        print(f"✅ Processed: {self.processed_count}")
        print(f"❌ Failed: {self.failed_count}")
        print(f"📊 Success rate: {(self.processed_count/(self.processed_count+self.failed_count)*100):.1f}%")
        
        return output_file

def main():
    """
    Main function - ESTABLISHED PROCESS
    
    CRITICAL: Update input_file to match the latest batch created by create_next_batch.py
    
    ESTABLISHED BEHAVIOR:
    - Local Llama returns confidence_score as N/A, null, or empty - THIS IS NORMAL
    - Products with good nutrition data but N/A confidence are VALID
    - Success rate typically 97-100% with occasional timeout failures
    - Output goes to llm_batches/output/llama_enhanced_[N]products_[TIMESTAMP].csv
    """
    processor = LocalLlamaProcessor()
    
    # IMPORTANT: Update this filename to match the latest batch from create_next_batch.py
    input_file = "llm_batches/input/input_all_categories_50products_20251105_1326.csv"
    
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        print(f"💡 Create a batch first: python scripts/batch_processing/create_next_batch.py 10")
        return
    
    print(f"🚀 Starting Local Llama Processing")
    print(f"📥 Input: {input_file}")
    print(f"🤖 Model: llama3.2:3b")
    
    processor.process_batch(input_file, max_products=50)

if __name__ == "__main__":
    main()