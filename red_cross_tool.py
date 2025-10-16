import requests
import pandas as pd
from datetime import datetime, timedelta
import folium

class RedCrossDisasterTool:
    """Focused disaster monitoring for American Red Cross operations"""
    
    def __init__(self):
        # US geographic bounds
        self.us_bounds = {
            'lat_min': 18.9,   # Southern tip of Hawaii
            'lat_max': 71.4,   # Northern Alaska
            'lon_min': -179.0, # Western Alaska
            'lon_max': -66.9   # Eastern Maine
        }
        
        # Events that trigger Red Cross shelter response
        self.shelter_triggers = [
            'Hurricane Warning', 'Hurricane Watch', 'Tornado Warning',
            'Flash Flood Warning', 'Flood Warning', 'Blizzard Warning',
            'Ice Storm Warning', 'Severe Thunderstorm Warning'
        ]

    def get_us_weather_emergencies(self):
        """Get current weather emergencies requiring shelter response"""
        emergencies = []
        
        try:
            url = "https://api.weather.gov/alerts/active"
            r = requests.get(url, timeout=10)
            data = r.json()
            
            for alert in data['features']:
                props = alert['properties']
                event = props.get('event', '')
                severity = props.get('severity', '')
                
                # Only shelter-triggering events
                if event in self.shelter_triggers or severity == 'Extreme':
                    geom = alert.get('geometry')
                    if geom and geom.get('type') == 'Polygon':
                        coords = geom['coordinates'][0]
                        center_lat = sum(p[1] for p in coords) / len(coords)
                        center_lon = sum(p[0] for p in coords) / len(coords)
                        
                        # US territory only
                        if self._is_us_territory(center_lat, center_lon):
                            expires = props.get('expires', '')
                            expires_dt = pd.to_datetime(expires) if expires else None
                            
                            # Only active alerts
                            if not expires_dt or expires_dt > datetime.now():
                                emergencies.append({
                                    'type': 'WEATHER_EMERGENCY',
                                    'event': event,
                                    'severity': severity,
                                    'area': props.get('areaDesc', ''),
                                    'headline': props.get('headline', ''),
                                    'expires': expires,
                                    'lat': center_lat,
                                    'lon': center_lon,
                                    'shelter_required': True
                                })
        except Exception as e:
            print(f"Error fetching weather alerts: {e}")
        
        return emergencies

    def get_us_earthquakes(self):
        """Get significant earthquakes in US territory (last 24 hours)"""
        earthquakes = []
        
        try:
            url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
            r = requests.get(url, timeout=10)
            data = r.json()
            
            for quake in data['features']:
                props = quake['properties']
                coords = quake['geometry']['coordinates']
                mag = props.get('mag', 0)
                
                # Only significant earthquakes in US territory
                if mag >= 4.0 and self._is_us_territory(coords[1], coords[0]):
                    earthquakes.append({
                        'type': 'EARTHQUAKE',
                        'magnitude': mag,
                        'location': props.get('place', ''),
                        'time': pd.to_datetime(props.get('time'), unit='ms'),
                        'lat': coords[1],
                        'lon': coords[0],
                        'shelter_required': mag >= 5.5  # Significant damage threshold
                    })
        except Exception as e:
            print(f"Error fetching earthquakes: {e}")
        
        return earthquakes

    def get_us_wildfires(self):
        """Get major active wildfires in US territory"""
        wildfires = []
        
        try:
            # Use MODIS data for US only
            url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_USA_contiguous_and_Hawaii_24h.csv"
            r = requests.get(url, timeout=10)
            from io import StringIO
            df = pd.read_csv(StringIO(r.text))
            
            # Filter for high-confidence, high-intensity fires
            major_fires = df[
                (df['confidence'] >= 85) & 
                (df['frp'] >= 200) &  # High fire radiative power
                (df['latitude'] >= self.us_bounds['lat_min']) &
                (df['latitude'] <= self.us_bounds['lat_max']) &
                (df['longitude'] >= self.us_bounds['lon_min']) &
                (df['longitude'] <= self.us_bounds['lon_max'])
            ]
            
            for _, fire in major_fires.iterrows():
                wildfires.append({
                    'type': 'WILDFIRE',
                    'confidence': fire['confidence'],
                    'frp': fire['frp'],
                    'lat': fire['latitude'],
                    'lon': fire['longitude'],
                    'detection_time': f"{fire['acq_date']} {fire['acq_time']}",
                    'shelter_required': fire['frp'] >= 500  # Very large fires
                })
        except Exception as e:
            print(f"Error fetching wildfire data: {e}")
        
        return wildfires

    def _is_us_territory(self, lat, lon):
        """Check if coordinates are within US territory"""
        return (self.us_bounds['lat_min'] <= lat <= self.us_bounds['lat_max'] and
                self.us_bounds['lon_min'] <= lon <= self.us_bounds['lon_max'])

    def generate_shelter_deployment_report(self):
        """Generate actionable report for Red Cross shelter deployment"""
        print("🏠 RED CROSS SHELTER DEPLOYMENT ANALYSIS")
        print("=" * 60)
        
        # Get all current US disasters
        weather = self.get_us_weather_emergencies()
        earthquakes = self.get_us_earthquakes()
        wildfires = self.get_us_wildfires()
        
        all_events = weather + earthquakes + wildfires
        
        # Filter for shelter-requiring events only
        shelter_events = [e for e in all_events if e.get('shelter_required', False)]
        
        if not shelter_events:
            print("✅ No major disasters currently requiring shelter deployment")
            return []
        
        print(f"\n🚨 {len(shelter_events)} EVENTS REQUIRING SHELTER RESPONSE:")
        print("-" * 60)
        
        for i, event in enumerate(shelter_events, 1):
            print(f"\n{i}. {event['type']}")
            
            if event['type'] == 'WEATHER_EMERGENCY':
                print(f"   Event: {event['event']}")
                print(f"   Area: {event['area']}")
                print(f"   Severity: {event['severity']}")
                if event.get('expires'):
                    print(f"   Expires: {event['expires']}")
            
            elif event['type'] == 'EARTHQUAKE':
                print(f"   Magnitude: {event['magnitude']}")
                print(f"   Location: {event['location']}")
                print(f"   Time: {event['time']}")
            
            elif event['type'] == 'WILDFIRE':
                print(f"   Fire Intensity: {event['frp']} MW")
                print(f"   Confidence: {event['confidence']}%")
                print(f"   Detection: {event['detection_time']}")
            
            print(f"   📍 Coordinates: {event['lat']:.3f}, {event['lon']:.3f}")
        
        # Save deployment data
        if shelter_events:
            df = pd.DataFrame(shelter_events)
            df.to_csv('red_cross_deployments.csv', index=False)
            print(f"\n💾 Deployment data saved to red_cross_deployments.csv")
        
        return shelter_events

    def create_deployment_map(self, events):
        """Create map for Red Cross deployment planning"""
        if not events:
            print("No events to map")
            return
        
        # Center map on CONUS
        m = folium.Map(location=[39.8, -98.6], zoom_start=4)
        
        for event in events:
            # Color by event type
            if event['type'] == 'WEATHER_EMERGENCY':
                color = 'red'
                icon = '🌪️'
            elif event['type'] == 'EARTHQUAKE':
                color = 'orange'
                icon = '🌍'
            elif event['type'] == 'WILDFIRE':
                color = 'darkred'
                icon = '🔥'
            
            # Create popup with deployment info
            popup_text = f"""
            <b>{icon} {event['type']}</b><br>
            <b>SHELTER REQUIRED</b><br>
            Coordinates: {event['lat']:.3f}, {event['lon']:.3f}
            """
            
            if event['type'] == 'WEATHER_EMERGENCY':
                popup_text += f"<br>Event: {event['event']}<br>Area: {event['area']}"
            elif event['type'] == 'EARTHQUAKE':
                popup_text += f"<br>Magnitude: {event['magnitude']}<br>Location: {event['location']}"
            elif event['type'] == 'WILDFIRE':
                popup_text += f"<br>Intensity: {event['frp']} MW"
            
            folium.CircleMarker(
                location=[event['lat'], event['lon']],
                radius=12,
                color='white',
                weight=3,
                fill=True,
                fillColor=color,
                fillOpacity=0.8,
                popup=popup_text
            ).add_to(m)
        
        # Add title
        title_html = f"""
        <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                    z-index:9999; background: #d32f2f; color: white; 
                    padding: 15px; border-radius: 8px; font-family: Arial; font-weight: bold;">
        🏠 RED CROSS SHELTER DEPLOYMENT MAP - {len(events)} ACTIVE EVENTS
        </div>
        """
        m.get_root().html.add_child(folium.Element(title_html))
        
        m.save('red_cross_deployment_map.html')
        print(f"🗺️ Deployment map saved to red_cross_deployment_map.html")

if __name__ == "__main__":
    tool = RedCrossDisasterTool()
    events = tool.generate_shelter_deployment_report()
    if events:
        tool.create_deployment_map(events)