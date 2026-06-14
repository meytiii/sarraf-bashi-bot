import os
import time
import json
import base64
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
FIAT_PATH = os.path.join(DATA_DIR, 'fiat.json')
GOLD_PATH = os.path.join(DATA_DIR, 'gold.json')

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)

def get_phpsessid(driver, url):
    driver.get(url)
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(2)
    for cookie in driver.get_cookies():
        if cookie['name'] == 'PHPSESSID':
            return cookie['value']
    return None

def make_request(driver, endpoint, filename, csrf_token):
    unix_time = int(time.time())
    url = f"https://www.navasan.net/{endpoint}?csrf={csrf_token}&_={unix_time}"

    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': 'https://www.navasan.net/',
    }

    response = requests.get(url, headers=headers, cookies=cookies, timeout=15)
    if response.status_code == 200:
        try:
            data = response.json()
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except json.JSONDecodeError:
            with open(filename.replace('.json', '.txt'), 'w', encoding='utf-8') as f:
                f.write(response.text)

def main():
    url = "https://www.navasan.net/"
    prefix = "2bba8a6abdcae9571d63fefcd1df29bb3a8f5d91http://www.navasan.net/54tf%f"

    driver = get_driver()
    try:
        phpsessid = get_phpsessid(driver, url)
        if not phpsessid:
            print("PHPSESSID not found.")
            return
        csrf_token = base64.b64encode((prefix + phpsessid).encode()).decode()

        os.makedirs(DATA_DIR, exist_ok=True)

        make_request(driver, "last_currencies.php", FIAT_PATH, csrf_token)
        make_request(driver, "gold_rates.php", GOLD_PATH, csrf_token)

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
