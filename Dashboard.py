import os

import pandas as pd
import streamlit as st

CSV_PATH = "data/observations.csv"
INDICATORS = {
    "litter": "Litter",
    "water_discoloration": "Water discoloration",
    "algae_like_growth": "Algae-like growth",
    "erosion": "Erosion",
    "vegetation_stress": "Vegetation stress",
    "blockage": "Blockage",
}

st.set_page_config(page_title="EcoVision Dashboard", page_icon="🌎")
st.title("🌎 Environmental Dashboard")
st.caption("Citizen observations. AI-assisted, human-verified, not lab measurements.")

if not os.path.exists(CSV_PATH):
    st.warning("No observations yet. Go to the main page, analyze a photo, and save an observation.")
    st.stop()

df = pd.read_csv(CSV_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])

for key in INDICATORS:
    df[f"{key}_found"] = (df[f"{key}_ai"] == "possible") & (df[f"{key}_human"] == "confirm")

confirmed_total = int(sum(df[f"{k}_found"].sum() for k in INDICATORS))

c1, c2, c3 = st.columns(3)
c1.metric("Total observations", len(df))
c2.metric("Locations", df["location"].nunique())
c3.metric("Human-confirmed findings", confirmed_total)

st.subheader("AI flags vs human confirmations")
chart_df = pd.DataFrame({
    "AI flagged 'possible'": {label: int((df[f"{k}_ai"] == "possible").sum())
                              for k, label in INDICATORS.items()},
    "Human confirmed": {label: int(df[f"{k}_found"].sum())
                        for k, label in INDICATORS.items()},
})
st.bar_chart(chart_df)

st.subheader("Recent observations")
recent = df.sort_values("timestamp", ascending=False).head(10).copy()
recent["Confirmed findings"] = recent.apply(
    lambda r: ", ".join(label for k, label in INDICATORS.items() if r[f"{k}_found"]) or "none",
    axis=1,
)
st.dataframe(
    recent[["timestamp", "location", "Confirmed findings", "summary"]],
    use_container_width=True,
    hide_index=True,
)
