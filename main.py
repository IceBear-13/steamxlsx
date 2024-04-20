from steam_web_api import Steam
import settings
import json_csv


def run():
    KEY = settings.STEAM_API_KEY

    steam = Steam(KEY)
    steam_id = input("Input Steam ID")
    def fetch_steam_profile(custom_url):
        dict = steam.users.get_steamid(custom_url)
        return dict['steamid']
    
    steamid = fetch_steam_profile(steam_id)
    
    json_csv.get_data(steamid)
    



if __name__ == "__main__":
    run()