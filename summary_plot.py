# summary_plot.py
import pandas as pd
import plotly.express as px

def make_summary(csv_file="combined_disaster_feed.csv"):
    df = pd.read_csv(csv_file)
    df["source"] = df["source"].fillna("Unknown")
    count = df["source"].value_counts().reset_index()
    count.columns = ["source", "count"]

    fig = px.bar(count, x="source", y="count", color="source",
                 title="Active Disaster Events by Source",
                 text="count")
    fig.update_traces(textposition='outside')
    fig.write_html("summary.html")
    print("✅ Summary saved to summary.html")

if __name__ == "__main__":
    make_summary()