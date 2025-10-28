"""
Real-time Nutrition API Server
Fast Flask API for fetching nutrition data on-demand for Android app
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from llm_nutrition_service import LLMNutritionService
import threading
from concurrent.futures import ThreadPoolExecutor
import sqlite3
from datetime import datetime, timezone

app = Flask(__name__)
CORS(app)

# Initialize LLM service
llm_service = LLMNutritionService()

# Thread pool for concurrent requests
executor = ThreadPoolExecutor(max_workers=5)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cache_stats": llm_service.get_cache_stats()
    })

@app.route('/nutrition', methods=['POST'])
def get_nutrition():
    """
    Get nutrition data for a product
    Expected JSON payload:
    {
        "product_name": "Amul Butter",
        "brand": "Amul",
        "category": "dairy",
        "size_value": 500,
        "size_unit": "g"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        required_fields = ["product_name", "brand", "category"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        start_time = time.time()
        
        # Get nutrition data (cache-first, then LLM)
        result = llm_service.get_nutrition_data(
            product_name=data["product_name"],
            brand=data["brand"],
            category=data["category"],
            size_value=data.get("size_value"),
            size_unit=data.get("size_unit")
        )
        
        response_time = time.time() - start_time
        
        if result:
            return jsonify({
                "success": True,
                "nutrition_data": result["nutrition_data"],
                "confidence_score": result["confidence_score"],
                "model_used": result["model_used"],
                "from_cache": result["from_cache"],
                "response_time_seconds": round(response_time, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        else:
            return jsonify({
                "success": False,
                "error": "Could not fetch nutrition data",
                "response_time_seconds": round(response_time, 2),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }), 404
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/nutrition/batch', methods=['POST'])
def get_nutrition_batch():
    """
    Get nutrition data for multiple products
    Expected JSON payload:
    {
        "products": [
            {"product_name": "...", "brand": "...", "category": "..."},
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        products = data.get("products", [])
        
        if not products:
            return jsonify({"error": "No products provided"}), 400
        
        if len(products) > 10:
            return jsonify({"error": "Maximum 10 products per batch"}), 400
        
        start_time = time.time()
        results = []
        
        # Process products concurrently
        def fetch_nutrition(product):
            return llm_service.get_nutrition_data(
                product_name=product["product_name"],
                brand=product["brand"],
                category=product["category"],
                size_value=product.get("size_value"),
                size_unit=product.get("size_unit")
            )
        
        # Use thread pool for concurrent processing
        futures = {executor.submit(fetch_nutrition, product): product for product in products}
        
        for future in futures:
            product = futures[future]
            try:
                result = future.result(timeout=10)  # 10 second timeout per product
                if result:
                    results.append({
                        "product": product,
                        "nutrition_data": result["nutrition_data"],
                        "confidence_score": result["confidence_score"],
                        "model_used": result["model_used"],
                        "from_cache": result["from_cache"]
                    })
                else:
                    results.append({
                        "product": product,
                        "error": "Could not fetch nutrition data"
                    })
            except Exception as e:
                results.append({
                    "product": product,
                    "error": str(e)
                })
        
        response_time = time.time() - start_time
        
        return jsonify({
            "success": True,
            "results": results,
            "total_products": len(products),
            "successful_fetches": len([r for r in results if "nutrition_data" in r]),
            "response_time_seconds": round(response_time, 2),
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/cache/stats', methods=['GET'])
def cache_stats():
    """Get cache statistics"""
    try:
        stats = llm_service.get_cache_stats()
        return jsonify({
            "success": True,
            "cache_stats": stats,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

@app.route('/cache/clear', methods=['POST'])
def clear_cache():
    """Clear nutrition cache (admin endpoint)"""
    try:
        # Clear the cache database
        conn = sqlite3.connect(llm_service.cache_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nutrition_cache")
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Cleared {deleted_count} cached entries",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }), 500

if __name__ == '__main__':
    print("🚀 Starting Real-time Nutrition API Server...")
    print("📊 Cache stats:", llm_service.get_cache_stats())
    print("🔗 Available endpoints:")
    print("   POST /nutrition - Get nutrition for single product")
    print("   POST /nutrition/batch - Get nutrition for multiple products")
    print("   GET /cache/stats - Cache statistics")
    print("   GET /health - Health check")
    
    # Run in development mode
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)