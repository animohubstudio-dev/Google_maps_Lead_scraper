# utils/file_manager.py
import csv
import os
from datetime import datetime
import config

def setup_output_dir():
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

def save_to_csv(data, filename=None):
    setup_output_dir()
    
    if filename is None:
        filename = config.CSV_FILENAME
        
    filepath = os.path.join(config.OUTPUT_DIR, filename)
    
    # Define headers based on the requirements
    headers = [
        "Business Name", "Website", "Phone", "Email", 
        "Instagram", "Facebook", "LinkedIn", "WhatsApp", 
        "City", "State", "Rating", "Reviews", "Quality Score", "Notes"
    ]
    
    file_exists = os.path.isfile(filepath)
    
    with open(filepath, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        
        if not file_exists:
            writer.writeheader()
            
        for row in data:
            # Filter row to ensure only valid headers are written
            filtered_row = {k: row.get(k, "") for k in headers}
            writer.writerow(filtered_row)
            
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Saved {len(data)} leads to {filepath}")

def generate_summary(data):
    total_leads = len(data)
    high_quality_leads = len([d for d in data if d.get('Quality Score', 0) >= 8])
    
    summary = f"""
    --- Scraping Summary ---
    Total Leads Scraped: {total_leads}
    High Quality Leads (Score >= 8): {high_quality_leads}
    Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    summary_path = os.path.join(config.OUTPUT_DIR, "summary.txt")
    with open(summary_path, "a") as f:
        f.write(summary + "\n")
        
    return summary
