import io
import json
import time
import os
from datetime import datetime

import pandas as pd
import streamlit as st
from google import genai
from google.genai import types
from PIL import Image

CSV_PATH = "data/observations.csv"
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.6-flash", "gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-3.1-flash-lite"]
INDICATORS = {
    "litter": "Litter",
    "water_discoloration": "Water discoloration",
    "algae_like_growth": "Algae-like growth",
    "erosion": "Erosion",
    "vegetation_stress": "Vegetation stress",
    "blockage": "Blockage",
}

PROMPT = """You help citizen scientists document freshwater sites.
Look at the photo and report ONLY visible indicators.
Never say the water is safe, unsafe, toxic or polluted.

For each of these indicators: litter, water_discoloration, algae_like_growth,
erosion, vegetation_stress, blockage, return:
- status: "possible", "none_obvious", or "cannot_determine"
- confidence: integer 0-100 (how sure you are of that status)
- reason: one sentence naming what you actually see in the image

Return ONLY valid JSON, no markdown:
{"indicators": {"litter": {"status": "", "confidence": 0, "reason": ""}, ...},
 "summary": "2 sentences, cautious wording, say a human should verify"}"""

DISCLAIMER = (
    "EcoVision gives AI-assisted visual observations for citizen science. "
    "Results are not laboratory water-quality measurements or regulatory "
    "determinations. A human should verify observations before any action."
)


def prepare_image(uploaded_file) -> bytes:
    img = Image.open(uploaded_file).convert("RGB")
    img.thumbnail((1280, 1280))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def analyze(image_bytes: bytes) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    last_err = None
    for model in MODELS:
        for attempt in range(2):
            try:
                resp = client.models.generate_content(
                    model=model,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
                        PROMPT,
                    ],
                    config=types.GenerateContentConfig(response_mime_type="application/json"),
                )
                text = resp.text.strip()
                text = text.replace("```json", "").replace("```", "").strip()
                return json.loads(text)
            except Exception as e:
                last_err = e
                msg = str(e)
                if "503" in msg or "429" in msg:
                    time.sleep(2)   # busy: retry once, then move to next model
                    continue
                if "404" in msg:
                    break           # model not available: next model
                raise
    raise last_err


def save_observation(location: str, result: dict, verdicts: dict):
    row = {"timestamp": datetime.now().isoformat(timespec="seconds"),
           "location": location, "summary": result.get("summary", "")}
    for key in INDICATORS:
        ind = result["indicators"].get(key, {})
        row[f"{key}_ai"] = ind.get("status", "cannot_determine")
        row[f"{key}_conf"] = ind.get("confidence", 0)
        row[f"{key}_human"] = verdicts.get(key, "not_reviewed")
    os.makedirs("data", exist_ok=True)
    df = pd.DataFrame([row])
    df.to_csv(CSV_PATH, mode="a", header=not os.path.exists(CSV_PATH), index=False)


st.set_page_config(page_title="EcoVision", page_icon="")
st.title(" EcoVision")
st.caption("AI Freshwater Observation Assistant")
st.info(DISCLAIMER)

photo = st.file_uploader("Upload a photo of a freshwater site", type=["jpg", "jpeg", "png"])
location = st.text_input("Observation location", placeholder="e.g. Brandywine Creek, Site A")

if photo:
    st.image(photo, use_container_width=True)

if photo and st.button("Analyze photo", type="primary"):
    with st.spinner("Analyzing..."):
        try:
            st.session_state["result"] = analyze(prepare_image(photo))
            st.session_state["saved"] = False
        except Exception as e:
            st.error(f"Analysis failed: {e}")

result = st.session_state.get("result")
if result:
    st.subheader("AI observations")
    st.write(result.get("summary", ""))

    verdicts = {}
    for key, label in INDICATORS.items():
        ind = result["indicators"].get(key, {})
        status = ind.get("status", "cannot_determine")
        conf = ind.get("confidence", 0)
        with st.container(border=True):
            st.markdown(f"**{label}** — {status.replace('_', ' ')} ({conf}%)")
            st.caption(f"Why: {ind.get('reason', '')}")
            verdicts[key] = st.radio(
                "Does this look correct?",
                ["confirm", "reject", "not sure"],
                key=f"v_{key}", horizontal=True, index=2,
            )

    if st.button("Save verified observation"):
        if not location.strip():
            st.warning("Please enter a location first.")
        else:
            save_observation(location.strip(), result, verdicts)
            st.session_state["saved"] = True

    if st.session_state.get("saved"):
        st.success("Observation saved.")
