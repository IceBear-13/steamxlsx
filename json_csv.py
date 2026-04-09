import urllib.request
import pandas as pd
import json
import requests


def get_data(steam_id):
    with urllib.request.urlopen(f"https://steamcommunity.com/inventory/{steam_id}/730/2") as url:
        data = json.load(url)
    
    items = data['descriptions']
    market_names = []
    for item in items:
        market_names.append(item['name'])
        
    print(market_names)

    df = pd.DataFrame({"Skins" : market_names})
    df.to_excel('output.xlsx', index=False)

# get_data("ripaimmm")
