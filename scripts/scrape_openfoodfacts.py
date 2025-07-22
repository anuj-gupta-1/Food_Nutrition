# scrape_openfoodfacts.py
"""
Scrape 10 products each from 'Drinks' and 'Oil' categories from openfoodfacts.org.
- Collect all fields as per Product_Specs.docx
- Save raw JSON data in raw_data/<category>/
- Download all product images to images/<category>/
- Prepare a single CSV file in data/products.csv
- Modular functions for menu integration
"""

import os
import requests
import csv
import json
from datetime import datetime
from urllib.parse import urlparse

CATEGORIES = [
    ("carbonated-drinks", "Carbonated Drinks", "https://in.openfoodfacts.org/facets/categories/carbonated-drinks"),
    ("vegetable-oils", "Vegetable Oils", "https://in.openfoodfacts.org/facets/categories/vegetable-oils")
]
BASE_URL = "https://world.openfoodfacts.org/category/{}/{}.json"
PRODUCTS_PER_CATEGORY = 10

RAW_DATA_DIR = "raw_data"
IMAGES_DIR = "images"
DATA_DIR = "data"
CSV_FILE = os.path.join(DATA_DIR, "products.csv")

FIELDS = [
    "id", "product_name", "brand", "category", "category_url", "ingredients", "nutrition_json",
    "serving_size", "nutrition_per", "image_paths", "selected_image",
    "nutrition_extracted", "source", "scraped_at"
]

os.makedirs(RAW_DATA_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)


def fetch_products(category_tag, display_name, category_url):
    url = BASE_URL.format(category_tag, 1)
    resp = requests.get(url)
    data = resp.json()
    products = data.get("products", [])[:PRODUCTS_PER_CATEGORY]
    raw_dir = os.path.join(RAW_DATA_DIR, category_tag)
    os.makedirs(raw_dir, exist_ok=True)
    for i, prod in enumerate(products):
        with open(os.path.join(raw_dir, f"{prod.get('id', i)}.json"), "w", encoding="utf-8") as f:
            json.dump(prod, f, ensure_ascii=False, indent=2)
    return products


def download_images(product, category_tag):
    image_urls = []
    for key in ["image_front_url", "image_ingredients_url", "image_nutrition_url"]:
        url = product.get(key)
        if url:
            image_urls.append(url)
    saved_paths = []
    cat_dir = os.path.join(IMAGES_DIR, category_tag)
    os.makedirs(cat_dir, exist_ok=True)
    for url in image_urls:
        try:
            filename = os.path.basename(urlparse(url).path)
            save_path = os.path.join(cat_dir, filename)
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(r.content)
                saved_paths.append(save_path)
        except Exception as e:
            continue
    return saved_paths


def parse_product(prod, category_tag, display_name, category_url, image_paths):
    nutrition_json = prod.get("nutriments", {})
    return {
        "id": prod.get("id", ""),
        "product_name": prod.get("product_name", ""),
        "brand": prod.get("brands", ""),
        "category": display_name,
        "category_url": category_url,
        "ingredients": prod.get("ingredients_text", ""),
        "nutrition_json": json.dumps(nutrition_json, ensure_ascii=False),
        "serving_size": prod.get("serving_size", ""),
        "nutrition_per": prod.get("nutrition_data_per", ""),
        "image_paths": ",".join(image_paths),
        "selected_image": "",  # To be filled after manual selection
        "nutrition_extracted": "",  # To be filled after OCR
        "source": "openfoodfacts",
        "scraped_at": datetime.now().isoformat(sep=" ", timespec="seconds")
    }


def main():
    all_rows = []
    for category_tag, display_name, category_url in CATEGORIES:
        products = fetch_products(category_tag, display_name, category_url)
        for prod in products:
            image_paths = download_images(prod, category_tag)
            row = parse_product(prod, category_tag, display_name, category_url, image_paths)
            all_rows.append(row)
    # Write to CSV
    with open(CSV_FILE, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        for row in all_rows:
            writer.writerow(row)
    print(f"Scraping complete. Data saved to {CSV_FILE}")

if __name__ == "__main__":
    main() 