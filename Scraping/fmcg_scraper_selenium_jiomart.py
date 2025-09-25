# Jiomart FMCG Product Scraper
# This script uses Selenium to scrape product data from Jiomart category pages.
# Requirements: pip install selenium webdriver-manager

import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager

def scrape_jiomart_products(url, category=None, subcategory=None):
    driver = None
    import re
    try:
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        options = Options()
        # options.add_argument('--headless')  # Uncomment to run headless
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)

        wait = WebDriverWait(driver, 40)
        # If pincode popup appears, enter 560006
        try:
            # Wait for pincode input or skip if not present
            pincode_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#pincode')))
            pincode_input.clear()
            pincode_input.send_keys('560006')
            # Click submit or check button
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], button.btn-pincode-check')
            submit_btn.click()
            time.sleep(2)
        except Exception:
            pass  # No pincode popup

        # Wait for page to load (product cards or fallback)
        time.sleep(5)
        # Save page source for analysis
        with open('jiomart_debug_page_source.html', 'w', encoding='utf-8') as f:
            f.write(driver.page_source)
        print('Saved page source to jiomart_debug_page_source.html for analysis.')

        # Scroll to the bottom to load all products (infinite scroll)
        last_count = 0
        scroll_pause = 4  # seconds
        max_scrolls = 200  # increased safety limit
        for _ in range(max_scrolls):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause)
            products = driver.find_elements(By.CSS_SELECTOR, 'li.ais-InfiniteHits-item')
            if len(products) == last_count:
                break  # No new products loaded
            last_count = len(products)
        # After scrolling, get all product cards
        products = driver.find_elements(By.CSS_SELECTOR, 'li.ais-InfiniteHits-item')
        import datetime
        data = []
        timestamp = datetime.datetime.now().isoformat()
        for product in products:
            try:
                name = product.find_element(By.CSS_SELECTOR, '.plp-card-details-name').text.strip()
            except Exception:
                name = ''
            try:
                brand = product.find_element(By.CSS_SELECTOR, '.gtmEvents').get_attribute('data-manu')
            except Exception:
                brand = ''
            try:
                price = product.find_element(By.CSS_SELECTOR, '.plp-card-details-price span.jm-heading-xxs').text.strip()
            except Exception:
                price = ''
            # Extract size and split into value/unit
            try:
                size = product.find_element(By.CSS_SELECTOR, '.variant_value').text.strip()
            except Exception:
                size = ''
            size_value, size_unit = '', ''
            size_source = size if size else name
            if size_source:
                # Try to match patterns like '3 x 50g', '200 g', '1.5 L', 'Pack of 3', etc.
                match = re.search(r"([\d\.]+)\s*[xX]\s*([\d\.]+)\s*([a-zA-Z]+)", size_source)
                if match:
                    size_value = f"{match.group(1)}x{match.group(2)}"
                    size_unit = match.group(3)
                else:
                    match = re.search(r"([\d\.]+)\s*([a-zA-Z]+)", size_source)
                    if match:
                        size_value, size_unit = match.group(1), match.group(2)
                    else:
                        match = re.search(r"Pack of (\d+)", size_source, re.IGNORECASE)
                        if match:
                            size_value, size_unit = match.group(1), 'pack'
                        else:
                            size_value, size_unit = '', ''
            data.append({
                'name': name,
                'price': price,
                'brand': brand,
                'size_value': size_value,
                'size_unit': size_unit,
                'category': category if category else '',
                'subcategory': subcategory if subcategory else '',
                'url': url,
                'timestamp': timestamp
            })
        print(f"Successfully scraped {len(data)} products from Jiomart.")
        return data
    except TimeoutException:
        print("Timed out waiting for the page to load. The website might have changed or is taking too long to respond.")
        return []
    except WebDriverException as e:
        print(f"A WebDriver error occurred: {e}")
        print("Please ensure you have Chrome installed and the correct driver is being used.")
        return []
    finally:
        if driver:
            driver.quit()

def save_to_csv(data, filename='fmcg_products_jiomart.csv'):
    if not data:
        print("No data was scraped to save.")
        return
    import os
    fieldnames = ['name', 'price', 'brand', 'size_value', 'size_unit', 'category', 'subcategory', 'url', 'timestamp']
    file_exists = os.path.isfile(filename)
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        if not file_exists or os.stat(filename).st_size == 0:
            writer.writeheader()
        writer.writerows(data)
    print(f"Successfully appended {len(data)} products to {filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        TARGET_URL = sys.argv[1]
        CATEGORY = sys.argv[2] if len(sys.argv) > 2 else None
        SUBCATEGORY = sys.argv[3] if len(sys.argv) > 3 else None
        CSV_FILENAME = sys.argv[4] if len(sys.argv) > 4 else 'fmcg_products_jiomart.csv'
    else:
        print("Usage: python fmcg_scraper_selenium_jiomart.py <URL> [CATEGORY] [CSV_FILENAME]")
        sys.exit(1)
    scraped_data = scrape_jiomart_products(TARGET_URL, CATEGORY, SUBCATEGORY)
    save_to_csv(scraped_data, filename=CSV_FILENAME)
