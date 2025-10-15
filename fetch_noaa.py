import requests
import pandas as pd

def fetch_noaa_alerts():
    url = "https://api.weather.gov/alerts/active"
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
                "source": "NOAA",
                "event": props.get("event"),
                "severity": props.get("severity"),
                "area": props.get("areaDesc"),
                "headline": props.get("headline"),
                "lat": coords[1],
                "lon": coords[0]
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = fetch_noaa_alerts()
    print(df.head())
    df.to_csv("noaa_alerts.csv", index=False)