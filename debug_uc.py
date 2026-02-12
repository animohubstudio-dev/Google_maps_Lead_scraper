import undetected_chromedriver as uc
try:
    options = uc.ChromeOptions()
    # options.add_argument('--headless')
    driver = uc.Chrome(options=options)
    driver.get('https://google.com')
    print("UC Works!")
    driver.quit()
except Exception as e:
    print(f"UC Failed: {e}")
