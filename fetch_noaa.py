import requests
import pandas as pd

def get_centroid(geometry):
    """Calculate centroid for polygon or return point coordinates."""
    if not geometry:
        return None, None
    
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates")
    
    if geom_type == "Point":
        return coords[1], coords[0]  # lat, lon
    elif geom_type == "Polygon" and coords:
        # Calculate centroid of first ring
        ring = coords[0]
        if len(ring) > 0:
            lats = [point[1] for point in ring]
            lons = [point[0] for point in ring]
            return sum(lats)/len(lats), sum(lons)/len(lons)
    
    return None, None

def fetch_noaa_alerts():
    url = "https://api.weather.gov/alerts/active"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    js = r.json()
    rows = []
    for feat in js["features"]:
        props = feat["properties"]
        geom = feat["geometry"]
        
        lat, lon = get_centroid(geom)
        if lat is not None and lon is not None:
            rows.append({
                "source": "NOAA",
                "event": props.get("event"),
                "severity": props.get("severity"),
                "area": props.get("areaDesc"),
                "headline": props.get("headline"),
                "lat": lat,
                "lon": lon
            })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = fetch_noaa_alerts()
    print(df.head())
    df.to_csv("noaa_alerts.csv", index=False)