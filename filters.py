import pandas as pd

def filter_data(df, source=None, event=None, severity=None):
    """
    Filter the combined dataset by source, event type, or severity.
    Returns a new filtered DataFrame.
    """
    out = df.copy()
    if source:
        out = out[out["source"].str.contains(source, case=False, na=False)]
    if event:
        out = out[out["event"].str.contains(event, case=False, na=False)]
    if severity and "severity" in out.columns:
        out = out[out["severity"].str.contains(severity, case=False, na=False)]
    return out