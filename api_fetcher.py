import aiohttp
import asyncio

async def get_market_data():
    DATA_URL = "https://raw.githubusercontent.com/meytiii/sarraf-bashi-bot/main/data/tgju.json"
    
    results = {
        "usd": "نامشخص", "eur": "نامشخص", "gbp": "نامشخص",
        "iqd": "نامشخص", "try": "نامشخص", "gold_18k": "نامشخص",
        "coin_emami": "نامشخص", "coin_bahar": "نامشخص",
        "coin_half": "نامشخص", "coin_quarter": "نامشخص",
        "silver_ounce": "نامشخص"
    }

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
        try:
            async with session.get(DATA_URL) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    current_data = data.get("current", data)
                    
                    def get_price(keys, unit="ریال"):
                        for key in keys:
                            if key in current_data:
                                if 'p' in current_data[key]:
                                    return f"{current_data[key]['p']} {unit}"
                                elif 'v' in current_data[key]:
                                    return f"{current_data[key]['v']} {unit}"
                        return "نامشخص"

                    results["usd"] = get_price(["price_dollar_rl", "dollar_rl"])
                    results["eur"] = get_price(["price_eur", "eur"])
                    results["gbp"] = get_price(["price_gbp", "gbp"])
                    results["iqd"] = get_price(["price_iqd", "iqd"])
                    results["try"] = get_price(["price_try", "try", "lira"])
                    results["gold_18k"] = get_price(["geram18", "tgju_gold_irg18", "gerami18", "price_gerami18", "gold18", "18ayar", "ayar18", "gerami", "mesghal_18"])
                    results["coin_emami"] = get_price(["sekee", "emami", "sekkeh_emami"])
                    results["coin_bahar"] = get_price(["sekeb", "sekeb_buy", "retail_sekeb", "bahar", "price_bahar", "sekkeh_bahar", "sekeh_bahar", "seke_bahar", "sekebahar", "sekkeh"])
                    results["coin_half"] = get_price(["nim", "nim_sekkeh"])
                    results["coin_quarter"] = get_price(["rob", "rob_sekkeh"])
                    
                    results["silver_ounce"] = get_price(["silver_999", "ons_silver", "silver"])

            return results

        except Exception as e:
            print(f"🚨 TGJU Fetch Error: {e}")
            return None

async def get_history_data():
    assets = {
        "usd": "price_dollar_rl",
        "coin_emami": "sekee",
        "gold_18k": "geram18"
    }
    history = {"usd": {}, "coin_emami": {}, "gold_18k": {}}
    timeout = aiohttp.ClientTimeout(total=10)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
        "Referer": "https://www.tgju.org/"
    }
    
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout, headers=headers) as session:
        for key, tgju_id in assets.items():
            url = f"https://api.tgju.org/v1/market/indicator/summary-table-data/{tgju_id}?start=0&length=7"
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        rows = data.get("data", [])
                        
                        rows.reverse()
                        
                        for row in rows:
                            if len(row) >= 7:
                                date_str = row[6].replace("/", "-") 
                                price_str = row[3].replace(",", "")
                                try:
                                    history[key][date_str] = float(price_str)
                                except ValueError:
                                    continue
            except Exception as e:
                print(f"🚨 History API Fetch Error ({key}): {e}")
                
    return history

if __name__ == "__main__":
    async def test_api():
        data = await get_market_data()
        print(data)
        
    asyncio.run(test_api())