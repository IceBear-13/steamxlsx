import urllib.request
import pandas as pd
import json
import requests


def get_data(steam_id):
    with urllib.request.urlopen(f"https://steamcommunity.com/id/{steam_id}/inventory/json/730/2") as url:
        data = json.load(url)
    market_names = [item.get('market_hash_name') for item in data['descriptions']]
    
    df = pd.DataFrame({"Skins" : market_names})
    df.to_excel('output.xlsx', index=False)

    
