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

        # Wait for the product list to be visible. Update selector to match Frugivore's actual product card structure.
        wait = WebDriverWait(driver, 40)
        product_elements = []
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.product-listing div.product-card')))
        except TimeoutException:
            print("Timeout waiting for 'div.product-listing div.product-card'. Printing current URL and partial page source for debugging:")
            print("Current URL:", driver.current_url)
            with open('debug_page_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            print("Saved page source to debug_page_source.html. Please inspect this file to update your selectors.")
            try:
                print('Page title:', driver.title)
            except Exception:
                pass
        else:
            # Now, select the product elements after the page is fully loaded and scrolled
            product_elements = driver.find_elements(By.CSS_SELECTOR, 'div.product-listing div.product-card')

        if not product_elements:
            print("No products found using the specified selectors. Please check the website's HTML.")
            try:
                print('Page title:', driver.title)
            except Exception:
                pass
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
                # Brand: Try to extract from a <p class="greyText"> or similar
                try:
                    brand = product.find_element(By.CSS_SELECTOR, 'p.greyText').text.strip()
                except Exception:
                    brand = ''

                # Name: Try to extract from <p class="fruitname"> or similar
                try:
                    name = product.find_element(By.CSS_SELECTOR, 'p.fruitname').text.strip()
                except Exception:
                    name = ''

                # Size: Try to extract from <span class="weight"> or similar
                try:
                    size_label = product.find_element(By.CSS_SELECTOR, 'span.weight').text.strip()
                except Exception:
                    size_label = ''

                # Price: Try to extract from <div class="base-fruit-table"> or <div class="fruit-table">, look for Rs and numbers
                try:
                    price_elem = product.find_element(By.CSS_SELECTOR, 'div.base-fruit-table, div.fruit-table')
                    import re
                    price_match = re.search(r'Rs\s*([\d,.]+)', price_elem.text)
                    price = price_match.group(1).replace(',', '') if price_match else ''
                except Exception:
                    price = ''

                # Extract size value and unit from size_label
                import re
                size_value = ''
                size_unit = ''
                size_match = re.search(r'(\d+(?:\.\d+)?)\s*(gm|ml|kg|l|L|Gm|g|mL|Kg|pcs|Pack|pack|Piece|piece|Tablet|tablet|Capsule|capsule)', size_label)
                if size_match:
                    size_value = size_match.group(1)
                    size_unit = size_match.group(2)

                products.append({
                    'name': name,
                    'price': price,
                    'brand': brand,
                    'size_value': size_value,
                    'size_unit': size_unit,
                    'category': category,
                    'subcategory': subcategory,
                    'url': url,
                    'timestamp': run_timestamp
                })
            except Exception as e:
                print(f"Skipping a product due to error: {e}")
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

def save_to_csv(data, filename='fmcg_products_frugivore.csv'):
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
        CSV_FILENAME = sys.argv[3] if len(sys.argv) > 3 else 'fmcg_products_frugivore.csv'
    else:
        print("Usage: python fmcg_scraper_selenium_frugivore.py <URL> [CATEGORY] [CSV_FILENAME]")
        sys.exit(1)

    scraped_data = scrape_fmcg_products(TARGET_URL, CATEGORY)
    save_to_csv(scraped_data, filename=CSV_FILENAME)
