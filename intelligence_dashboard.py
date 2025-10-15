import pandas as pd
import folium
from folium import plugins
import json
from datetime import datetime

def create_intelligence_dashboard():
    """Create unified dashboard combining disaster data with news intelligence"""
    
    # Load all data sources
    disasters = pd.read_csv('combined_disaster_feed.csv')
    
    try:
        news_data = pd.read_csv('disaster_news_feed.csv')
        correlations = pd.read_csv('news_disaster_correlations.csv')
        has_news = True
    except:
        news_data = pd.DataFrame()
        correlations = pd.DataFrame()
        has_news = False
    
    # Create enhanced map
    m = folium.Map(location=[38, -97], zoom_start=4, tiles="CartoDB positron")
    
    # Add disaster markers with news correlation indicators
    for _, row in disasters.iterrows():
        coords = f"{row['lat']}, {row['lon']}"
        
        # Check if this disaster has news coverage
        related_news = []
        if has_news and not correlations.empty:
            related_news = correlations[correlations['disaster_coords'] == coords]
        
        # Color based on news coverage + disaster type
        if len(related_news) > 0:
            color = 'purple'  # Has news coverage
            marker_size = 10
        elif row['source'] == 'NOAA':
            color = 'red'
            marker_size = 7
        elif row['source'] == 'USGS':
            color = 'orange'
            marker_size = 6
        else:
            color = 'darkred'
            marker_size = 5
        
        # Enhanced popup with news integration
        popup_html = f"""
        <div style="width: 350px; font-family: Arial;">
            <h4 style="color: {color}; margin: 0;">
                🚨 {row['source']} - {row.get('event', 'Event')}
            </h4>
            <hr style="margin: 5px 0;">
            <table style="width: 100%; font-size: 12px;">
                <tr><td><b>Location:</b></td><td>{row.get('area', row.get('place', 'Unknown'))}</td></tr>
                <tr><td><b>Coordinates:</b></td><td>{row['lat']:.3f}, {row['lon']:.3f}</td></tr>
        """
        
        # Add source-specific data
        if row['source'] == 'USGS':
            popup_html += f"<tr><td><b>Magnitude:</b></td><td>{row.get('magnitude', 'N/A')}</td></tr>"
        elif row['source'] == 'NOAA':
            popup_html += f"<tr><td><b>Severity:</b></td><td>{row.get('severity', 'N/A')}</td></tr>"
        elif row['source'] == 'NASA-FIRMS':
            popup_html += f"<tr><td><b>Confidence:</b></td><td>{row.get('confidence', 'N/A')}%</td></tr>"
        
        popup_html += "</table>"
        
        # Add news intelligence section
        if len(related_news) > 0:
            popup_html += f"""
            <hr style="margin: 10px 0;">
            <h5 style="color: purple; margin: 5px 0;">📰 NEWS INTELLIGENCE ({len(related_news)} reports)</h5>
            """
            for _, news in related_news.head(3).iterrows():
                popup_html += f"""
                <div style="margin: 5px 0; padding: 5px; background: #f0f0f0; border-radius: 3px; font-size: 11px;">
                    <b>{news['news_source']}</b><br>
                    <a href="{news['news_url']}" target="_blank">{news['news_title'][:60]}...</a>
                </div>
                """
        
        popup_html += "</div>"
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=marker_size,
            color='white',
            weight=2,
            fill=True,
            fillColor=color,
            fillOpacity=0.8,
            popup=folium.Popup(popup_html, max_width=370)
        ).add_to(m)
    
    # Add news-only markers for stories without precise coordinates
    if has_news and not news_data.empty:
        news_locations = []  # You could geocode news locations here
    
    # Intelligence header
    news_count = len(news_data) if has_news else 0
    correlation_count = len(correlations) if has_news else 0
    
    header_html = f"""
    <div style="position: fixed; top: 10px; left: 10px; right: 10px; z-index:9999; 
                background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%); 
                color: white; padding: 20px; border-radius: 12px; 
                box-shadow: 0 8px 25px rgba(0,0,0,0.3); font-family: Arial;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h2 style="margin: 0; font-size: 20px;">🌐 Disaster Intelligence Command Center</h2>
                <p style="margin: 8px 0 0 0; font-size: 13px; opacity: 0.9;">
                    Multi-Source Intelligence Fusion | Updated: {datetime.now().strftime('%H:%M UTC')}
                </p>
            </div>
            <div style="text-align: right;">
                <div style="font-size: 28px; font-weight: bold; color: #ffeb3b;">{len(disasters)}</div>
                <div style="font-size: 12px;">Active Disasters</div>
            </div>
        </div>
        <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-top: 20px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.3);">
            <div style="text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #ff5722;">{len(disasters[disasters['source'] == 'NOAA'])}</div>
                <div style="font-size: 11px;">Weather Alerts</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #ff9800;">{len(disasters[disasters['source'] == 'USGS'])}</div>
                <div style="font-size: 11px;">Earthquakes</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #f44336;">{len(disasters[disasters['source'] == 'NASA-FIRMS'])}</div>
                <div style="font-size: 11px;">Wildfires</div>
            </div>
            <div style="text-align: center;">
                <div style="font-size: 22px; font-weight: bold; color: #9c27b0;">{correlation_count}</div>
                <div style="font-size: 11px;">News Links</div>
            </div>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(header_html))
    
    # Enhanced legend
    legend_html = f"""
    <div style="position: fixed; bottom: 20px; left: 20px; width: 220px; z-index:9999; 
                background: rgba(255,255,255,0.95); border: 1px solid #ddd; border-radius: 8px;
                padding: 15px; font-family: Arial; font-size: 12px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);">
        <h4 style="margin: 0 0 12px 0; color: #333;">Intelligence Legend</h4>
        <div style="margin: 6px 0;"><span style="color: purple;">●</span> <b>News Coverage</b> - Disaster with media reports</div>
        <div style="margin: 6px 0;"><span style="color: red;">●</span> <b>NOAA Alerts</b> - Weather emergencies</div>
        <div style="margin: 6px 0;"><span style="color: orange;">●</span> <b>USGS Quakes</b> - Earthquake activity</div>
        <div style="margin: 6px 0;"><span style="color: darkred;">●</span> <b>NASA Fires</b> - Wildfire detections</div>
        <hr style="margin: 12px 0;">
        <div style="font-size: 10px; color: #666; line-height: 1.3;">
            <b>Intelligence Sources:</b><br>
            • {news_count} news reports monitored<br>
            • {correlation_count} disaster-news correlations<br>
            • RSS feeds from major outlets<br>
            • Reddit social monitoring
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Add full screen
    plugins.Fullscreen().add_to(m)
    
    m.save('intelligence_dashboard.html')
    print(f"🎯 Intelligence dashboard created with {len(disasters)} disasters and {correlation_count} news correlations")

if __name__ == "__main__":
    create_intelligence_dashboard()