import urllib.request
import pandas as pd
import json
import requests


def get_data(steam_id):
    with urllib.request.urlopen(f"https://steamcommunity.com/inventory/{steam_id}/730/2?l=en&count=5000") as url:
        data = json.load(url)
    market_names = [item.get('market_hash_name') for item in data['descriptions']]
    
    df = pd.DataFrame({"Skins" : market_names})
    df.to_excel('output.xlsx', index=False)

    
