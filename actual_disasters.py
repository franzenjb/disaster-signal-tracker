import requests
import pandas as pd
from datetime import datetime, timedelta

def get_actual_disasters():
    """Focus on REAL disasters happening RIGHT NOW that emergency managers care about"""
    
    disasters = []
    
    # 1. MAJOR EARTHQUAKES (M5.0+) in last 24 hours
    print("🔍 Checking for significant earthquakes...")
    try:
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_day.geojson"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        for quake in data['features']:
            props = quake['properties']
            coords = quake['geometry']['coordinates']
            mag = props.get('mag', 0)
            
            if mag >= 5.0:  # Only significant earthquakes
                disasters.append({
                    'type': 'MAJOR_EARTHQUAKE',
                    'magnitude': mag,
                    'location': props.get('place', ''),
                    'time': pd.to_datetime(props.get('time'), unit='ms'),
                    'lat': coords[1],
                    'lon': coords[0],
                    'url': props.get('url', ''),
                    'priority': 'CRITICAL' if mag >= 7.0 else 'HIGH'
                })
    except Exception as e:
        print(f"Error fetching earthquakes: {e}")
    
    # 2. ACTIVE SEVERE WEATHER WARNINGS (not advisories)
    print("🌪️ Checking for severe weather warnings...")
    try:
        url = "https://api.weather.gov/alerts/active"
        r = requests.get(url, timeout=10)
        data = r.json()
        
        critical_events = ['Tornado Warning', 'Hurricane Warning', 'Flash Flood Warning', 
                          'Severe Thunderstorm Warning', 'Blizzard Warning']
        
        for alert in data['features']:
            props = alert['properties']
            event = props.get('event', '')
            severity = props.get('severity', '')
            
            if event in critical_events or severity == 'Extreme':
                geom = alert.get('geometry')
                if geom and geom.get('type') == 'Polygon':
                    coords = geom['coordinates'][0]
                    center_lat = sum(p[1] for p in coords) / len(coords)
                    center_lon = sum(p[0] for p in coords) / len(coords)
                    
                    disasters.append({
                        'type': 'SEVERE_WEATHER',
                        'event': event,
                        'severity': severity,
                        'area': props.get('areaDesc', ''),
                        'headline': props.get('headline', ''),
                        'expires': props.get('expires', ''),
                        'lat': center_lat,
                        'lon': center_lon,
                        'priority': 'CRITICAL' if severity == 'Extreme' else 'HIGH'
                    })
    except Exception as e:
        print(f"Error fetching weather alerts: {e}")
    
    # 3. LARGE ACTIVE WILDFIRES (high confidence only)
    print("🔥 Checking for major active wildfires...")
    try:
        url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_USA_contiguous_and_Hawaii_24h.csv"
        r = requests.get(url, timeout=10)
        df = pd.read_csv(pd.io.StringIO(r.text))
        
        # Filter for high-confidence, high-intensity fires only
        major_fires = df[
            (df['confidence'] >= 80) & 
            (df['frp'] >= 100)  # Fire Radiative Power - indicates intensity
        ].copy()
        
        # Group nearby fires into fire complexes
        fire_clusters = []
        for _, fire in major_fires.iterrows():
            disasters.append({
                'type': 'MAJOR_WILDFIRE',
                'confidence': fire['confidence'],
                'brightness': fire['brightness'],
                'frp': fire['frp'],
                'lat': fire['latitude'],
                'lon': fire['longitude'],
                'detection_time': f"{fire['acq_date']} {fire['acq_time']}",
                'priority': 'CRITICAL' if fire['frp'] >= 500 else 'HIGH'
            })
    except Exception as e:
        print(f"Error fetching wildfire data: {e}")
    
    # 4. Check for trending disaster keywords in news
    print("📰 Checking breaking disaster news...")
    disaster_keywords = ['earthquake', 'hurricane', 'tornado', 'wildfire', 'tsunami', 'volcano']
    
    # Filter and prioritize
    current_disasters = []
    now = datetime.now()
    
    for disaster in disasters:
        # Only include recent events
        if 'time' in disaster:
            if (now - disaster['time']).total_seconds() > 86400:  # Skip if > 24 hours old
                continue
        
        # Only include high-priority events
        if disaster.get('priority') in ['CRITICAL', 'HIGH']:
            current_disasters.append(disaster)
    
    return current_disasters

def generate_emergency_report():
    """Generate actionable emergency management report"""
    disasters = get_actual_disasters()
    
    if not disasters:
        print("✅ No major disasters currently active")
        return
    
    critical = [d for d in disasters if d.get('priority') == 'CRITICAL']
    high = [d for d in disasters if d.get('priority') == 'HIGH']
    
    print(f"\n🚨 EMERGENCY SITUATION REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M UTC')}")
    print("=" * 60)
    
    if critical:
        print(f"\n🔴 CRITICAL EVENTS REQUIRING IMMEDIATE RESPONSE ({len(critical)}):")
        for event in critical:
            if event['type'] == 'MAJOR_EARTHQUAKE':
                print(f"  🌍 M{event['magnitude']} Earthquake - {event['location']}")
            elif event['type'] == 'SEVERE_WEATHER':
                print(f"  🌪️ {event['event']} - {event['area']}")
            elif event['type'] == 'MAJOR_WILDFIRE':
                print(f"  🔥 Major Wildfire - FRP {event['frp']}, Confidence {event['confidence']}%")
    
    if high:
        print(f"\n🟡 HIGH PRIORITY EVENTS ({len(high)}):")
        for event in high[:5]:  # Top 5 only
            if event['type'] == 'MAJOR_EARTHQUAKE':
                print(f"  🌍 M{event['magnitude']} Earthquake - {event['location']}")
            elif event['type'] == 'SEVERE_WEATHER':
                print(f"  ⛈️ {event['event']} - {event['area']}")
            elif event['type'] == 'MAJOR_WILDFIRE':
                print(f"  🔥 Wildfire - FRP {event['frp']}")
    
    # Save actionable data
    if disasters:
        df = pd.DataFrame(disasters)
        df.to_csv('active_emergencies.csv', index=False)
        print(f"\n💾 Emergency data saved to active_emergencies.csv")
    
    return disasters

if __name__ == "__main__":
    generate_emergency_report()