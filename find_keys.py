import json
import os

filepath = os.path.join('data', 'tgju.json')
with open(filepath, encoding='utf-8') as f:
    data = json.load(f)
    current = data.get('current', data)
    
    print("--- ALL TGJU KEYS ---")
    for key in current.keys():
        print(key)