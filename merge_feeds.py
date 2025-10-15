import pandas as pd
import os

files = ["noaa_alerts.csv", "usgs_earthquakes.csv", "wildfires.csv"]
dfs = [pd.read_csv(f) for f in files if os.path.exists(f)]
merged = pd.concat(dfs, ignore_index=True)
print(f"✅ Merged {sum(len(df) for df in dfs)} records")

merged.to_csv("combined_disaster_feed.csv", index=False)