"""Streamlit interface for seven-day municipal service-request risk triage."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import streamlit as st

from predict import explain_frame, load_bundle, predict_frame, predict_single
from prepare_data import FEATURES

st.set_page_config(page_title="Service Request Risk Triage", page_icon="🛠️", layout="centered")


@st.cache_resource
def cached_bundle():
    return load_bundle()


bundle = cached_bundle()
maps = bundle["category_maps"]

st.title("Municipal Service Request - Seven-Day Risk Triage")
st.caption("Educational decision support only: estimates the risk that a request will not be completed within seven calendar days.")

mode = st.radio("Input mode", ["Single request", "Batch CSV"], horizontal=True)

if mode == "Single request":
    with st.form("risk_form"):
        created_date = st.date_input("Request creation date", value=dt.date(2026, 5, 30))
        sub_council = st.selectbox("Sub-council", sorted(maps["Sub_Council"].keys()))
        ward = st.selectbox("Ward", sorted(maps["Ward"].keys()))
        suburb = st.selectbox("Suburb", sorted(maps["Suburb"].keys()))
        complaint = st.selectbox("Complaint type", sorted(maps["C3_Complaint_Type"].keys()))
        work_center = st.selectbox("Work centre", sorted(maps["Work_Center"].keys()))
        coordinate_state = st.radio("Coordinate quality", ["Available", "Missing", "Recorded as 0,0"], horizontal=True)
        submitted = st.form_submit_button("Assess risk", type="primary")

    if submitted:
        try:
            output, explanation = predict_single(
                created_date, sub_council, ward, suburb, complaint, work_center,
                coordinate_state, bundle,
            )
            probability = float(output.loc[0, "probability_at_risk"])
            prediction = int(output.loc[0, "prediction_at_risk"])
            if prediction:
                st.error(f"Review recommended - estimated non-completion risk: {probability:.1%}")
            else:
                st.success(f"Below review threshold - estimated non-completion risk: {probability:.1%}")
            st.write(f"Decision threshold: **{bundle['threshold']:.2f}**")
            st.write("Largest model-signal contributions (not causal explanations):")
            st.dataframe(pd.DataFrame(explanation, columns=["Feature", "Contribution"]), hide_index=True)
        except ValueError as error:
            st.error(str(error))
else:
    uploaded = st.file_uploader("Upload a CSV containing the documented model input columns", type=["csv"])
    if uploaded is not None:
        try:
            frame = pd.read_csv(uploaded)
            missing = [column for column in FEATURES if column not in frame.columns]
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
            output = predict_frame(frame[FEATURES], bundle)
            st.dataframe(output, use_container_width=True)
            st.download_button(
                "Download predictions",
                output.to_csv(index=False).encode("utf-8"),
                file_name="service_request_risk_predictions.csv",
                mime="text/csv",
            )
        except Exception as error:
            st.error(f"The batch file could not be scored: {error}")

with st.expander("Limitations and responsible use"):
    st.markdown(
        """
- This model was trained on a two-month historical extract and may not generalise to other periods.
- The seven-day horizon is a project assumption, not a confirmed service-level standard for every complaint type.
- The score must never be used to deny, close or automatically deprioritise a request.
- A human decision-maker must consider urgency, safety, vulnerability, service standards and operational capacity.
- Predictions show statistical associations, not causes.
- Do not enter names, phone numbers, email addresses, exact street addresses, credentials or free-text personal data.
- Suburb, ward and coordinate information may still be privacy-sensitive and must be handled under applicable governance requirements.
        """
    )

st.caption("Model source: committed assignment package. Load only the trusted joblib file supplied with this project.")
