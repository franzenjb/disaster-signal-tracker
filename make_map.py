import pandas as pd
import folium
from filters import filter_data

def make_map(csv_file="combined_disaster_feed.csv", output_file="disaster_map.html"):
    """
    Build an interactive map from your combined disaster feed.
    Automatically color-codes events by source and saves as HTML.
    """
    df = pd.read_csv(csv_file)

    if df.empty:
        print("⚠️ No data found in file:", csv_file)
        return

    # Example: only show severe NOAA events
    # df = filter_data(df, source="NOAA", severity="Severe")
    
    # Handle missing coordinates safely
    df = df.dropna(subset=["lat", "lon"])

    # Define colors for sources
    colors = {
        "NOAA": "red",
        "USGS": "orange",
        "NASA-FIRMS": "darkred",
    }

    # Create map centered on the continental US
    m = folium.Map(location=[38, -97], zoom_start=5, tiles="CartoDB positron")

    # Create feature groups for each data source
    noaa_group = folium.FeatureGroup(name="NOAA Weather Alerts")
    usgs_group = folium.FeatureGroup(name="USGS Earthquakes") 
    fire_group = folium.FeatureGroup(name="NASA Wildfires")

    # Add markers by source to appropriate groups
    for _, row in df.iterrows():
        src = row.get("source", "Other")
        color = colors.get(src, "gray")
        event = row.get("event", "")
        desc_parts = []

        # Build popup text dynamically based on available columns
        for field in ["headline", "place", "area", "acq_datetime"]:
            if field in row and not pd.isna(row[field]):
                desc_parts.append(f"{field.title()}: {row[field]}")
        popup_text = f"<b>{src}</b> — {event}<br>" + "<br>".join(desc_parts)

        marker = folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=popup_text
        )
        
        # Add to appropriate group
        if src == "NOAA":
            marker.add_to(noaa_group)
        elif src == "USGS":
            marker.add_to(usgs_group)
        elif src == "NASA-FIRMS":
            marker.add_to(fire_group)
        else:
            marker.add_to(m)  # fallback for unknown sources

    # Add feature groups to map
    noaa_group.add_to(m)
    usgs_group.add_to(m)
    fire_group.add_to(m)

    # Add title with summary link
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
         z-index:9999; background-color:white; padding:6px 12px; border-radius:8px;
         box-shadow:0 0 8px rgba(0,0,0,0.3); font-size:16px;">
    <b>🌐 American Red Cross – Live Disaster Feed (NOAA | USGS | NASA)</b>
    <br><a href="sum.html" target="_blank" style="font-size:12px; color:#0066cc;">📊 View Summary Chart</a>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Add a layer toggle (optional if you later add more)
    folium.LayerControl().add_to(m)

    # Add legend
    legend_html = """
    <div style="position: fixed; 
         bottom: 30px; left: 20px; width: 160px; z-index:9999; 
         background-color:white; border:1px solid #444; border-radius:6px;
         padding:6px; font-size:13px;">
    <b>Legend</b><br>
    <span style="color:red;">●</span> NOAA Alerts<br>
    <span style="color:orange;">●</span> USGS Quakes<br>
    <span style="color:darkred;">●</span> Wildfires
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))

    # Save
    m.save(output_file)
    print(f"✅ Map saved to {output_file}")

if __name__ == "__main__":
    make_map()