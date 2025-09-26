import pandas as pd
import requests
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from backend.config import ny2o_api_key

def api_caller(locations):
    base_url = 'https://api.n2yo.com/rest/v1/satellite/'
    if not ny2o_api_key:
        print("API key is missing in config.py!")
        return None

    print("API key loaded successfully")

    meta_info_columns = ['seen_from','category','transactioncount','satcount']
    meta_info_df = pd.DataFrame(columns=meta_info_columns)

    sat_info_columns = ["seen_from","satid","launchdate","satlat","satlng","satlt"]
    sat_info_df = pd.DataFrame(columns=sat_info_columns)

    for loc in locations:
        name = loc['name']
        lat = loc['lat']
        long = loc['long']
        alt = loc['alt']
        radius = loc['radius']
        sat_cat = loc['sat_cat']

        api_info = f'above/{lat}/{long}/{alt}/{radius}/{sat_cat}'
        full_api_url = base_url+api_info+'&apiKey='+ny2o_api_key

        response = requests.get(full_api_url)
        if response.status_code == 200:
            content = response.json()
            loc_sat_df = pd.DataFrame(content['above'])
            loc_sat_df['seen_from'] = name 
            meta_info_df = pd.concat([meta_info_df,sat_info_df],ignore_index=True)
            sat_info_df = pd.concat([sat_info_df,loc_sat_df], ignore_index=True)
            print(f"Fetched Successfully for{name}")
        else:
            print(f"Failed to fetch data for {name}. Status code:{response.status_code}")
    return meta_info_df,sat_info_df
api_caller()

