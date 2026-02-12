from flask import Flask, render_template, request, jsonify, send_from_directory
import os
import main
import config

app = Flask(__name__)
# Ensure output directory exists for downloads
OUTPUT_DIR = "output"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    city = data.get('city')
    query = data.get('query') # Optional override
    max_leads = data.get('max_leads')

    if not city:
        return jsonify({"status": "error", "message": "City is required"}), 400

    query_list = [query] if query else None

    # Run the scraper
    # Note: This is blocking. In production, use Celery/Redis.
    try:
        result = main.run_scraper(city, query_list=query_list, max_leads=max_leads)
        
        if result['success']:
            return jsonify({
                "status": "success", 
                "filename": result['filename'],
                "summary": {
                    "total_leads": result['total_leads'],
                    "message": result['message']
                }
            })
        else:
             return jsonify({
                "status": "warning", 
                "message": result['message']
            })

    except Exception as e:
        print(f"Scraping error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/download/<filename>')
def download_file(filename):
    # Security check: ensure filename is just a name, not a path
    if '/' in filename or '\\' in filename:
         return "Invalid filename", 400
    try:
        return send_from_directory(OUTPUT_DIR, filename, as_attachment=True)
    except FileNotFoundError:
        return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5002)
