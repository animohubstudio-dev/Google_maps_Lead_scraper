# scraper/website_scraper.py
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Email Regex
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
# Phone Regex (US focused)
PHONE_REGEX = r'(\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'

def extract_emails(text):
    return set(re.findall(EMAIL_REGEX, text))

def extract_phones(text):
    return set(re.findall(PHONE_REGEX, text))

def get_social_links(soup, base_url):
    socials = {
        "Instagram": "",
        "Facebook": "",
        "LinkedIn": "",
        "Twitter": "",
        "TikTok": "",
        "YouTube": ""
    }
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        lower_href = href.lower()
        
        if "instagram.com" in lower_href:
            socials["Instagram"] = href
        elif "facebook.com" in lower_href:
            socials["Facebook"] = href
        elif "linkedin.com" in lower_href:
            socials["LinkedIn"] = href
        elif "twitter.com" in lower_href or "x.com" in lower_href:
            socials["Twitter"] = href
        elif "tiktok.com" in lower_href:
            socials["TikTok"] = href
        elif "youtube.com" in lower_href:
            socials["YouTube"] = href
            
    return socials

def analyze_website(url):
    """
    Visits the website and extracts contact details and quality score.
    Returns a dictionary with extracted data.
    """
    data = {
        "Website": url,
        "Emails": [],
        "Phones": [],
        "Socials": {},
        "Quality Score": 10,
        "Notes": ""
    }
    
    if not url:
        data["Notes"] = "No Website"
        return data

    try:
        response = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            data["Notes"] = f"Error: {response.status_code}"
            return data
            
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract Contact Details
        text_content = soup.get_text()
        emails = extract_emails(text_content)
        phones = extract_phones(text_content)
        socials = get_social_links(soup, url)
        
        # Check for booking keywords
        booking_keywords = ["book online", "schedule appointment", "request appointment", "book now"]
        has_booking = any(keyword in text_content.lower() for keyword in booking_keywords)
        
        data["Emails"] = list(emails)
        data["Phones"] = list(phones)
        data["Socials"] = socials
        
        # Calculate Quality Score
        from utils.quality_score import calculate_quality_score
        score = calculate_quality_score(url) # This might re-request, but we can refactor later to reuse soup if needed. 
        # Actually, quality_score.py requests strictly to do its own checks (like header checks which bs4 doesn't do easily without requests obj).
        # We can optimize by passing response object if we refactor quality_score.
        # For now, let's just call it.
        
        data["Quality Score"] = score
        
        if not has_booking:
            data["Notes"] += "No booking system detected. "
            
    except Exception as e:
        data["Notes"] = f"Scraping Error: {str(e)}"
        
    return data
