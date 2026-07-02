import aiohttp
import asyncio
import re

async def get_market_data():
    DATA_URL = "https://raw.githubusercontent.com/meytiii/sarraf-bashi-bot/main/data/tgju.json"
    
    # Pre-fill default empty dictionaries
    results = {}
    for k in ["usd", "eur", "gbp", "iqd", "try", "gold_18k", "coin_emami", "coin_bahar", "coin_half", "coin_quarter", "silver_ounce"]:
        results[k] = "نامشخص"
        results[f"{k}_d"] = "0"
        results[f"{k}_dp"] = "0"
        results[f"{k}_dt"] = ""

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
        try:
            async with session.get(DATA_URL) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    current_data = data.get("current", data)
                    
                    def set_price(target_key, keys, unit="ریال"):
                        for key in keys:
                            if key in current_data:
                                item = current_data[key]
                                if 'p' in item:
                                    results[target_key] = f"{item['p']} {unit}"
                                elif 'v' in item:
                                    results[target_key] = f"{item['v']} {unit}"
                                
                                # Extract the change metrics
                                results[f"{target_key}_d"] = str(item.get('d', '0'))
                                results[f"{target_key}_dp"] = str(item.get('dp', '0'))
                                results[f"{target_key}_dt"] = str(item.get('dt', ''))
                                return

                    set_price("usd", ["price_dollar_rl", "dollar_rl"])
                    set_price("eur", ["price_eur", "eur"])
                    set_price("gbp", ["price_gbp", "gbp"])
                    set_price("iqd", ["price_iqd", "iqd"])
                    set_price("try", ["price_try", "try", "lira"])
                    
                    set_price("gold_18k", ["geram18", "tgju_gold_irg18", "gerami18", "price_gerami18", "gold18", "18ayar", "ayar18", "gerami", "mesghal_18"])
                    set_price("coin_emami", ["sekee", "emami", "sekkeh_emami"])
                    set_price("coin_bahar", ["sekeb", "sekeb_buy", "retail_sekeb", "bahar", "price_bahar", "sekkeh_bahar", "sekeh_bahar", "seke_bahar", "sekebahar", "sekkeh"])
                    set_price("coin_half", ["nim", "nim_sekkeh"])
                    set_price("coin_quarter", ["rob", "rob_sekkeh"])
                    set_price("silver_ounce", ["silver_999", "ons_silver", "silver"])

            return results

        except Exception as e:
            print(f"🚨 TGJU Fetch Error: {e}")
            return None


async def get_history_data():
    assets = {
        "usd": ["price_dollar_rl", "dollar_rl", "price_dollar_sm"],
        "coin_emami": ["sekee", "emami", "sekkeh_emami"],
        "gold_18k": ["geram18", "tgju_gold_irg18"]
    }
    history = {"usd": {}, "coin_emami": {}, "gold_18k": {}}
    timeout = aiohttp.ClientTimeout(total=10)
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json", "Referer": "https://www.tgju.org/"}
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout, headers=headers) as session:
        for key, id_list in assets.items():
            for tgju_id in id_list:
                url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{tgju_id}?start=0&length=10"
                try:
                    async with session.get(url) as response:
                        if response.status == 200:
                            data = await response.json()
                            rows = data.get("data", [])
                            if rows:
                                rows.reverse()
                                for row in rows:
                                    if len(row) >= 7:
                                        date_str = row[6].replace("/", "-") 
                                        price_str = re.sub(r'[^\d.]', '', row[3])
                                        if price_str:
                                            history[key][date_str] = float(price_str)
                                break 
                except Exception as e:
                    print(f"🚨 History API Fetch Error ({key} -> {tgju_id}): {e}")
                    
    return history