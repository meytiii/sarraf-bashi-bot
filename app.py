import os
import json
import requests

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
            current_market = data.get("current", {})
            
            os.makedirs(DATA_DIR, exist_ok=True)
            
            with open(TGJU_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
            print("✅ Data successfully fetched and saved to data/tgju.json!")
            
            # --- 7-Day History Logging System ---
            HISTORY_PATH = os.path.join(DATA_DIR, 'history.json')
            
            def extract_val(keys):
                for k in keys:
                    if k in current_market:
                        return float(re.sub(r'[^\d.]', '', current_market[k]['p']))
                return None

            import re
            import datetime
            today_str = datetime.date.today().isoformat()
            
            live_prices = {
                "usd": extract_val(["price_dollar_rl", "dollar_rl"]),
                "coin_emami": extract_val(["sekee", "emami", "sekkeh_emami"]),
                "gold_18k": extract_val(["geram18", "tgju_gold_irg18"])
            }
            
            if os.path.exists(HISTORY_PATH):
                with open(HISTORY_PATH, 'r', encoding='utf-8') as h_file:
                    history = json.load(h_file)
            else:
                history = {"usd": {}, "coin_emami": {}, "gold_18k": {}}
                
            for asset, price in live_prices.items():
                if price:
                    history[asset][today_str] = price
                    
                    sorted_dates = sorted(history[asset].keys())[-7:]
                    history[asset] = {d: history[asset][d] for d in sorted_dates}
                    
            with open(HISTORY_PATH, 'w', encoding='utf-8') as h_file:
                json.dump(history, h_file, indent=2, ensure_ascii=False)
            print("📈 Rolling history log updated successfully!")
        else:
            print(f"❌ Failed to fetch data. Status Code: {response.status_code}")

    except Exception as e:
        print(f"🚨 Error fetching data: {e}")

if __name__ == "__main__":
    main()