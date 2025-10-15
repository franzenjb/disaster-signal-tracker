import requests
import json

def debug_noaa_alerts():
    url = "https://api.weather.gov/alerts/active"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    js = r.json()
    
    print(f"Total features: {len(js['features'])}")
    
    if js['features']:
        first_feature = js['features'][0]
        print(f"First feature geometry type: {first_feature['geometry']['type'] if first_feature['geometry'] else 'None'}")
        print("Sample properties:", json.dumps(first_feature['properties'], indent=2)[:500])
        
        # Check geometry types
        geom_types = {}
        for feat in js['features']:
            geom_type = feat['geometry']['type'] if feat['geometry'] else 'None'
            geom_types[geom_type] = geom_types.get(geom_type, 0) + 1
        
        print("Geometry types:", geom_types)

if __name__ == "__main__":
    debug_noaa_alerts()