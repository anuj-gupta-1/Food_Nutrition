#!/usr/bin/env python3
"""
LLM Classification Service using Local Ollama/Llama
Dedicated service for product classification and name cleanup
"""

import requests
import json
import time
from typing import Dict, Optional


class LLMClassificationService:
    """Local Llama-based classification service"""
    
    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "qwen2.5:7b-instruct"  # Use Qwen 2.5 7B Instruct model
        self.timeout = 120  # Increased timeout to 120 seconds
    
    def test_connection(self) -> bool:
        """Test if Ollama is running and accessible"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                available_models = [model['name'] for model in models]
                print(f"✅ Ollama connected. Available models: {available_models}")
                
                # Override with Qwen 2.5 Instruct model
                self.model = "qwen2.5:7b-instruct"  # Force use of Qwen 2.5 7B Instruct model
                print(f"✅ Using model: {self.model}")
                
                return True
            return False
        except Exception as e:
            print(f"❌ Ollama connection failed: {e}")
            return False
    
    def classify_product(self, product_name: str, current_category: str, 
                        current_subcategory: str, brand: str, 
                        valid_subcategories: list) -> Dict:
        """
        Classify product using local Llama model
        """
        
        subcategories_str = ', '.join(valid_subcategories)
        
        prompt = f"""Clean Indian food product names by removing unnecessary words.

INPUT:
Name: {product_name}
Brand: {brand}

TASK 1: Pick subcategory from: {subcategories_str}

TASK 2: Clean the name - BE AGGRESSIVE, keep it SHORT:

DELETE EVERYTHING:
- Brand "{brand}"
- ALL sizes/weights/quantities
- ALL marketing: Premium, Healthy, Rich, Traditional, Delicious, Perfect, Classic, Finest, Special, Natural, Pure, Strong, Aromatic, Energy-Rich, High Protein, Ideal, Benefits, Support, Manage, Free (except Gluten Free, Sugar Free)
- ALL usage descriptions: "for cooking", "for fasting", "for diabetes", "for immune support"
- ALL symbols except hyphen
- Parentheses

KEEP ONLY:
- Product type (Macaroni, Fusilli, Rice, Oil, Flour, Tea, Chutney)
- Specific variety (Double Diamond, Seeraga Samba, Kuttu, Kagazi Badam)
- Indian/regional terms (Rajasthani, Gujrati, Pudina, Desi Khand, Kolhu, Kacchi Ghani)
- Essential descriptors: Organic, Brown, White, Cold Pressed, Gluten Free, Sugar Free
- Combo format: "Pack of [Item1] and [Item2]"

EXAMPLES:
"Sambhojanam Sugar free Diet flour wheat free for Manage Diabetes Gluten free" → "Sugar Free Gluten Free Diet Flour"
"Momsy Premium Gems Munchies Chocolate Truffles Balls" → "Gems Munchies Chocolate Truffles"
"First Flavour Tea Premium Assam Black CTC Strong Aromatic Rich" → "Assam Black CTC Tea"
"Trushita Cold Pressed Mustard Oil Virgin Pure for Healthy Cooking" → "Cold Pressed Mustard Oil"
"Amwel Kuttu Atta Buckwheat Flour Navratri Special Fasting" → "Kuttu Atta"
"Sresth Ora Cold-pressed Olive Oil Organic pure for immune support" → "Organic Cold Pressed Olive Oil"
"Nutzy Kagazi Badam Almond Inshell Thin Shell Energy-Rich High Protein" → "Kagazi Badam - Almond Inshell"

RULE: Maximum 5 words in output. Be ruthless.

OUTPUT:
new_subcategory: [answer]
clean_product_name: [answer]
confidence_score: [0.0-1.0]
reasoning: [brief]"""

        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "max_tokens": 200
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
                
                # Parse the response
                parsed = self.parse_llm_response(
                    llm_response, 
                    valid_subcategories,
                    current_subcategory,
                    product_name
                )
                
                return parsed
            else:
                print(f"  -> Llama API error: {response.status_code}")
                return self.create_fallback_result(current_subcategory, product_name, "api_error")
                
        except Exception as e:
            print(f"  -> Llama classification error: {e}")
            return self.create_fallback_result(current_subcategory, product_name, f"error: {str(e)}")
    
    def parse_llm_response(self, response: str, valid_subcategories: list,
                          fallback_subcategory: str, fallback_name: str) -> Dict:
        """Parse Llama response and extract classification data"""
        
        try:
            import re
            
            new_subcategory = fallback_subcategory
            clean_name = fallback_name
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
                clean_name = name_match.group(1).strip()
                clean_name = clean_name.strip('"\'[]')
                if clean_name and len(clean_name) > 3:  # Valid name
                    confidence = max(confidence, 0.7)
            
            # Extract confidence_score
            conf_match = re.search(r'confidence_score:\s*([\d.]+)', response, re.IGNORECASE)
            if conf_match:
                try:
                    llm_confidence = float(conf_match.group(1))
                    confidence = (confidence + llm_confidence) / 2  # Average with our confidence
                except:
                    pass
            
            # Extract reasoning
            reason_match = re.search(r'reasoning:\s*(.+?)(?=\n|$)', response, re.IGNORECASE)
            if reason_match:
                reasoning = reason_match.group(1).strip()
            
            return {
                'new_subcategory': new_subcategory,
                'clean_product_name': clean_name,
                'confidence_score': round(confidence, 2),
                'classification_method': 'llama_local',
                'needs_manual_review': confidence < 0.7,
                'processing_notes': reasoning if reasoning else 'Llama classification',
                'llm_response': response[:200] + '...' if len(response) > 200 else response
            }
            
        except Exception as e:
            print(f"  -> Error parsing Llama response: {e}")
            return self.create_fallback_result(fallback_subcategory, fallback_name, f"parse_error: {str(e)}")
    
    def create_fallback_result(self, subcategory: str, name: str, error: str) -> Dict:
        """Create fallback result when classification fails"""
        return {
            'new_subcategory': subcategory,
            'clean_product_name': name,
            'confidence_score': 0.3,
            'classification_method': 'fallback',
            'needs_manual_review': True,
            'processing_notes': f'Classification failed: {error}',
            'llm_response': ''
        }


def test_classification_service():
    """Test the classification service"""
    
    service = LLMClassificationService()
    
    if not service.test_connection():
        print("❌ Cannot connect to Ollama. Make sure it's running with: ollama serve")
        return False
    
    # Test with a sample product
    test_result = service.classify_product(
        product_name="Dhampur Green Organic Brown Sugar 800g, 100% Certified Organic Natural Brown Demerara Sugar",
        current_category="essentials",
        current_subcategory="salt-sugar",
        brand="Dhampur Green",
        valid_subcategories=['flour', 'salt', 'sugar', 'dry-fruits-nuts', 'oil', 'rice', 'pulses', 'masala', 'wheat-soya']
    )
    
    print("\n🧪 TEST RESULT:")
    print(f"New Subcategory: {test_result['new_subcategory']}")
    print(f"Clean Name: {test_result['clean_product_name']}")
    print(f"Confidence: {test_result['confidence_score']}")
    print(f"Method: {test_result['classification_method']}")
    print(f"Notes: {test_result['processing_notes']}")
    
    return test_result['confidence_score'] > 0.5


if __name__ == "__main__":
    test_classification_service()