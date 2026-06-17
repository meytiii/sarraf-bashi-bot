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

if __name__ == "__main__":
    async def test_api():
        data = await get_market_data()
        print(data)
        
    asyncio.run(test_api())