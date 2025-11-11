import json
import time
import os
import requests
from typing import Dict, List, Optional, Tuple
import pandas as pd
from datetime import datetime, timezone
import sqlite3
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class LLMNutritionService:
    """
    Fast, free LLM service for real-time nutrition data fetching
    Uses multiple free LLM providers with intelligent fallbacks
    """
    
    def __init__(self, cache_db_path: str = "llm_cache.db"):
        self.cache_db_path = cache_db_path
        self.init_cache_db()
        
        # Free LLM providers configuration
        self.providers = {
            "huggingface": {
                "url": "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                "headers": {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY', '')}"},
                "timeout": 10,
                "cost": 0.0,  # Free
                "rate_limit": 1000  # requests per hour
            },
            "ollama_local": {
                "url": "http://localhost:11434/api/generate",
                "headers": {"Content-Type": "application/json"},
                "timeout": 15,
                "cost": 0.0,  # Free local model
                "rate_limit": float('inf')
            },
            "groq": {
                "url": "https://api.groq.com/openai/v1/chat/completions",
                "headers": {
                    "Authorization": f"Bearer {os.getenv('GROQ_API_KEY', '')}",
                    "Content-Type": "application/json"
                },
                "timeout": 5,  # Very fast
                "cost": 0.0,  # Free tier
                "rate_limit": 30  # requests per minute
            }
        }
        
        # Performance tracking
        self.request_timestamps = {}
        self.provider_performance = {}
        self.target_response_time = 3.0  # seconds
        self.daily_cost = 0.0  # All providers are free, but keep for compatibility
        
    def init_cache_db(self):
        """Initialize SQLite cache database"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS nutrition_cache (
                product_hash TEXT PRIMARY KEY,
                product_name TEXT,
                brand TEXT,
                category TEXT,
                nutrition_data TEXT,
                confidence_score REAL,
                created_at TEXT,
                model_used TEXT
            )
        ''')
        conn.commit()
        conn.close()
        
    def get_product_hash(self, product_name: str, brand: str, category: str) -> str:
        """Generate unique hash for product identification"""
        key = f"{product_name.lower().strip()}|{brand.lower().strip()}|{category.lower().strip()}"
        return hashlib.md5(key.encode()).hexdigest()
    
    def check_cache(self, product_name: str, brand: str, category: str) -> Optional[Dict]:
        """Check if nutrition data exists in cache"""
        product_hash = self.get_product_hash(product_name, brand, category)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nutrition_data, confidence_score, created_at FROM nutrition_cache WHERE product_hash = ?",
            (product_hash,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "nutrition_data": json.loads(result[0]),
                "confidence_score": result[1],
                "created_at": result[2],
                "from_cache": True
            }
        return None
    
    def save_to_cache(self, product_name: str, brand: str, category: str, 
                     nutrition_data: Dict, confidence_score: float, model_used: str):
        """Save nutrition data to cache"""
        product_hash = self.get_product_hash(product_name, brand, category)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO nutrition_cache 
            (product_hash, product_name, brand, category, nutrition_data, confidence_score, created_at, model_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            product_hash, product_name, brand, category,
            json.dumps(nutrition_data), confidence_score,
            datetime.now(timezone.utc).isoformat(), model_used
        ))
        conn.commit()
        conn.close()
    
    def can_make_request(self, provider: str) -> Tuple[bool, str]:
        """Check if we can make a request to a specific provider"""
        now = time.time()
        
        if provider not in self.request_timestamps:
            self.request_timestamps[provider] = []
        
        # Clean old timestamps
        if provider == "groq":
            # Clean timestamps older than 1 minute
            self.request_timestamps[provider] = [
                ts for ts in self.request_timestamps[provider] if now - ts < 60
            ]
            if len(self.request_timestamps[provider]) >= self.providers[provider]["rate_limit"]:
                return False, f"Rate limit exceeded for {provider}"
        else:
            # Clean timestamps older than 1 hour for other providers
            self.request_timestamps[provider] = [
                ts for ts in self.request_timestamps[provider] if now - ts < 3600
            ]
            if len(self.request_timestamps[provider]) >= self.providers[provider]["rate_limit"]:
                return False, f"Rate limit exceeded for {provider}"
        
        return True, "OK"
    
    def get_nutrition_from_groq(self, prompt: str) -> Optional[Dict]:
        """Fast nutrition data from Groq (free tier, very fast)"""
        try:
            payload = {
                "model": "llama3-8b-8192",  # Fast, free model
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.providers["groq"]["url"],
                headers=self.providers["groq"]["headers"],
                json=payload,
                timeout=self.providers["groq"]["timeout"]
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                return self.parse_nutrition_response(content, "groq-llama3")
            
        except Exception as e:
            print(f"  -> Groq API error: {e}")
        return None
    
    def get_nutrition_from_huggingface(self, prompt: str) -> Optional[Dict]:
        """Nutrition data from HuggingFace free inference API"""
        try:
            # Use a nutrition-focused model if available
            payload = {"inputs": prompt}
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
                headers=self.providers["huggingface"]["headers"],
                json=payload,
                timeout=self.providers["huggingface"]["timeout"]
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    content = result[0].get("generated_text", "")
                    return self.parse_nutrition_response(content, "huggingface")
            
        except Exception as e:
            print(f"  -> HuggingFace API error: {e}")
        return None
    
    def get_nutrition_from_ollama(self, prompt: str) -> Optional[Dict]:
        """Local Ollama model (if running)"""
        try:
            payload = {
                "model": "llama2",  # or "mistral", "codellama"
                "prompt": prompt,
                "stream": False
            }
            
            response = requests.post(
                self.providers["ollama_local"]["url"],
                headers=self.providers["ollama_local"]["headers"],
                json=payload,
                timeout=self.providers["ollama_local"]["timeout"]
            )
            
            if response.status_code == 200:
                content = response.json().get("response", "")
                return self.parse_nutrition_response(content, "ollama-local")
            
        except Exception as e:
            print(f"  -> Ollama local error: {e}")
        return None
    
    def parse_nutrition_response(self, content: str, model_used: str) -> Optional[Dict]:
        """Parse field-value response format"""
        try:
            import re
            
            # Try field-value format first (new format)
            field_pattern = r'(\w+):\s*(.+?)(?=\n\w+:|$)'
            matches = re.findall(field_pattern, content, re.MULTILINE | re.DOTALL)
            
            if matches:
                # Parse field-value pairs
                response_data = {}
                for field, value in matches:
                    value = value.strip()
                    # Convert numeric values
                    if field.endswith('_per_100g') or field in ['confidence_score', 'servings_per_container']:
                        try:
                            if value.lower() == 'null':
                                response_data[field] = None
                            else:
                                response_data[field] = float(value) if '.' in value else int(value)
                        except:
                            response_data[field] = None
                    else:
                        response_data[field] = value if value.lower() != 'null' else None
                
                # Extract metadata
                confidence = response_data.pop("confidence_score", 0.7)
                data_source = response_data.pop("data_source", f"LLM-{model_used}")
                processing_notes = response_data.pop("processing_notes", "LLM enhanced")
                ingredients_list = response_data.pop("ingredients_list", "")
                serving_size = response_data.pop("serving_size", "")
                servings_per_container = response_data.pop("servings_per_container", None)
                
                # Remaining fields are nutrition data
                nutrition_data = response_data
                
            else:
                # Fallback to JSON format
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                    
                    # Extract based on format
                    if "energy_kcal_per_100g" in response_data:
                        confidence = response_data.pop("confidence_score", 0.7)
                        data_source = response_data.pop("data_source", f"LLM-{model_used}")
                        processing_notes = response_data.pop("processing_notes", "LLM enhanced")
                        ingredients_list = response_data.pop("ingredients_list", "")
                        serving_size = response_data.pop("serving_size", "")
                        servings_per_container = response_data.pop("servings_per_container", None)
                        nutrition_data = response_data
                    else:
                        # Legacy format
                        nutrition_data = response_data.copy()
                        confidence = nutrition_data.pop("confidence", 0.6)
                        ingredients_list = ""
                        serving_size = ""
                        servings_per_container = None
                        data_source = f"LLM-{model_used}"
                        processing_notes = "LLM enhanced"
                else:
                    return None
            
            # Validate required fields
            required_fields = [
                "energy_kcal_per_100g", "carbs_g_per_100g", "total_sugars_g_per_100g",
                "protein_g_per_100g", "fat_g_per_100g", "saturated_fat_g_per_100g", 
                "fiber_g_per_100g", "sodium_mg_per_100g", "salt_g_per_100g"
            ]
            
            for field in required_fields:
                if field not in nutrition_data:
                    # Try legacy field mapping
                    legacy_field = field.replace("_per_100g", "")
                    if legacy_field == "total_sugars_g":
                        legacy_field = "sugars_g"
                    
                    if legacy_field in nutrition_data:
                        nutrition_data[field] = nutrition_data[legacy_field]
                    else:
                        nutrition_data[field] = None
            
            return {
                "nutrition_data": nutrition_data,
                "confidence_score": confidence,
                "model_used": model_used,
                "data_source": data_source,
                "processing_notes": processing_notes,
                "ingredients_list": ingredients_list,
                "serving_size": serving_size,
                "servings_per_container": servings_per_container,
                "indian_market_specific": True,
                "from_cache": False
            }
            
        except Exception as e:
            print(f"  -> Failed to parse response from {model_used}: {e}")
            print(f"  -> Content: {content[:200]}...")
        return None
    
    def get_nutrition_from_llm(self, product_name: str, brand: str, category: str, 
                              size_value: float = None, size_unit: str = None) -> Optional[Dict]:
        """Fetch nutrition data using fastest available free LLM"""
        
        size_info = f" ({size_value} {size_unit})" if size_value and size_unit else ""
        
        # Simplified field-based prompt for Indian nutrition data
        prompt = f"""INDIAN FOOD NUTRITION DATA EXTRACTION

Product: {product_name}{size_info}
Brand: {brand}
Category: {category}
Size: {size_value} {size_unit}

TASK: Extract nutrition data for database integration. Provide field-value pairs for our Indian food database.

DATA SOURCES (priority order):
1. Official brand websites (Nestle India, Britannia, Parle, ITC, etc.)
2. FSSAI nutrition databases
3. Indian Food Composition Tables (NIN-ICMR)  
4. Verified Indian retailer nutrition labels
5. Indian market standards for {category}

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

INDIAN MARKET FOCUS:
- Use Indian formulations (not international variants)
- Consider Indian ingredients (mustard oil, jaggery, Indian spices)
- Apply Indian serving size standards
- Ensure FSSAI compliance
- Use "null" for uncertain values

CONFIDENCE SCORING:
0.9-1.0: Official brand/FSSAI data
0.8-0.9: Government nutrition database  
0.7-0.8: Verified retailer label
0.6-0.7: Industry standard for Indian {category}

Return ONLY the field-value pairs as shown above. No additional text."""
        
        # Try providers in order of speed (fastest first)
        providers_by_speed = ["groq", "ollama_local", "huggingface"]
        
        for provider in providers_by_speed:
            can_request, reason = self.can_make_request(provider)
            if not can_request:
                continue
            
            start_time = time.time()
            result = None
            
            try:
                if provider == "groq":
                    result = self.get_nutrition_from_groq(prompt)
                elif provider == "ollama_local":
                    result = self.get_nutrition_from_ollama(prompt)
                elif provider == "huggingface":
                    result = self.get_nutrition_from_huggingface(prompt)
                
                # Track request
                self.request_timestamps[provider].append(time.time())
                
                if result:
                    response_time = time.time() - start_time
                    print(f"  -> Got nutrition data from {provider} in {response_time:.2f}s")
                    
                    # Track performance
                    if provider not in self.provider_performance:
                        self.provider_performance[provider] = []
                    self.provider_performance[provider].append(response_time)
                    
                    return result
                    
            except Exception as e:
                print(f"  -> {provider} failed: {e}")
                continue
        
        print(f"  -> All LLM providers failed for {product_name}")
        return None
    
    def get_nutrition_data(self, product_name: str, brand: str, category: str,
                          size_value: float = None, size_unit: str = None,
                          force_refresh: bool = False) -> Optional[Dict]:
        """
        Get nutrition data with cache-first approach
        """
        # Check cache first (unless force refresh)
        if not force_refresh:
            cached_result = self.check_cache(product_name, brand, category)
            if cached_result:
                print(f"  -> Using cached nutrition data for {product_name}")
                return cached_result
        
        # Fetch from LLM
        print(f"  -> Fetching nutrition data from LLM for {product_name}")
        llm_result = self.get_nutrition_from_llm(product_name, brand, category, size_value, size_unit)
        
        if llm_result:
            # Save to cache
            self.save_to_cache(
                product_name, brand, category,
                llm_result["nutrition_data"],
                llm_result["confidence_score"],
                llm_result["model_used"]
            )
            
        return llm_result
    
    def process_products_batch(self, products_df: pd.DataFrame, 
                              batch_size: int = 10, 
                              min_confidence: float = 0.3) -> pd.DataFrame:
        """
        Process multiple products in batches with smart filtering
        """
        print(f"Processing {len(products_df)} products for nutrition enhancement...")
        
        # Filter products that need nutrition data
        needs_nutrition = products_df[
            (products_df['nutrition_data'].str.contains('"energy_kcal": null', na=True)) |
            (products_df['nutrition_data'] == '') |
            (products_df['nutrition_data'].isna())
        ].copy()
        
        print(f"  -> {len(needs_nutrition)} products need nutrition data")
        
        if needs_nutrition.empty:
            return products_df
        
        # Process in batches
        processed_count = 0
        enhanced_count = 0
        
        for i in range(0, len(needs_nutrition), batch_size):
            batch = needs_nutrition.iloc[i:i+batch_size]
            print(f"\nProcessing batch {i//batch_size + 1} ({len(batch)} products)...")
            
            for idx, row in batch.iterrows():
                result = self.get_nutrition_data(
                    row['product_name'], 
                    row['brand'], 
                    row['category'],
                    row.get('size_value'),
                    row.get('size_unit')
                )
                
                if result and result.get('confidence_score', 0) >= min_confidence:
                    # Update the main dataframe
                    products_df.at[idx, 'nutrition_data'] = json.dumps(result['nutrition_data'])
                    products_df.at[idx, 'llm_fallback_used'] = True
                    products_df.at[idx, 'data_quality_score'] = min(
                        products_df.at[idx, 'data_quality_score'] + 15,  # Boost for nutrition data
                        100
                    )
                    enhanced_count += 1
                
                processed_count += 1
                
                # Add delay between requests to be respectful
                time.sleep(1)
            
            print(f"  -> Batch complete. Enhanced {enhanced_count}/{processed_count} products so far")
            
            # Check if we should continue
            can_continue, reason = self.can_make_request()
            if not can_continue:
                print(f"  -> Stopping batch processing: {reason}")
                break
        
        print(f"\nLLM Enhancement complete:")
        print(f"  -> Processed: {processed_count} products")
        print(f"  -> Enhanced: {enhanced_count} products")
        print(f"  -> Daily cost: ${self.daily_cost:.3f}")
        
        return products_df
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM nutrition_cache")
        total_cached = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence_score) FROM nutrition_cache")
        avg_confidence = cursor.fetchone()[0] or 0
        
        cursor.execute("SELECT model_used, COUNT(*) FROM nutrition_cache GROUP BY model_used")
        model_stats = dict(cursor.fetchall())
        
        conn.close()
        
        return {
            "total_cached": total_cached,
            "average_confidence": avg_confidence,
            "model_breakdown": model_stats,
            "daily_cost": self.daily_cost,
            "requests_this_minute": len(self.request_timestamps)
        }


def main():
    """Example usage"""
    # Initialize service
    service = LLMNutritionService()
    
    # Test with a single product
    result = service.get_nutrition_data(
        "Amul Butter 500g",
        "Amul", 
        "dairy",
        500,
        "g"
    )
    
    if result:
        print("Nutrition data:", json.dumps(result['nutrition_data'], indent=2))
        print("Confidence:", result['confidence_score'])
    
    # Print cache stats
    stats = service.get_cache_stats()
    print("Cache stats:", json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()