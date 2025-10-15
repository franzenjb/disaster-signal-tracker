import pandas as pd
import folium

def make_map(csv_file="combined_disaster_feed.csv", output_file="disaster_map.html"):
    """
    Build an interactive map from your combined disaster feed.
    Automatically color-codes events by source and saves as HTML.
    """
    df = pd.read_csv(csv_file)

    if df.empty:
        print("⚠️ No data found in file:", csv_file)
        return

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

    # Add markers by source
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

        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=6,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.8,
            popup=popup_text
        ).add_to(m)

    # Add title
    title_html = '''
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%);
         z-index:9999; background-color:white; padding:6px 12px; border-radius:8px;
         box-shadow:0 0 8px rgba(0,0,0,0.3); font-size:16px;">
    <b>🌐 American Red Cross – Live Disaster Feed (NOAA | USGS | NASA)</b>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Add a layer toggle (optional if you later add more)
    folium.LayerControl().add_to(m)

    # Save
    m.save(output_file)
    print(f"✅ Map saved to {output_file}")

if __name__ == "__main__":
    make_map()