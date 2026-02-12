import requests
import time

BASE_URL = "http://127.0.0.1:5002"

def test_index():
    try:
        response = requests.get(BASE_URL)
        if response.status_code == 200:
            print("GET / passed")
        else:
            print(f"GET / failed: {response.status_code}")
    except Exception as e:
        print(f"GET / failed with exception: {e}")

def test_scrape():
    payload = {
        "city": "Palo Alto",
        "query": "Dentist near Palo Alto",
        "max_leads": 1
    }
    try:
        print("Testing POST /scrape (this may take a moment)...")
        response = requests.post(f"{BASE_URL}/scrape", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print(f"POST /scrape passed. Filename: {data.get('filename')}")
                return data.get('filename')
            else:
                print(f"POST /scrape returned non-success: {data}")
        else:
            print(f"POST /scrape failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"POST /scrape failed with exception: {e}")
    return None

def test_download(filename):
    if not filename: return
    try:
        response = requests.get(f"{BASE_URL}/download/{filename}")
        if response.status_code == 200:
            print("GET /download passed")
        else:
            print(f"GET /download failed: {response.status_code}")
    except Exception as e:
        print(f"GET /download failed with exception: {e}")

if __name__ == "__main__":
    test_index()
    filename = test_scrape()
    test_download(filename)
