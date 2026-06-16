import aiohttp
import asyncio

async def get_market_data():
    FIAT_URL = "https://raw.githubusercontent.com/meytiii/sarraf-bashi-bot/main/data/fiat.json"
    GOLD_URL = "https://raw.githubusercontent.com/meytiii/sarraf-bashi-bot/main/data/gold.json"
    
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
            async with session.get(FIAT_URL) as response:
                if response.status == 200:
                    fiat_data = await response.json(content_type=None)
                    
                    if "usd" in fiat_data:
                        results["usd"] = f"{int(fiat_data['usd']['value']):,} تومان"
                    if "eur" in fiat_data:
                        results["eur"] = f"{int(fiat_data['eur']['value']):,} تومان"
                    if "gbp" in fiat_data:
                        results["gbp"] = f"{int(fiat_data['gbp']['value']):,} تومان"
                    if "iqd" in fiat_data:
                        results["iqd"] = f"{int(fiat_data['iqd']['value']):,} تومان"
                    if "try" in fiat_data:
                        results["try"] = f"{int(fiat_data['try']['value']):,} تومان"
                    if "xag" in fiat_data:
                        results["silver_ounce"] = f"{int(fiat_data['xag']['value']):,} تومان"

            # 2. Fetch Gold and Coin Data
            async with session.get(GOLD_URL) as response:
                if response.status == 200:
                    gold_data = await response.json(content_type=None)
                    
                    if "18ayar" in gold_data:
                        results["gold_18k"] = f"{int(gold_data['18ayar']['value']):,} تومان"
                    if "sekkeh" in gold_data:
                        results["coin_emami"] = f"{int(gold_data['sekkeh']['value']):,} تومان"
                    if "bahar" in gold_data:
                        results["coin_bahar"] = f"{int(gold_data['bahar']['value']):,} تومان"
                    if "nim" in gold_data:
                        results["coin_half"] = f"{int(gold_data['nim']['value']):,} تومان"
                    if "rob" in gold_data:
                        results["coin_quarter"] = f"{int(gold_data['rob']['value']):,} تومان"

            return results

        except Exception as e:
            print(f"🚨 GitHub Fetch Error: {e}")
            return None