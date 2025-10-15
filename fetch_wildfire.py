import requests
import pandas as pd
from io import StringIO

def fetch_active_wildfires():
    """
    Fetch current U.S. wildfires using NASA FIRMS API
    """
    # NASA FIRMS API requires registration but has a public endpoint for recent data
    url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/csv/MODIS_C6_1_USA_contiguous_and_Hawaii_24h.csv"
    
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        df = pd.read_csv(StringIO(r.text))
        
        # Rename columns to match our schema
        df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
        df["source"] = "NASA-FIRMS"
        df["event"] = "Wildfire"
        
        # Create datetime from date and time
        if "acq_date" in df.columns and "acq_time" in df.columns:
            df["acq_datetime"] = pd.to_datetime(df["acq_date"] + " " + df["acq_time"].astype(str).str.zfill(4))
        
        # Filter out oceanic false positives (rough continental US bounds)
        # Exclude fires in Atlantic, Gulf of Mexico, Pacific
        df = df[
            (df["lat"] >= 24.0) & (df["lat"] <= 49.0) &  # Continental US latitude range
            (df["lon"] >= -125.0) & (df["lon"] <= -66.0)  # Continental US longitude range
        ]
        
        # Additional filter: exclude fires too far from shore (likely offshore platforms/artifacts)
        # Remove fires in major water bodies
        gulf_mexico = (df["lat"] >= 24.0) & (df["lat"] <= 30.5) & (df["lon"] >= -98.0) & (df["lon"] <= -80.5)
        atlantic_coast = (df["lat"] >= 25.0) & (df["lat"] <= 35.0) & (df["lon"] >= -81.0) & (df["lon"] <= -75.0)
        
        # Keep only land-based fires (exclude obvious water areas)
        df = df[~(gulf_mexico | atlantic_coast)]
        
        # Select relevant columns
        available_cols = ["source", "event", "acq_datetime", "lat", "lon"]
        if "brightness" in df.columns:
            available_cols.append("brightness")
        if "confidence" in df.columns:
            available_cols.append("confidence")
        if "frp" in df.columns:
            available_cols.append("frp")
            
        df = df[[col for col in available_cols if col in df.columns]]
        return df
        
    except requests.exceptions.HTTPError:
        # Fallback: create sample data structure for testing
        print("⚠️  NASA FIRMS API unavailable, creating sample data structure")
        return pd.DataFrame(columns=["source", "event", "acq_datetime", "lat", "lon", "brightness", "confidence", "frp"])

if __name__ == "__main__":
    df = fetch_active_wildfires()
    print(f"🔥 {len(df)} wildfire detections retrieved")
    df.to_csv("wildfires.csv", index=False)