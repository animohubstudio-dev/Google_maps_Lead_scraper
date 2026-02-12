# main.py
import argparse
import time
import config
from scraper.maps_scraper import MapsScraper
from scraper.website_scraper import analyze_website
from utils.file_manager import save_to_csv, generate_summary

def filter_leads(leads):
    """
    Filters leads based on SKIP_KEYWORDS and Quality Score.
    """
    filtered_leads = []
    
    for lead in leads:
        name = lead.get("Business Name", "").lower()
        
        # Check skip keywords
        skip = False
        for keyword in config.SKIP_KEYWORDS:
            if keyword.lower() in name:
                skip = True
                print(f"Skipping (Keyword match): {lead['Business Name']}")
                break
        if skip: continue
        
        # Check Quality Score
        score = lead.get("Quality Score", 5) # Default to 5 if missing
        if score < 8:
            print(f"Skipping (Low Quality Score {score}): {lead['Business Name']}")
            continue
            
        filtered_leads.append(lead)
        
    return filtered_leads

def run_scraper(city, query_list=None, max_leads=None):
    """
    Runs the scraper logic and returns the generated filename.
    """
    print(f"--- Starting Scraper for City: {city} ---")
    
    # Update config if max_leads is provided
    original_max_leads = config.MAX_LEADS_PER_RUN
    if max_leads:
        config.MAX_LEADS_PER_RUN = int(max_leads)
        
    maps_scraper = MapsScraper()
    unique_leads = {}
    
    try:
        queries = config.SEARCH_QUERIES
        if query_list:
            queries = query_list
            
        for query_template in queries:
            # Handle if template or direct string
            if "{city}" in query_template:
                query = query_template.format(city=city)
            else:
                query = query_template
                
            print(f"Running Query: {query}")
            
            maps_scraper.search(query)
            leads = maps_scraper.get_leads()
            print(f"Found {len(leads)} leads from Maps.")
            
            # Enrich with Website Data
            print("Enriching leads with website data...")
            for i, lead in enumerate(leads):
                name = lead.get("Business Name")
                if not name:
                    continue
                    
                if name in unique_leads:
                    print(f"Skipping duplicate: {name}")
                    continue
                
                website = lead.get("Website")
                if website:
                    print(f"[{i+1}/{len(leads)}] Visiting {website}...")
                    web_data = analyze_website(website)
                    
                    # Merge data
                    lead.update(web_data)
                else:
                    lead["Quality Score"] = 10 # No website
                    lead["Notes"] = "No Website listed on Maps."
                
                # Default empty fields if missing
                for field in ["Email", "Instagram", "Facebook", "LinkedIn", "WhatsApp"]:
                     if field not in lead: lead[field] = ""
                     
                # Flatten Socials for CSV
                socials = lead.get("Socials", {})
                if socials:
                    lead["Instagram"] = socials.get("Instagram", "")
                    lead["Facebook"] = socials.get("Facebook", "")
                    lead["LinkedIn"] = socials.get("LinkedIn", "")
                    lead["WhatsApp"] = socials.get("WhatsApp", "") 
                
                # Flatten specific fields
                if isinstance(lead.get("Emails"), list):
                    lead["Email"] = ", ".join(lead["Emails"])
                
                # Ensure duplicate phones are handled
                web_phones = []
                if isinstance(lead.get("Phones"), list):
                     web_phones = lead.get("Phones")
                
                current_phone = lead.get("Phone", "")
                all_phones = set()
                if current_phone: 
                    all_phones.add(current_phone)
                for p in web_phones: 
                    all_phones.add(p)
                
                lead["Phone"] = ", ".join(list(all_phones))

                unique_leads[name] = lead

    finally:
        maps_scraper.close()
        # Restore config
        config.MAX_LEADS_PER_RUN = original_max_leads
        
    all_leads = list(unique_leads.values())
    print(f"Total Unique Leads: {len(all_leads)}")
    
    # Filter
    print("Filtering leads...")
    final_leads = filter_leads(all_leads)
    
    # Save
    if final_leads:
        filename = f"leads_{city.replace(' ', '_')}_{int(time.time())}.csv"
        save_to_csv(final_leads, filename=filename)
        generate_summary(final_leads)
        print(f"Done! Saved to {filename}")
        
        return {
            "success": True,
            "filename": filename,
            "total_leads": len(final_leads),
            "message": f"Successfully scraped {len(final_leads)} leads."
        }
    else:
        print("No leads found matching criteria.")
        return {
            "success": False,
            "filename": None,
            "total_leads": 0,
            "message": "No leads found matching criteria."
        }

def main():
    parser = argparse.ArgumentParser(description="Autonomous Lead Scraper")
    parser.add_argument("--city", type=str, help="Target city for scraping", required=True)
    parser.add_argument("--query", type=str, help="Specific query override")
    
    args = parser.parse_args()
    
    queries = None
    if args.query:
        queries = [args.query]
        
    run_scraper(args.city, queries)

if __name__ == "__main__":
    main()
