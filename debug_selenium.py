from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

try:
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.get('https://google.com')
    print("Selenium Works!")
    time.sleep(2)
    driver.quit()
except Exception as e:
    print(f"Selenium Failed: {e}")
