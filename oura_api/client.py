import requests
from datetime import datetime, timedelta

OURA_API_BASE = "https://api.ouraring.com/v2/usercollection/enhanced_tag"

def fetch_tag_data(token: str, days_back: int = 7) -> list:
    """
    Fetch enhanced tag data from Oura API for the past `days_back` days.
    Returns a list of enhanced tag dictionaries.
    """
    headers = {
        "Authorization": f"Bearer {token}"
    }

    end_date = datetime.utcnow().date()
    start_date = end_date - timedelta(days=days_back)
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat()
    }

    all_data = []
    next_token = None

    while True:
        if next_token:
            params["next_token"] = next_token

        response = requests.get(OURA_API_BASE, headers=headers, params=params)
        response.raise_for_status()

        data = response.json()
        all_data.extend(data.get("data", []))

        next_token = data.get("next_token")
        if not next_token:
            break

    return all_data
