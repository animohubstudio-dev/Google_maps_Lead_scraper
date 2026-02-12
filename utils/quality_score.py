# utils/quality_score.py
import requests
from bs4 import BeautifulSoup
import re

def check_ssl(url):
    return url.startswith("https")

def check_mobile_friendly(soup):
    viewport = soup.find("meta", attrs={"name": "viewport"})
    return viewport is not None

def check_modern_tech(soup):
    # Heuristic: Check for modern frameworks or meta generators
    html_str = str(soup).lower()
    modern_keywords = [
        "react", "next.js", "gatsby", "vue", "nuxt", "tailwind", "bootstrap",
        "wix", "squarespace", "webflow", "shopify"
    ]
    for keyword in modern_keywords:
        if keyword in html_str:
            return True
    return False

def check_copyright_year(soup):
    html_str = str(soup).lower()
    # Simple regex to find "copyright 20XX" or "© 20XX"
    matches = re.findall(r"(?:copyright|©)\s*(?:20\d{2})", html_str)
    if matches:
        # Get the max year found
        years = []
        for match in matches:
            try:
                year = int(re.search(r"20\d{2}", match).group(0))
                years.append(year)
            except:
                pass
        if years:
            return max(years)
    return None

def calculate_quality_score(url):
    """
    Analyzes the website and returns a Quality Score.
    10 = No website / Connection Error
    8 = Outdated / Not mobile friendly / HTTP only
    5 = Average
    0 = Modern / High Quality
    """
    if not url:
        return 10
    
    try:
        # Add timeout to avoid hanging
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            return 10
    except Exception:
        return 10

    soup = BeautifulSoup(response.text, "lxml")
    
    score = 5 # Default average
    
    # Check 1: SSL
    if not check_ssl(response.url):
        return 8 # Not secure = Outdated
        
    # Check 2: Mobile Friendly (Viewport)
    if not check_mobile_friendly(soup):
        return 8 # Not mobile friendly
        
    # Check 3: Modern Tech
    if check_modern_tech(soup):
        # If it's built with modern tech, it's likely a 0 (Modern/High Quality)
        # But maybe we want to target them if they are missing something specific? 
        # For now, following instructions: 0 = Modern high-quality website (skip outreach)
        return 0
        
    # Check 4: Copyright Year
    latest_year = check_copyright_year(soup)
    if latest_year and latest_year < 2020:
        return 8 # Old copyright
        
    return score
