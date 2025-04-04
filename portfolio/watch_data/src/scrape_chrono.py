from selenium import webdriver
from selenium_stealth import stealth
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

# Set up Selenium with Chrome
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)

# Initialize the WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Apply stealth settings
stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )

# Create an empty list to store watch data
watch_data = []

try:
    for i in range(1, 7600):  # Adjust the range as needed for pagination
        url = f"https://www.chrono24.com/watches/mens-watches--62-{i}.htm?keyword=mens-watches&keywordId=62&resultview=list&showpage={i}"

        # Load the page
        driver.get(url)
        time.sleep(0.5)  # Wait for content to load

        # Wait for the content to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "js-article-item-container"))
        )

        # Get the page source after JavaScript execution
        html_content = driver.page_source

        # Parse the HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        watches_div = soup.find("div", id="wt-watches")

        if not watches_div:
            print(f"No watches found on page {i}")
            continue

        watches = watches_div.find_all("div", class_="js-article-item-container article-item-container wt-search-result article-image-carousel")

        # Process each watch listing
        for watch in watches:
            try:
                # Extract watch details
                watch_data_item = {}

                # Get watch model and brand
                model_div = watch.find("div", class_="text-sm text-sm-xlg text-bold text-ellipsis")
                if model_div:
                    watch_data_item["model"] = model_div.text.strip()

                # Get watch details
                details_div = watch.find("div", class_="text-sm text-sm-lg text-ellipsis p-r-5")
                if details_div:
                    watch_data_item["details"] = details_div.text.strip()

                # Extract price
                price_div = watch.find("div", class_="text-md text-sm-xlg text-bold")
                if price_div:
                    price_text = price_div.text.strip()
                    # Extract numeric value and currency
                    currency_symbol = price_div.find("span", class_="currency").text.strip() if price_div.find("span", class_="currency") else ""
                    price_num = re.sub(r'[^\d.]', '', price_text)
                    watch_data_item["price"] = price_num
                    watch_data_item["currency"] = currency_symbol

                # Extract shipping cost if available
                shipping_div = watch.find("div", class_="text-muted text-sm")
                if shipping_div:
                    shipping_text = shipping_div.text.strip()
                    shipping_cost = re.search(r'\$\s*(\d+(?:,\d+)*(?:\.\d+)?)', shipping_text)
                    if shipping_cost:
                        watch_data_item["shipping_cost"] = shipping_cost.group(1)
                    else:
                        watch_data_item["shipping_cost"] = "0"

                # Extract specifications from rows
                spec_rows = watch.find_all("div", class_="w-50 row row-direct")
                for row in spec_rows:
                    label_div = row.find_all("div", class_="col-xs-12")
                    if len(label_div) >= 2:
                        label = label_div[0].text.strip().rstrip(':').lower().replace(' ', '_')
                        value = label_div[1].find("strong").text.strip() if label_div[1].find("strong") else label_div[1].text.strip()
                        watch_data_item[label] = value

                # Extract more specifications from rows
                more_spec_rows = watch.find_all("div", class_="w-50 row row-direct d-none d-md-block")
                for row in more_spec_rows:
                    label_div = row.find_all("div", class_="col-xs-12")
                    if len(label_div) >= 2:
                        label = label_div[0].text.strip().rstrip(':').lower().replace(' ', '_')
                        value = label_div[1].find("strong").text.strip() if label_div[1].find("strong") else label_div[1].text.strip()
                        watch_data_item[label] = value

                # Extract watch link
                link_element = watch.find("a", class_="js-article-item article-item list-item rcard")
                if link_element and link_element.has_attr('href'):
                    watch_data_item["product_url"] = "https://www.chrono24.com" + link_element['href']

                # Extract location
                location_button = watch.find("button", {"data-title": True, "data-content": True})
                if location_button:
                    location_content = location_button.get("data-content", "")
                    location_match = re.search(r'from\s+([^,]+),\s+(.+)', location_content)
                    if location_match:
                        watch_data_item["dealer_city"] = location_match.group(1)
                        watch_data_item["dealer_country"] = location_match.group(2)

                    location_span = location_button.find("span", class_="text-sm text-uppercase")
                    if location_span:
                        watch_data_item["country_code"] = location_span.text.strip()

                # Add to our list of watches
                watch_data.append(watch_data_item)

            except Exception as e:
                print(f"Error processing watch: {e}")
                continue

        print(f"Processed page {i}, found {len(watches)} watches")

        # Sleep to avoid overwhelming the server
        time.sleep(0.1)

    # Create a DataFrame from the collected data
    df = pd.DataFrame(watch_data)

    # Save to CSV
    df.to_csv("../resources/watches_data_new.csv", index=False)
    print(f"Successfully scraped {len(watch_data)} watches and saved to watches_data_new.csv")

except Exception as e:
    print(f"Error during scraping: {e}")

    # Create a DataFrame from the collected data
    df = pd.DataFrame(watch_data)

    # Save to CSV
    df.to_csv("../resources/watches_data_new.csv", index=False)

finally:
    # Always close the driver
    driver.quit()


