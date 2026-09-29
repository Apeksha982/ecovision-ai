# EcoVision

AI-Powered Freshwater Observation Assistant

**Live app:** https://ecovision-ai-fmynjycpxdojbugm25x8z5.streamlit.app/

## Problem
Citizens see local streams and creeks all the time, but a photo alone can't be counted, compared, or tracked. Turning photos into structured, reviewable observations is hard.

## Solution
EcoVision lets a person upload a photo of a freshwater site. A vision-language model (Google Gemini) lists visible indicators (litter, water discoloration, algae-like growth, erosion, vegetation stress, blockage), each with a status, a model-reported confidence, and a one-sentence explanation. The person confirms or rejects each item before it is saved. Confirmed observations feed a dashboard and a repeat-observation alert.

## Features
- AI photo analysis with explanations ("Why" for every indicator)
- "Cannot determine" option, so the AI can admit when it can't tell
- Human-in-the-loop verification (confirm / reject / not sure)
- Dashboard: totals, AI flags vs human confirmations, recent observations
- Alerts: flags sites with repeated human-confirmed observations

## How it works
Citizen uploads photo -> AI analysis -> explanation + confidence -> human verification -> saved observation -> dashboard -> alert -> human follow-up

## Responsible AI
- EcoVision reports only *visible indicators*, never water safety or pollution.
- Confidence scores are model-reported and not calibrated.
- Only human-confirmed observations trigger alerts.
- Not a laboratory measurement or regulatory determination.

## Tech
Python, Streamlit, Pandas, Pillow, Google Gemini API

## Run locally
```
pip install -r requirements.txt

streamlit run app.py
```

## Limitations and future work
- Observations are stored in a CSV file; a production version would use a shared database.
- Sites are matched by name; a production version would use map coordinates.
- Not validated against expert-labelled data.

## Author
Apeksha paudel
