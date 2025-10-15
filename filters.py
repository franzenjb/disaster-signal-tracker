import pandas as pd
from datetime import datetime, timedelta

def filter_data(df, source=None, event=None, severity=None, hours_ago=None):
    """
    Filter the combined dataset by source, event type, severity, or time.
    Returns a new filtered DataFrame.
    """
    out = df.copy()
    if source:
        out = out[out["source"].str.contains(source, case=False, na=False)]
    if event:
        out = out[out["event"].str.contains(event, case=False, na=False)]
    if severity and "severity" in out.columns:
        out = out[out["severity"].str.contains(severity, case=False, na=False)]
    
    # Time filter
    if hours_ago and any(col in out.columns for col in ["time", "acq_datetime"]):
        now = datetime.now()
        cutoff = now - timedelta(hours=hours_ago)
        
        # Handle different time column names
        for time_col in ["time", "acq_datetime"]:
            if time_col in out.columns:
                out[time_col] = pd.to_datetime(out[time_col], errors='coerce')
                out = out[out[time_col] >= cutoff]
                break
    
    return out

def filter_last_24h(df):
    """Quick filter for last 24 hours"""
    return filter_data(df, hours_ago=24)

def filter_last_7d(df):
    """Quick filter for last 7 days"""
    return filter_data(df, hours_ago=168)  # 7 * 24