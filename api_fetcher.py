import aiohttp
import asyncio

async def get_market_data():
    DATA_URL = "https://raw.githubusercontent.com/meytiii/sarraf-bashi-bot/main/data/tgju.json"
    
    results = {
        "usd": "نامشخص",
        "eur": "نامشخص",
        "gbp": "نامشخص",
        "iqd": "نامشخص",
        "try": "نامشخص",
        "gold_18k": "نامشخص",
        "coin_emami": "نامشخص",
        "coin_bahar": "نامشخص",
        "coin_half": "نامشخص",
        "coin_quarter": "نامشخص",
        "silver_ounce": "نامشخص"
    }

    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), timeout=timeout) as session:
        try:
            async with session.get(DATA_URL) as response:
                if response.status == 200:
                    data = await response.json(content_type=None)
                    
                    current_data = data.get("current", data)
                    
                    def get_price(key, unit="تومان"):
                        try:
                            if key in current_data:
                                return f"{current_data[key]['p']} {unit}"
                            return "نامشخص"
                        except:
                            return "نامشخص"

                    results["usd"] = get_price("price_dollar_rl")
                    results["eur"] = get_price("price_eur")
                    results["gbp"] = get_price("price_gbp")
                    results["iqd"] = get_price("price_iqd")
                    results["try"] = get_price("price_try")
                    
                    results["gold_18k"] = get_price("gerami18")
                    results["coin_emami"] = get_price("sekee")
                    results["coin_bahar"] = get_price("sekkeh")
                    results["coin_half"] = get_price("nim")
                    results["coin_quarter"] = get_price("rob")
                    
                    results["silver_ounce"] = get_price("ons_silver", "دلار")

            return results

        except Exception as e:
            print(f"🚨 TGJU Fetch Error: {e}")
            return None

if __name__ == "__main__":
    async def test_api():
        data = await get_market_data()
        print(data)
        
    asyncio.run(test_api())