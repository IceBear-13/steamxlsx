import urllib.request
import urllib.parse
import urllib.error
import pandas as pd
import json
import re
import time


def _json_get(url: str, retries: int = 3, timeout: int = 20) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": "steamxlsx/1.0"})
    delay_seconds = 1.0

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return json.load(response)
        except urllib.error.HTTPError as err:
            if err.code == 429 and attempt < retries:
                retry_after = err.headers.get("Retry-After")
                wait = float(retry_after) if retry_after else delay_seconds
                time.sleep(wait)
                delay_seconds *= 2
                continue
            raise
        except urllib.error.URLError:
            if attempt < retries:
                time.sleep(delay_seconds)
                delay_seconds *= 2
                continue
            raise


def _get_market_value(item: str) -> str:
    url = f"https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={urllib.parse.quote(item)}"
    data = _json_get(url)
    return data.get("median_price") or "Unknown"

def _extract_quality(item: dict, market_name: str) -> str:
    tags = item.get("tags", [])
    for tag in tags:
        category = (tag.get("category") or "").lower()
        if category in {"exterior", "quality"}:
            return tag.get("localized_tag_name") or tag.get("name") or "Unknown"

    # Fallback for names like: "AK-47 | Redline (Field-Tested)"
    match = re.search(r"\(([^()]*)\)\s*$", market_name)
    if match:
        return match.group(1).strip()

    return "Unknown"


def _fetch_inventory_page(steam_id: str, start_assetid: str | None = None) -> dict:
    # params = {"l": "english", "count": "5000"}
    # if start_assetid:
    #     params["start_assetid"] = start_assetid

    # query = urllib.parse.urlencode(params)
    url = f"https://steamcommunity.com/inventory/{steam_id}/730/2"
    return _json_get(url)


def get_data(steam_id: str, fetch_market_values: bool = False):
    try:
        descriptions = []
        start_assetid = None

        # Handle multi-page inventories.
        while True:
            data = _fetch_inventory_page(steam_id, start_assetid)

            if data.get("success") != 1:
                message = data.get("error", "Unknown inventory API error")
                raise ValueError(f"Failed to fetch inventory: {message}")

            descriptions.extend(data.get("descriptions", []))

            if not data.get("more_items"):
                break
            start_assetid = data.get("last_assetid")
            if not start_assetid:
                break

        market_values: dict[str, str] = {}
        if fetch_market_values:
            # One request per unique item name instead of one request per inventory row.
            unique_names = {
                item.get("market_name") or item.get("market_hash_name") or item.get("name")
                for item in descriptions
            }
            unique_names.discard(None)

            for idx, market_name in enumerate(sorted(unique_names)):
                market_values[market_name] = _get_market_value(market_name)
                # Add a small delay to avoid rate-limiting by Steam market API.
                if idx < len(unique_names) - 1:
                    time.sleep(0.25)

        rows = []
        for item in descriptions:
            market_name = item.get("market_name") or item.get("market_hash_name") or item.get("name")
            if not market_name:
                continue

            row = {
                "market_name": market_name,
                "quality": _extract_quality(item, market_name),
                "tradable": bool(item.get("tradable", 0)),
                "marketable": bool(item.get("marketable", 0)),
                "market_value": _get_market_value(market_name),
            }
            
            time.sleep(5)  # Add a delay to avoid rate-limiting by Steam market API.

            for tag in item.get("tags", []):
                if (tag.get("category") or "").lower() == "rarity":
                    row["rarity"] = tag.get("localized_tag_name") or tag.get("name") or "Unknown"
                    break

            rows.append(row)

        df = pd.DataFrame(rows, columns=["market_name", "quality", "tradable", "marketable", "market_value"])
        df.to_excel("output.xlsx", index=False)

        return df
    except Exception as e:
        print(f"Error fetching inventory: {e}")
        return pd.DataFrame()
    finally:
        print("Finished fetching inventory.")
