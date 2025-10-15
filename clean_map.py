import pandas as pd
import folium

def make_clean_map(csv_file="combined_disaster_feed.csv", output_file="clean_map.html"):
    """
    Clean, honest presentation of real disaster data.
    No BS risk scores or fake intelligence - just the facts.
    """
    df = pd.read_csv(csv_file)
    df = df.dropna(subset=["lat", "lon"])
    
    # Simple, clear colors by source
    colors = {"NOAA": "red", "USGS": "orange", "NASA-FIRMS": "darkred"}
    
    m = folium.Map(location=[38, -97], zoom_start=5, tiles="OpenStreetMap")
    
    # Group by source for toggle
    groups = {
        "NOAA": folium.FeatureGroup(name="NOAA Weather Alerts"),
        "USGS": folium.FeatureGroup(name="USGS Earthquakes"), 
        "NASA-FIRMS": folium.FeatureGroup(name="NASA Fire Detections")
    }
    
    for _, row in df.iterrows():
        source = row.get("source", "Unknown")
        
        # Build popup with actual data only
        popup_parts = [f"<b>{source}</b>"]
        
        if source == "NOAA":
            popup_parts.append(f"Event: {row.get('event', 'N/A')}")
            if pd.notna(row.get('severity')):
                popup_parts.append(f"Severity: {row['severity']}")
            if pd.notna(row.get('area')):
                popup_parts.append(f"Area: {row['area']}")
                
        elif source == "USGS":
            popup_parts.append(f"Magnitude: {row.get('magnitude', 'N/A')}")
            if pd.notna(row.get('place')):
                popup_parts.append(f"Location: {row['place']}")
                
        elif source == "NASA-FIRMS":
            popup_parts.append("Wildfire Detection")
            if pd.notna(row.get('confidence')):
                popup_parts.append(f"Confidence: {row['confidence']}%")
        
        popup_parts.append(f"Coordinates: {row['lat']:.3f}, {row['lon']:.3f}")
        popup_text = "<br>".join(popup_parts)
        
        marker = folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6,
            color=colors.get(source, "gray"),
            fill=True,
            fillColor=colors.get(source, "gray"),
            fillOpacity=0.7,
            popup=popup_text
        )
        
        if source in groups:
            marker.add_to(groups[source])
        else:
            marker.add_to(m)
    
    # Add groups to map
    for group in groups.values():
        group.add_to(m)
    
    # Simple header with real counts
    noaa_count = len(df[df['source'] == 'NOAA'])
    usgs_count = len(df[df['source'] == 'USGS']) 
    fire_count = len(df[df['source'] == 'NASA-FIRMS'])
    
    header = f"""
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
                z-index:9999; background: white; padding: 10px; border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2); font-family: Arial;">
        <h3 style="margin: 0;">Real-Time Disaster Data</h3>
        <div style="font-size: 14px; margin-top: 5px;">
            {noaa_count} Weather Alerts • {usgs_count} Earthquakes • {fire_count} Fire Detections
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(header))
    
    # Simple legend
    legend = """
    <div style="position: fixed; bottom: 20px; left: 20px; background: white;
                padding: 10px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        <div><span style="color: red;">●</span> NOAA Weather</div>
        <div><span style="color: orange;">●</span> USGS Earthquakes</div>
        <div><span style="color: darkred;">●</span> NASA Fires</div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend))
    
    folium.LayerControl().add_to(m)
    
    m.save(output_file)
    print(f"✅ Clean map saved: {output_file}")
    print(f"📊 Real data: {noaa_count} weather + {usgs_count} earthquakes + {fire_count} fires")

if __name__ == "__main__":
    make_clean_map()