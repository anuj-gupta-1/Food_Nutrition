# This script uses Selenium to scrape dynamically loaded FMCG product data.
# It simulates a real browser to bypass anti-bot measures and JavaScript-dependent content.

# --- INSTALLATION ---
# You need to install the required libraries and a web browser driver.
# 1. Install Selenium and a driver manager (recommended):
#    pip install selenium webdriver-manager
# 2. Make sure you have a Chrome browser installed on your system.

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

def scrape_fmcg_products(url, category_override=None):
    """
    Scrapes product data from a given URL using a real browser instance.

    Args:
        url (str): The URL of the webpage to scrape.
    """
    driver = None
    try:
        # Use Service and Options for compatibility with latest Selenium
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        options = Options()
        # options.add_argument("--headless")  # Uncomment to run headless
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        # Wait for the product list to be visible. This is crucial for dynamic websites.
        # It ensures that all JavaScript has loaded and rendered the content we need.
        # The selector here corresponds to the product list container.
        wait = WebDriverWait(driver, 20)
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.wizzy-result-product')))
        except TimeoutException:
            print("Timeout waiting for 'li.wizzy-result-product'. Printing current URL and partial page source for debugging:")
            print("Current URL:", driver.current_url)
            with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Saved page source to debug_page_source.html. Please inspect this file to update your selectors.")
            raise
        # Print all li classes for debugging
        lis = driver.find_elements(By.TAG_NAME, 'li')
        print("Sample of li classes on page:")
        for d in lis[:20]:
            cls = d.get_attribute('class')
            if cls:
                print(cls)

        # Scroll down to load all products, as many sites use infinite scrolling
        # This is a simple loop that scrolls to the bottom and waits for new content to load
        scroll_count = 0
        while scroll_count < 3: # Adjust this number based on how many scrolls are needed
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2) # Wait for the new content to load
            scroll_count += 1

        # Now, select the product elements after the page is fully loaded and scrolled
        product_elements = driver.find_elements(By.CSS_SELECTOR, 'li.wizzy-result-product')

        print(f"Found {len(product_elements)} product containers.")

        if not product_elements:
            print("No products found using the specified selectors. Please check the website's HTML.")
            return []

        products = []

        # Set category from override if provided, else default to 'diary'
        category = category_override if category_override else 'diary'
        # Extract subcategory from left side menu panel (if present)
        try:
            subcat_elem = driver.find_element(By.CSS_SELECTOR, 'ul.wizzy-facet-list li.active, ul.wizzy-facet-list li.selected, ul.wizzy-facet-list li[aria-checked="true"]')
            subcategory = subcat_elem.text.strip()
        except Exception:
            subcategory = ''

        # Extract known brands from the facet list (if present)
        brand_elements = driver.find_elements(By.CSS_SELECTOR, 'li.wizzy-facet-list-item[data-term]')
        known_brands = set()
        for el in brand_elements:
            brand = el.get_attribute('data-term')
            if brand:
                known_brands.add(brand.strip())

        import datetime
        run_timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for product in product_elements:
            try:
                # Use the 'title' attribute of the product card for the product name (more reliable)
                product_name = product.get_attribute('title')
                if not product_name or not product_name.strip():
                    try:
                        h3_heading = product.find_element(By.CSS_SELECTOR, 'h3.card__heading')
                        a_tags = h3_heading.find_elements(By.TAG_NAME, 'a')
                        # Find the first <a> with non-empty text
                        product_name = next((a.text.strip() for a in a_tags if a.text.strip()), 'Name not found')
                    except Exception:
                        product_name = 'Name not found'
                # Try to get sale price first, else regular price
                try:
                    price_element = product.find_element(By.CSS_SELECTOR, 'span.price-item.price-item--sale')
                except NoSuchElementException:
                    price_element = product.find_element(By.CSS_SELECTOR, 'span.price-item.price-item--regular')

                product_price = price_element.text.strip() if price_element else 'Price not found'

                # Extract brand from product_name using known brands
                brand = ''
                if product_name and product_name != 'Name not found' and known_brands:
                    for b in known_brands:
                        if product_name.lower().startswith(b.lower()):
                            brand = b
                            break
                # Fallback: try to get brand from data-product-name or title attribute if not matched
                if not brand:
                    brand = product.get_attribute('data-product-name')
                if not brand:
                    brand = ''

                # Extract size value and unit from product name (e.g., '400 Gm', '1 L', etc.)
                import re
                size_value = ''
                size_unit = ''
                size_match = re.search(r'(\d+(?:\.\d+)?)\s*(gm|ml|kg|l|L|Gm|g|mL|Kg|pcs|Pack|pack|Piece|piece|Tablet|tablet|Capsule|capsule)', product_name)
                if size_match:
                    size_value = size_match.group(1)
                    size_unit = size_match.group(2)

                products.append({
                    'name': product_name,
                    'price': product_price,
                    'brand': brand,
                    'size_value': size_value,
                    'size_unit': size_unit,
                    'category': category,
                    'subcategory': subcategory,
                    'url': url,
                    'timestamp': run_timestamp
                })
            except NoSuchElementException:
                print("Skipping a product due to missing name or price element.")
                continue

        return products

    except TimeoutException:
        print("Timed out waiting for the page to load. The website might have changed or is taking too long to respond.")
        return []
    except WebDriverException as e:
        print(f"A WebDriver error occurred: {e}")
        print("Please ensure you have Chrome installed and the correct driver is being used.")
        return []
    finally:
        if driver:
            driver.quit() # Always close the browser

def save_to_csv(data, filename='fmcg_products.csv'):
    """
    Saves the scraped data to a CSV file.
    """
    if not data:
        # --- NEW: Made the "no data" message more explicit. ---
        print("No data was scraped to save.")
        return

    import os
    # Update fieldnames to include new fields
    fieldnames = ['name', 'price', 'brand', 'size_value', 'size_unit', 'category', 'subcategory', 'url', 'timestamp']
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Write header only if file does not exist
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerows(data)
    print(f"Successfully appended {len(data)} products to {filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        TARGET_URL = sys.argv[1]
        CATEGORY = sys.argv[2] if len(sys.argv) > 2 else None
        CSV_FILENAME = sys.argv[3] if len(sys.argv) > 3 else 'fmcg_products.csv'
    else:
        print("Usage: python fmcg_scraper_selenium.py <URL> [CATEGORY] [CSV_FILENAME]")
        sys.exit(1)

    scraped_data = scrape_fmcg_products(TARGET_URL, CATEGORY)
    save_to_csv(scraped_data, filename=CSV_FILENAME)
