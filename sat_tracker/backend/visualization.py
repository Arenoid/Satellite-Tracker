import requests
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from config import ny2o_api_key 

API_KEY = ny2o_api_key 
OBSERVER_LAT = 27.7
OBSERVER_LON = 85.3
OBSERVER_ALT = 0 
RADIUS = 70
CATEGORY = 0 
EARTH_RADIUS = 6371

def llh_to_ecef(lat, lon, alt_km):
    lat = np.radians(lat)
    lon = np.radians(lon)
    r = EARTH_RADIUS + alt_km
    x = r * np.cos(lat) * np.cos(lon)
    y = r * np.cos(lat) * np.sin(lon)
    z = r * np.sin(lat)
    return x, y, z

def fetch_satellites():
    url = f"https://api.n2yo.com/rest/v1/satellite/above/{OBSERVER_LAT}/{OBSERVER_LON}/{OBSERVER_ALT}/{RADIUS}/{CATEGORY}/&apiKey={API_KEY}"
    res = requests.get(url)
    data = res.json()

    sats = []
    for sat in data.get("above", []):
        x, y, z = llh_to_ecef(sat["satlat"], sat["satlng"], sat["satalt"])
        sats.append({
            "satname": sat["satname"],
            "satlat": sat["satlat"],
            "satlng": sat["satlng"],
            "satalt": sat["satalt"],
            "orbit_class": "N/A",
            "X": x,
            "Y": y,
            "Z": z
        })
    return pd.DataFrame(sats)

def visualize_satellites_2d(df, search_query=None):
    
    if search_query:
        df = df[df["satname"].str.contains(search_query, case=False, na=False)]
        title_suffix = f" (Filtered: {search_query})"
    else:
        title_suffix = ""

    sat_trace = go.Scattergeo(
        lon = df["satlng"],
        lat = df["satlat"],
        text = df["satname"] + "<br>Alt: " + df["satalt"].round(2).astype(str) + " km",
        mode = 'markers',
        marker = dict(
            size = 8,
            color = 'yellow',
            opacity = 0.8,
            symbol = 'circle'
        ),
        name = 'Visible Satellites'
    )

    observer_trace = go.Scattergeo(
        lon = [OBSERVER_LON],
        lat = [OBSERVER_LAT],
        text = "Observer Location",
        mode = 'markers',
        marker = dict(
            size = 15,
            color = 'lime',
            symbol = 'star'
        ),
        name = 'Observer'
    )

    fig = go.Figure(data=[sat_trace, observer_trace])

    fig.update_layout(
        title = 'Goofy ahh visualization' + title_suffix,
        geo = dict(
            scope = 'world',
            projection_type = 'mercator',
            showland = True,
            landcolor = "rgb(243, 243, 243)",
            countrycolor = "rgb(204, 204, 204)",
            lataxis = dict(range = [OBSERVER_LAT - 30, OBSERVER_LAT + 30]),
            lonaxis = dict(range = [OBSERVER_LON - 30, OBSERVER_LON + 30]),
            center = dict(lat = OBSERVER_LAT, lon = OBSERVER_LON),
            
            bgcolor = 'lightblue',
            resolution = 50,
            
            showcountries = True,
            showsubunits = True,
            subunitcolor = "darkgray"
        ),
        hovermode = 'closest',
        height=None, 
        width=None 
    )

    plot_config = {
        'responsive': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d', 'hoverClosestGeo'],
        'displayModeBar': True
    }

    fig.write_html(
        "satellite_plot_2d_map_fullscreen.html", 
        auto_open=True,
        config=plot_config,
        full_html=True
    )


if __name__ == "__main__":
    df = fetch_satellites()
    print(f"Fetched {len(df)} total satellites.")

    search_term = input(
        "Enter a satellite name (e.g., STARLINK, OneWeb, NOAA) to search, or press Enter to show all: "
    )
    
    search_term = search_term.strip().upper() if search_term else None

    visualize_satellites_2d(df, search_query=search_term)