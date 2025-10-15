import pandas as pd
import folium
from folium import plugins
import numpy as np
from risk_engine import DisasterRiskEngine

def create_professional_map(csv_file="combined_disaster_feed.csv", output_file="professional_map.html"):
    """
    Create a professional disaster intelligence map with advanced features
    """
    # Load and enrich data
    df = pd.read_csv(csv_file)
    df = DisasterRiskEngine.enrich_disaster_data(df)
    df = df.dropna(subset=["lat", "lon"])
    
    if df.empty:
        print("⚠️ No valid data found")
        return
    
    # Create base map with satellite and street views
    m = folium.Map(
        location=[38, -97], 
        zoom_start=5,
        tiles=None
    )
    
    # Add multiple tile layers
    folium.TileLayer('CartoDB positron', name='Light Mode').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='Dark Mode').add_to(m)
    folium.TileLayer('OpenStreetMap', name='Street View').add_to(m)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='ESRI Satellite',
        name='Satellite'
    ).add_to(m)
    
    # Risk-based color mapping
    risk_colors = {
        'LOW': '#28a745',      # Green
        'MODERATE': '#ffc107', # Yellow
        'HIGH': '#fd7e14',     # Orange
        'EXTREME': '#dc3545'   # Red
    }
    
    # Size based on threat score
    def get_marker_size(threat_score):
        if threat_score >= 70:
            return 12
        elif threat_score >= 50:
            return 9
        elif threat_score >= 30:
            return 7
        else:
            return 5
    
    # Create feature groups by risk level
    groups = {}
    for risk in ['LOW', 'MODERATE', 'HIGH', 'EXTREME']:
        groups[risk] = folium.FeatureGroup(name=f"{risk} Risk Events")
    
    # Add markers with enhanced popups
    for _, row in df.iterrows():
        risk = row.get('risk_level', 'LOW')
        color = risk_colors.get(risk, '#6c757d')
        
        # Enhanced popup with professional styling
        popup_html = f"""
        <div style="font-family: Arial, sans-serif; width: 300px;">
            <h4 style="margin: 0; color: {color}; border-bottom: 2px solid {color}; padding-bottom: 5px;">
                🚨 {row.get('source', 'Unknown')} Alert
            </h4>
            <table style="width: 100%; margin-top: 10px; font-size: 12px;">
                <tr><td><b>Event:</b></td><td>{row.get('event', 'N/A')}</td></tr>
                <tr><td><b>Risk Level:</b></td><td><span style="color: {color}; font-weight: bold;">{risk}</span></td></tr>
                <tr><td><b>Threat Score:</b></td><td>{row.get('threat_score', 0)}/100</td></tr>
                <tr><td><b>Impact Radius:</b></td><td>{row.get('impact_radius_km', 0):.1f} km</td></tr>
        """
        
        # Add source-specific data
        if row.get('source') == 'USGS':
            popup_html += f"<tr><td><b>Magnitude:</b></td><td>{row.get('magnitude', 'N/A')}</td></tr>"
            popup_html += f"<tr><td><b>Location:</b></td><td>{row.get('place', 'N/A')}</td></tr>"
        elif row.get('source') == 'NOAA':
            popup_html += f"<tr><td><b>Severity:</b></td><td>{row.get('severity', 'N/A')}</td></tr>"
            popup_html += f"<tr><td><b>Area:</b></td><td>{row.get('area', 'N/A')}</td></tr>"
        elif row.get('source') == 'NASA-FIRMS':
            popup_html += f"<tr><td><b>Confidence:</b></td><td>{row.get('confidence', 'N/A')}%</td></tr>"
            popup_html += f"<tr><td><b>Brightness:</b></td><td>{row.get('brightness', 'N/A')}K</td></tr>"
        
        popup_html += f"""
                <tr><td><b>Urgency:</b></td><td>{row.get('urgency', 'N/A')}</td></tr>
                <tr><td><b>Coordinates:</b></td><td>{row['lat']:.3f}, {row['lon']:.3f}</td></tr>
            </table>
        </div>
        """
        
        # Create marker with impact radius circle
        marker = folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=get_marker_size(row.get('threat_score', 0)),
            color='white',
            weight=2,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            popup=folium.Popup(popup_html, max_width=320)
        )
        
        # Add impact radius circle for high-risk events
        if row.get('threat_score', 0) >= 50:
            folium.Circle(
                location=[row["lat"], row["lon"]],
                radius=row.get('impact_radius_km', 10) * 1000,  # Convert to meters
                color=color,
                weight=1,
                fill=True,
                fillOpacity=0.1
            ).add_to(groups[risk])
        
        marker.add_to(groups[risk])
    
    # Add all groups to map
    for group in groups.values():
        group.add_to(m)
    
    # Add heat map layer for threat density
    heat_data = [[row['lat'], row['lon'], row.get('threat_score', 10)/10] 
                 for _, row in df.iterrows()]
    
    heat_map = plugins.HeatMap(
        heat_data,
        name='Threat Density Heat Map',
        radius=25,
        blur=15,
        gradient={0.2: 'blue', 0.4: 'cyan', 0.6: 'lime', 0.8: 'yellow', 1.0: 'red'}
    )
    heat_map.add_to(m)
    
    # Add marker clustering for better performance
    marker_cluster = plugins.MarkerCluster(name='Clustered View').add_to(m)
    
    # Professional header with real-time stats
    high_risk_count = len(df[df['risk_level'].isin(['HIGH', 'EXTREME'])])
    avg_threat = df['threat_score'].mean()
    
    header_html = f"""
    <div style="position: fixed; top: 10px; left: 10px; right: 10px; z-index:9999; 
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                color: white; padding: 15px; border-radius: 10px; 
                box-shadow: 0 4px 15px rgba(0,0,0,0.3); font-family: Arial, sans-serif;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; font-size: 18px;">🌐 Disaster Intelligence Center</h2>
                <p style="margin: 5px 0 0 0; font-size: 12px; opacity: 0.9;">
                    Real-time Multi-Source Threat Assessment | Last Updated: {pd.Timestamp.now().strftime('%H:%M UTC')}
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 24px; font-weight: bold; color: #ffeb3b;">{len(df)}</div>
                <div style="font-size: 11px;">Active Events</div>
            </div>
        </div>
        <div style="display: flex; justify-content: space-around; margin-top: 15px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.3);">
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #ff5722;">{high_risk_count}</div>
                <div style="font-size: 10px;">High Risk</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #ffc107;">{avg_threat:.1f}</div>
                <div style="font-size: 10px;">Avg Threat</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 20px; font-weight: bold; color: #4caf50;">{len(df[df['urgency'] == 'IMMEDIATE'])}</div>
                <div style="font-size: 10px;">Immediate</div>
            </div>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(header_html))
    
    # Add professional legend
    legend_html = """
    <div style="position: fixed; bottom: 20px; left: 20px; width: 200px; z-index:9999; 
                background: rgba(255,255,255,0.95); border: 1px solid #ccc; border-radius: 8px;
                padding: 15px; font-family: Arial, sans-serif; font-size: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 10px 0; color: #333;">Risk Assessment Legend</h4>
        <div style="margin: 5px 0;"><span style="color: #dc3545;">●</span> <b>EXTREME</b> - Immediate action required</div>
        <div style="margin: 5px 0;"><span style="color: #fd7e14;">●</span> <b>HIGH</b> - Monitor closely</div>
        <div style="margin: 5px 0;"><span style="color: #ffc107;">●</span> <b>MODERATE</b> - Standard monitoring</div>
        <div style="margin: 5px 0;"><span style="color: #28a745;">●</span> <b>LOW</b> - Routine awareness</div>
        <hr style="margin: 10px 0;">
        <div style="font-size: 10px; color: #666;">
            Circle size = Threat score<br>
            Impact radius shown for high-risk events
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add mini map
    minimap = plugins.MiniMap(toggle_display=True)
    m.add_child(minimap)
    
    # Add full screen button
    plugins.Fullscreen().add_to(m)
    
    # Save map
    m.save(output_file)
    print(f"🗺️ Professional disaster map saved to {output_file}")
    print(f"📊 Analyzed {len(df)} events with {high_risk_count} high-risk situations")

if __name__ == "__main__":
    create_professional_map()