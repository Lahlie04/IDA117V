"""Reusable inference helpers for the saved IDA117V model."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd

from prepare_data import build_input_row, encode_lightgbm

BUNDLE_PATH = Path(__file__).resolve().with_name("final_model.joblib")


def load_bundle(path: Path | str = BUNDLE_PATH) -> dict:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Saved model not found: {path}. Run 03_Code/run_analysis.py first.")
    return joblib.load(path)


def predict_frame(frame: pd.DataFrame, bundle: dict | None = None) -> pd.DataFrame:
    bundle = bundle or load_bundle()
    encoded = encode_lightgbm(
        frame,
        bundle["category_maps"],
        bundle["categorical_features"],
        bundle["numeric_features"],
    )
    probability = bundle["model"].predict_proba(encoded)[:, 1]
    prediction = (probability >= bundle["threshold"]).astype(np.int8)
    output = frame.copy()
    output["probability_at_risk"] = probability
    output["prediction_at_risk"] = prediction
    return output


def explain_frame(frame: pd.DataFrame, bundle: dict | None = None, top_n: int = 3) -> list[tuple[str, float]]:
    bundle = bundle or load_bundle()
    encoded = encode_lightgbm(
        frame,
        bundle["category_maps"],
        bundle["categorical_features"],
        bundle["numeric_features"],
    )
    contributions = bundle["model"].predict(encoded, pred_contrib=True)[0][:-1]
    names = bundle["categorical_features"] + bundle["numeric_features"]
    indexes = np.argsort(-np.abs(contributions))[:top_n]
    return [(names[index], float(contributions[index])) for index in indexes]


def predict_single(
    created_date: dt.date,
    sub_council: str,
    ward: str,
    suburb: str,
    complaint_type: str,
    work_center: str,
    coordinate_state: str,
    bundle: dict | None = None,
) -> Tuple[pd.DataFrame, list[tuple[str, float]]]:
    frame = build_input_row(
        created_date, sub_council, ward, suburb, complaint_type, work_center, coordinate_state
    )
    return predict_frame(frame, bundle), explain_frame(frame, bundle)
