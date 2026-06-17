import os
import json
import requests

# We will save everything into a single file now!
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
TGJU_PATH = os.path.join(DATA_DIR, 'tgju.json')

def main():
    url = "https://call3.tgju.org/ajax.json?rev=fdQuRN1kGtR9rQviUtqdaPuDpnyMsBYyjj0hMOhG3CD3amFqrGmp6EHB9TWs"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.tgju.org/"
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            os.makedirs(DATA_DIR, exist_ok=True)
            
            with open(TGJU_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print("✅ Data successfully fetched and saved to data/tgju.json!")
        else:
            print(f"❌ Failed to fetch data. Status Code: {response.status_code}")

    except Exception as e:
        print(f"🚨 Error fetching data: {e}")

if __name__ == "__main__":
    main()