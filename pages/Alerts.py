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

st.set_page_config(page_title="EcoVision Alerts", page_icon="⚠️")
st.title("⚠️ Alerts")
st.caption("Places with repeated human-confirmed observations. Human review is recommended before any action.")

if not os.path.exists(CSV_PATH):
    st.warning("No observations yet. Save some observations on the main page first.")
    st.stop()

df = pd.read_csv(CSV_PATH)
df["timestamp"] = pd.to_datetime(df["timestamp"])
df["site"] = df["location"].astype(str).str.strip().str.lower()

days = st.slider("Look back (days)", 1, 60, 14)
min_reports = st.slider("Minimum confirmed reports to flag a site", 2, 5, 2)

cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
recent = df[df["timestamp"] >= cutoff]

found = []
for site, g in recent.groupby("site"):
    for key, label in INDICATORS.items():
        n = int(((g[f"{key}_ai"] == "possible") & (g[f"{key}_human"] == "confirm")).sum())
        if n >= min_reports:
            found.append((site.title(), label, n, len(g), g["timestamp"].max()))

if not found:
    st.success(f"No repeated observations in the last {days} days.")
else:
    st.warning(f"{len(found)} possible recurring issue(s) detected.")
    for site, label, n, total, last in found:
        with st.container(border=True):
            st.markdown(f"**⚠️ {site}**: possible recurring issue: **{label}**")
            st.write(f"{n} human-confirmed reports in the last {days} days ({total} observations at this site). Latest: {last:%b %d, %Y}.")
            st.caption("Human review / field verification recommended. This is not a finding of pollution.")

st.subheader("Observations per site")
counts = recent.groupby("site").size().rename("Observations").to_frame()
st.bar_chart(counts)
