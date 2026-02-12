# scraper/maps_scraper.py
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import config

class MapsScraper:
    def __init__(self):
        options = webdriver.ChromeOptions()
        # Stealth options
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Headless mode for deployment
        if os.environ.get("HEADLESS") == "true":
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--window-size=1280,720")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--blink-settings=imagesEnabled=false") # Disable images for speed/memory
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        self.wait = WebDriverWait(self.driver, 20)

    def search(self, query):
        self.driver.get('https://www.google.com/maps?hl=en') # Force English to standardize IDs/Labels if possible
        time.sleep(5)
        
        selectors = [
            (By.ID, "searchboxinput"),
            (By.NAME, "q"),
            (By.CSS_SELECTOR, "input#searchboxinput"),
            (By.XPATH, "//input[@id='searchboxinput']"),
            (By.CSS_SELECTOR, "input[aria-label='Search Google Maps']")
        ]
        
        search_box_input = None
        for by, value in selectors:
            try:
                element = self.driver.find_element(by, value)
                if element.is_displayed():
                    search_box_input = element
                    print(f"Found search box using {by}={value}")
                    break
            except:
                continue
                
        if not search_box_input:
            print("Could not find search box. Saving debug info to debug_screenshot.png and debug_page.html")
            try:
                self.driver.save_screenshot("debug_screenshot.png")
                with open("debug_page.html", "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
            except Exception as e:
                print(f"Failed to save debug info: {e}")
            return

        try:
            search_box_input.clear()
            search_box_input.send_keys(query)
            # small delay
            time.sleep(1)
            search_box_input.send_keys(Keys.ENTER)
            print(f"Searching for: {query}")
        except Exception as e:
            print(f"Error interacting with search box: {e}")
            return
            
        time.sleep(random.uniform(3, 5))

    def get_leads(self):
        """
        Scrolls the results list and collects details for up to MAX_LEADS_PER_RUN.
        """
        leads = []
        processed_names = set()
        
        try:
            # Locate the scrollable feed
            # Usually strict role="feed"
            feed = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="feed"]')))
        except:
            print("Could not find results feed.")
            return leads

        # Scroll loop
        while len(leads) < config.MAX_LEADS_PER_RUN:
            # Find all current items
            items = self.driver.find_elements(By.CSS_SELECTOR, 'div[role="feed"] > div > div[role="article"]')
            
            # Filter for unprocessed items
            new_items = []
            for item in items:
                try:
                    aria_label = item.get_attribute("aria-label")
                    if aria_label and aria_label not in processed_names:
                        new_items.append(item)
                except:
                    continue

            if not new_items:
                # Scroll down
                self.driver.execute_script("arguments[0].scrollBy(0, 1000);", feed)
                time.sleep(random.uniform(2, 4))
                
                # Check if end of list
                # (Simple check: if no new items found after scroll, maybe end)
                # But let's verify if scrollHeight increased or textual "You've reached the end"
                continue
            
            # Process new items (click and extract)
            for item in new_items:
                if len(leads) >= config.MAX_LEADS_PER_RUN:
                    break
                    
                try:
                    name = item.get_attribute("aria-label")
                    if not name: 
                        continue
                        
                    print(f"Processing: {name}")
                    item.click()
                    time.sleep(random.uniform(config.ACTION_DELAY_MIN, config.ACTION_DELAY_MAX))
                    
                    details = self.extract_details()
                    details["Business Name"] = name # Ensure name is captured
                    
                    leads.append(details)
                    processed_names.add(name)
                    
                except Exception as e:
                    print(f"Error clicking item: {e}")
            
            # Scroll again after processing this batch, just in case
            self.driver.execute_script("arguments[0].scrollBy(0, 1000);", feed)
            time.sleep(2)

        return leads

    def extract_details(self):
        details = {
            "Business Name": "",
            "Rating": "",
            "Reviews": "",
            "Address": "",
            "Website": "",
            "Phone": "",
            "Category": "",
            "Socials": {} 
        }
        
        def safe_get_text(selector):
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, selector)
                return el.text
            except:
                return ""

        def safe_get_attr(selector, attr):
            try:
                el = self.driver.find_element(By.CSS_SELECTOR, selector)
                return el.get_attribute(attr)
            except:
                return ""

        # Website
        # Look for the globe icon or "Website" text. 
        # Often has data-item-id="authority"
        website_url = safe_get_attr('a[data-item-id="authority"]', 'href')
        if not website_url:
             # Try searching by aria-label "Website: "
             website_url = safe_get_attr('a[aria-label^="Website:"]', 'href')
        details["Website"] = website_url

        # Phone
        phone = safe_get_text('button[data-item-id^="phone"]')
        if not phone:
             phone = safe_get_attr('button[data-item-id^="phone"]', 'aria-label')
        
        if phone:
            phone = phone.replace("Phone: ", "")
            # Remove non-ascii and extra whitespace
            phone = "".join([c for c in phone if c.isascii()]).strip()
        else:
            phone = ""
            
        details["Phone"] = phone

        # Address
        address = safe_get_text('button[data-item-id="address"]')
        if not address:
             address = safe_get_attr('button[data-item-id="address"]', 'aria-label')
        details["Address"] = address.replace("Address: ", "") if address else ""

        # Rating & Reviews
        # Often in a span like "4.5 stars 100 Reviews"
        try:
             # Find the main rating div
             # It's usually near the top of the pane.
             # Use xpath to find text that looks like rating
             rating_el = self.driver.find_element(By.XPATH, '//span[@role="img" and contains(@aria-label, "stars")]')
             rating_text = rating_el.get_attribute("aria-label")
             if rating_text:
                 parts = rating_text.split()
                 details["Rating"] = parts[0]
                 # Reviews often follows
        except:
            pass
            
        return details

    def close(self):
        try:
            self.driver.quit()
        except:
            pass
