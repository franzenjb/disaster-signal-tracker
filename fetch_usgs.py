import requests
import pandas as pd

def fetch_usgs_earthquakes():
    """
    Fetch recent USGS earthquakes (past 7 days, M ≥ 2.5)
    Returns a DataFrame with lat/lon/magnitude/place.
    """
    url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_week.geojson"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    js = r.json()

    rows = []
    for feat in js["features"]:
        props = feat["properties"]
        geom = feat["geometry"]
        if geom and geom.get("type") == "Point":
            coords = geom["coordinates"]
            rows.append({
                "source": "USGS",
                "event": "Earthquake",
                "magnitude": props.get("mag"),
                "place": props.get("place"),
                "time": pd.to_datetime(props.get("time"), unit="ms"),
                "lat": coords[1],
                "lon": coords[0]
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = fetch_usgs_earthquakes()
    print(f"✅ {len(df)} earthquakes retrieved")
    df.to_csv("usgs_earthquakes.csv", index=False)