#!/usr/bin/env python3
"""
Improved LLM Classification Service
Addresses all feedback points with better prompts and validation
"""

import requests
import json
import time
from typing import Dict, Optional


class ImprovedLLMClassificationService:
    """Improved Local Llama-based classification service"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "phi:2.7b"  # Use fastest model
        self.timeout = 60
        
        # Store category mappings in "memory" (class attributes)
        self.category_subcategories = {
            'essentials': [
                'flour', 'salt', 'sugar', 'dry-fruits-nuts', 'oil', 
                'rice', 'pulses', 'masala', 'wheat-soya'
            ],
            'snacks': [
                'breakfast', 'chips', 'namkeen', 'biscuit', 'bakery'
            ],
            'flavourings': [
                'pickles', 'chutney', 'sauce'
            ],
            'beverage': [
                'tea', 'coffee', 'juice', 'carbonated', 'energy-drinks', 
                'health-drinks', 'syrup', 'other-beverages'
            ],
            'spread': [
                'sauce-ketchup-butter', 'jam-honey', 'other-spreads'
            ],
            'noodles_pasta': [
                'noodles', 'pasta', 'instant-noodles'
            ],
            'chocolate': [
                'chocolate', 'candy'
            ],
            'ready_to_eat': [
                'ready-to-eat', 'instant-meals'
            ],
            'baby': [
                'baby-food', 'baby-snacks'
            ],
            'dairy': [
                'milk', 'curd', 'cheese', 'paneer', 'butter', 'yogurt', 'ghee'
            ],
            'bakery': [
                'cake', 'bread', 'pastry', 'cookies'
            ]
        }
        
        # Auto-accept threshold
        self.auto_accept_threshold = 0.8
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                print(f"✅ Ollama connected. Available models: {available_models}")
                
                # Use fastest model
                for model in available_models:
                    if 'phi' in model:
                        self.model = model
                        break
                
                print(f"✅ Using model: {self.model}")
                return True
            return False
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            return False
    
    def classify_product(self, product_name: str, current_category: str, 
                        current_subcategory: str, brand: str) -> Dict:
        """
        Classify product using local Llama model with improved prompts
        """
        
        # Get valid subcategories from memory
        valid_subcategories = self.category_subcategories.get(current_category.lower(), [])
        subcategories_str = ', '.join(valid_subcategories)
        
        # Create improved prompt with specific examples
        prompt = f"""You are an expert at Indian food product classification. Analyze this product carefully.

PRODUCT TO ANALYZE:
Name: {product_name}
Brand: {brand}
Category: {current_category}
Current Subcategory: {current_subcategory}

TASK 1: SUBCATEGORY CLASSIFICATION
Choose the MOST APPROPRIATE subcategory from: {subcategories_str}

TASK 2: CLEAN NAME EXTRACTION
Create a clean product name following these rules:
- Keep CORE product identity (the main product type)
- Keep important descriptors (Organic, Healthy, flavors like Elaichi/Mango)
- Keep brand name if it's part of product identity
- Remove size info (kg, ml, gm), pack details (Pack of X), marketing fluff
- Remove parentheses content and pipe-separated details

EXAMPLES:
"FreshoCartz Afghani Black Raisins 1kg | Kali Dakh" → "Afghani Black Raisins"
"FARMER'S FEAST Chia Seeds 1kg - Healthy Raw Seeds" → "Farmer's Feast Chia Seeds"
"Soni Farms - Organic Sonamasuri Rice - 1 Kg" → "Organic Sonamasuri Rice"
"Gone Mad Gang of 5 Choco Sticks - Crispy (312g)" → "Gang of 5 Choco Sticks"
"Hajmola Candy Elaichi Flavor 100g" → "Hajmola Candy Elaichi"
"B&B Organics Thooyamalli Rice (3 Kg), Premium" → "Thooyamalli Rice"

CRITICAL: The clean name MUST relate to the original product. Don't create unrelated names.

RESPOND IN EXACTLY THIS FORMAT:
new_subcategory: [choose from the list]
clean_product_name: [extracted clean name]
confidence_score: [0.0 to 1.0]
reasoning: [why this classification and name]"""

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,  # Lower temperature for more consistent results
                    "top_p": 0.8,
                    "max_tokens": 300
                }
            }
            
            print(f"  -> Calling Llama model: {self.model}")
            
            response = requests.post(
                self.ollama_url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("response", "")
                
                print(f"  -> Got response from Llama")
                
                # Parse and validate the response
                parsed = self.parse_and_validate_response(
                    llm_response, 
                    valid_subcategories,
                    current_subcategory,
                    product_name,
                    brand
                )
                
                return parsed
            else:
                print(f"  -> Llama API error: {response.status_code}")
                return self.create_fallback_result(current_subcategory, product_name, "api_error")
                
        except Exception as e:
            print(f"  -> Llama classification error: {e}")
            return self.create_fallback_result(current_subcategory, product_name, f"error: {str(e)}")
    
    def parse_and_validate_response(self, response: str, valid_subcategories: list,
                                   fallback_subcategory: str, original_name: str, brand: str) -> Dict:
        """Parse Llama response with validation"""
        
        try:
            import re
            
            new_subcategory = fallback_subcategory
            clean_name = ""
            confidence = 0.5
            reasoning = ""
            
            # Extract new_subcategory
            subcat_match = re.search(r'new_subcategory:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
            if subcat_match:
                extracted_subcat = subcat_match.group(1).strip()
                # Validate against valid subcategories
                if extracted_subcat in valid_subcategories:
                    new_subcategory = extracted_subcat
                    confidence = 0.8
                else:
                    # Try partial matching
                    for valid_sub in valid_subcategories:
                        if valid_sub.lower() in extracted_subcat.lower():
                            new_subcategory = valid_sub
                            confidence = 0.7
                            break
            
            # Extract clean_product_name
            name_match = re.search(r'clean_product_name:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
            if name_match:
                extracted_name = name_match.group(1).strip()
                extracted_name = extracted_name.strip('"\'[]')
                
                # Validate the clean name
                if self.validate_clean_name(extracted_name, original_name, brand):
                    clean_name = extracted_name
                    confidence = max(confidence, 0.75)
                else:
                    # Try to create a better name
                    clean_name = self.create_fallback_clean_name(original_name, brand)
                    confidence = max(confidence, 0.6)
            else:
                # No name extracted, create fallback
                clean_name = self.create_fallback_clean_name(original_name, brand)
                confidence = max(confidence, 0.5)
            
            # Extract confidence_score
            conf_match = re.search(r'confidence_score:\s*([\d.]+)', response, re.IGNORECASE)
            if conf_match:
                try:
                    llm_confidence = float(conf_match.group(1))
                    confidence = (confidence + llm_confidence) / 2
                except:
                    pass
            
            # Extract reasoning
            reason_match = re.search(r'reasoning:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
            if reason_match:
                reasoning = reason_match.group(1).strip()
            
            # Determine processing flags
            auto_accept = confidence >= self.auto_accept_threshold
            needs_review = confidence < 0.7
            
            return {
                'new_subcategory': new_subcategory,
                'clean_product_name': clean_name,
                'confidence_score': round(confidence, 2),
                'classification_method': 'llama_improved',
                'needs_manual_review': needs_review,
                'auto_accept': auto_accept,
                'processed_for_cleanup': True,
                'processing_notes': reasoning if reasoning else 'Improved Llama classification',
                'llm_response': response[:200] + '...' if len(response) > 200 else response
            }
            
        except Exception as e:
            print(f"  -> Error parsing Llama response: {e}")
            return self.create_fallback_result(fallback_subcategory, original_name, f"parse_error: {str(e)}")
    
    def validate_clean_name(self, clean_name: str, original_name: str, brand: str) -> bool:
        """Validate that the clean name makes sense for the original product"""
        
        import re
        
        if not clean_name or len(clean_name) < 3:
            return False
        
        # Check if clean name has some relation to original
        original_lower = original_name.lower()
        clean_lower = clean_name.lower()
        
        # Extract key words from both names
        original_words = set(re.findall(r'\b\w{3,}\b', original_lower))
        clean_words = set(re.findall(r'\b\w{3,}\b', clean_lower))
        
        # Should have at least some word overlap (excluding common words)
        common_words = {'the', 'and', 'for', 'with', 'pack', 'combo', 'premium', 'fresh'}
        original_words -= common_words
        clean_words -= common_words
        
        overlap = len(original_words & clean_words)
        return overlap >= 1  # At least one meaningful word should match
    
    def create_fallback_clean_name(self, original_name: str, brand: str) -> str:
        """Create a reasonable clean name as fallback using rule-based approach"""
        
        import re
        
        # Start with original name
        clean = original_name
        
        # Remove brand from beginning if present
        if brand and len(brand) > 2:
            brand_pattern = re.escape(brand)
            clean = re.sub(f'^{brand_pattern}\\s*', '', clean, flags=re.IGNORECASE)
        
        # Remove size patterns
        clean = re.sub(r'\b\d+(?:\.\d+)?\s*(?:kg|g|gm|gram|ml|l|litre|liter|oz|lb)\b', '', clean, flags=re.IGNORECASE)
        
        # Remove pack patterns
        clean = re.sub(r'\bpack\s+of\s+\d+\b', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\bcombo\s*pack\b', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\bcombo\b', '', clean, flags=re.IGNORECASE)
        clean = re.sub(r'\d+\s*x\s*\d+', '', clean, flags=re.IGNORECASE)
        
        # Remove parenthetical content
        clean = re.sub(r'\([^)]*\)', '', clean)
        
        # Remove pipe-separated content (everything after first |)
        if '|' in clean:
            clean = clean.split('|')[0]
        
        # Remove marketing fluff
        marketing_words = [
            'premium', 'fresh', 'pure', '100%', 'certified', 'natural',
            'rich', 'source', 'calcium', 'iron', 'protein', 'fiber',
            'low', 'calories', 'fat free', 'non-gmo', 'traditional',
            'handpounded', 'unpolished', 'chemicals', 'pesticides',
            'mason jar', 'glass bottle'
        ]
        
        for word in marketing_words:
            clean = re.sub(f'\\b{re.escape(word)}\\b', '', clean, flags=re.IGNORECASE)
        
        # Clean up extra spaces, punctuation, and separators
        clean = re.sub(r'[,\-\|]+', ' ', clean)
        clean = re.sub(r'\s+', ' ', clean)
        clean = clean.strip(' ,-|')
        
        # If brand was removed, add it back for important products
        if brand and len(brand) > 2 and len(clean) < 20:
            # Add brand back for short names
            clean = f"{brand} {clean}".strip()
        
        # Limit length and clean up
        if len(clean) > 60:
            words = clean.split()
            clean = ' '.join(words[:8])  # Take first 8 words
        
        # Final cleanup
        clean = clean.strip()
        
        return clean if clean and len(clean) > 2 else original_name[:50]
    
    def create_fallback_result(self, subcategory: str, name: str, error: str) -> Dict:
        """Create fallback result when classification fails"""
        return {
            'new_subcategory': subcategory,
            'clean_product_name': name,
            'confidence_score': 0.3,
            'classification_method': 'fallback',
            'needs_manual_review': True,
            'auto_accept': False,
            'processed_for_cleanup': False,
            'processing_notes': f'Classification failed: {error}',
            'llm_response': ''
        }


def test_improved_service():
    """Test the improved service with problematic examples"""
    
    service = ImprovedLLMClassificationService()
    
    if not service.test_connection():
        print("❌ Cannot connect to Ollama")
        return False
    
    # Test cases based on your feedback
    test_cases = [
        {
            'name': "FARMER'S FEAST Chia Seeds 1kg - Healthy Raw Seeds | Clean Chia Seeds for Eating",
            'category': 'essentials',
            'subcategory': 'dry-fruits-nuts',
            'brand': "Farmer'S Feast",
            'expected_clean': "Farmer's Feast Chia Seeds"
        },
        {
            'name': "Soni Farms - Organic Sonamasuri Rice - 1 Kg | Sonamasoori Rice | 100% Pure",
            'category': 'essentials', 
            'subcategory': 'rice',
            'brand': 'Soni Farms',
            'expected_clean': "Organic Sonamasuri Rice"
        },
        {
            'name': "FreshoCartz Afghani Black Raisins 1kg | Kali Dakh | Kali Kishmish",
            'category': 'essentials',
            'subcategory': 'dry-fruits-nuts', 
            'brand': 'Freshocartz',
            'expected_clean': "Afghani Black Raisins"
        }
    ]
    
    print("\n🧪 TESTING IMPROVED SERVICE:")
    print("=" * 60)
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name'][:50]}...")
        
        result = service.classify_product(
            test['name'],
            test['category'],
            test['subcategory'], 
            test['brand']
        )
        
        print(f"Expected Clean Name: {test['expected_clean']}")
        print(f"Got Clean Name: {result['clean_product_name']}")
        print(f"Confidence: {result['confidence_score']}")
        print(f"Auto Accept: {result['auto_accept']}")
        print(f"Processed: {result['processed_for_cleanup']}")
        print("-" * 40)
    
    return True


if __name__ == "__main__":
    test_improved_service()