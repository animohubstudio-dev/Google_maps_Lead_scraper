# config.py

# Search settings
SEARCH_QUERIES = [
    "Dentist near {city}",
    "Dental clinic near {city}",
    "Cosmetic dentist near {city}"
]

# Filtering settings
SKIP_KEYWORDS = [
    "Aspen Dental",
    "Smile Brands",
    "Pacific Dental Services",
    "Heartland Dental",
    "Western Dental",
    "Affordable Dentures & Implants",
    "Great Expressions",
    "Dental Care Alliance",
    "Smile medical" 
]

# Scraping settings
MAX_LEADS_PER_RUN = 100
SCROLL_PAUSE_TIME = 2  # Seconds
ACTION_DELAY_MIN = 2
ACTION_DELAY_MAX = 5

# Proxy settings (Placeholder)
PROXY_LIST = [
    # "http://user:pass@ip:port",
]

# Output settings
OUTPUT_DIR = "output"
CSV_FILENAME = "leads.csv"
