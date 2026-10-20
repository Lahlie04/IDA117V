"""Data loading and leakage-safe feature preparation for IDA117V."""
from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Dict, Iterable, Tuple

import numpy as np
import pandas as pd

SEED = 42
PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA = PROJECT_ROOT / "02_Data" / "raw" / "Service_Requests_01_April_2026_until_30_May_2026.xlsx"

CAT_FEATURES = [
    "Sub_Council",
    "Ward",
    "Suburb",
    "C3_Complaint_Type",
    "Work_Center",
    "day_of_week",
]
NUM_FEATURES = ["day_index", "day_of_month", "is_weekend", "coord_missing", "coord_zero"]
FEATURES = CAT_FEATURES + NUM_FEATURES
TARGET = "risk_7d"

TRAIN_END = pd.Timestamp("2026-05-12")
VALIDATION_START = pd.Timestamp("2026-05-13")
VALIDATION_END = pd.Timestamp("2026-05-21")
TEST_START = pd.Timestamp("2026-05-22")
SUPPORTED_START = dt.date(2026, 4, 1)


def _clean_category(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    return cleaned.mask(cleaned.isna() | cleaned.eq(""), "Missing").astype(str)


def load_source(path: Path | str = RAW_DATA) -> pd.DataFrame:
    """Load the source workbook while preserving Ward and Sub_Council as labels."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(
            f"Source workbook not found: {path}. See 02_Data/raw/README.md for setup instructions."
        )
    return pd.read_excel(path, dtype={"Ward": "string", "Sub_Council": "string"})


def prepare_frame(source: pd.DataFrame) -> pd.DataFrame:
    """Create the target and creation-time features without using leakage fields."""
    df = source.copy()
    required = {
        "Sub_Council", "Ward", "Suburb", "C3_Complaint_Type", "Work_Center",
        "X_Y_Co_ordinate_1", "X_Y_Co_ordinate_2", "Created_On_Date", "Completed_Date",
    }
    missing = sorted(required.difference(df.columns))
    if missing:
        raise ValueError(f"Source data is missing required columns: {missing}")

    for column in ["Created_On_Date", "Changed_on", "Completed_Date"]:
        if column in df:
            df[column] = pd.to_datetime(df[column], errors="coerce", utc=True)

    df["created_local"] = df["Created_On_Date"].dt.tz_convert("Africa/Johannesburg")
    # A request without a creation timestamp cannot be assigned to the chronological protocol.
    df = df.loc[df["created_local"].notna()].copy()

    for column in CAT_FEATURES[:-1]:
        df[column] = _clean_category(df[column])

    local_day = df["created_local"].dt.floor("D").dt.tz_localize(None)
    df["day_of_week"] = local_day.dt.day_name()
    df["day_index"] = (local_day - pd.Timestamp(SUPPORTED_START)).dt.days.astype(np.float32)
    df["day_of_month"] = local_day.dt.day.astype(np.float32)
    df["is_weekend"] = (local_day.dt.dayofweek >= 5).astype(np.float32)

    coordinate_1 = pd.to_numeric(df["X_Y_Co_ordinate_1"], errors="coerce")
    coordinate_2 = pd.to_numeric(df["X_Y_Co_ordinate_2"], errors="coerce")
    df["coord_missing"] = (coordinate_1.isna() | coordinate_2.isna()).astype(np.float32)
    df["coord_zero"] = ((coordinate_1 == 0) & (coordinate_2 == 0)).astype(np.float32)

    duration_days = (
        (df["Completed_Date"] - df["Created_On_Date"]).dt.total_seconds() / 86_400
    )
    df[TARGET] = (~duration_days.between(0, 7, inclusive="both")).astype(np.int8)
    return df


def chronological_masks(df: pd.DataFrame) -> Dict[str, pd.Series]:
    local_day = df["created_local"].dt.floor("D").dt.tz_localize(None)
    return {
        "train": local_day <= TRAIN_END,
        "validation": (local_day >= VALIDATION_START) & (local_day <= VALIDATION_END),
        "test": local_day >= TEST_START,
    }


def split_xy(df: pd.DataFrame):
    masks = chronological_masks(df)
    X = df[FEATURES]
    y = df[TARGET].to_numpy(np.int8)
    result = {}
    for name, mask in masks.items():
        result[name] = (
            X.loc[mask].reset_index(drop=True),
            y[np.asarray(mask)],
            df.loc[mask].reset_index(drop=True),
        )
    return result


def fit_category_maps(frame: pd.DataFrame, columns: Iterable[str] = CAT_FEATURES) -> Dict[str, Dict[str, int]]:
    maps: Dict[str, Dict[str, int]] = {}
    for column in columns:
        values = sorted(frame[column].astype(str).unique().tolist())
        maps[column] = {value: index + 1 for index, value in enumerate(values)}
    return maps


def encode_categories(
    frame: pd.DataFrame,
    category_maps: Dict[str, Dict[str, int]],
    columns: Iterable[str] = CAT_FEATURES,
) -> np.ndarray:
    encoded = []
    for column in columns:
        mapping = category_maps[column]
        encoded.append(frame[column].astype(str).map(mapping).fillna(0).to_numpy(np.int32))
    return np.column_stack(encoded)


def encode_lightgbm(
    frame: pd.DataFrame,
    category_maps: Dict[str, Dict[str, int]],
    cat_features: Iterable[str] = CAT_FEATURES,
    num_features: Iterable[str] = NUM_FEATURES,
) -> np.ndarray:
    cats = encode_categories(frame, category_maps, cat_features).astype(np.float32)
    nums = frame[list(num_features)].to_numpy(np.float32)
    return np.column_stack([cats, nums]).astype(np.float32, copy=False)


def fit_frequency_maps(frame: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    maps = {}
    denominator = max(len(frame), 1)
    for column in CAT_FEATURES:
        counts = frame[column].astype(str).value_counts(dropna=False)
        maps[column] = (counts / denominator).to_dict()
    return maps


def encode_dense(
    frame: pd.DataFrame,
    frequency_maps: Dict[str, Dict[str, float]],
    numeric_mean: np.ndarray | None = None,
    numeric_std: np.ndarray | None = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    categorical = np.column_stack([
        frame[column].astype(str).map(frequency_maps[column]).fillna(0.0).to_numpy(np.float32)
        for column in CAT_FEATURES
    ])
    numeric = frame[NUM_FEATURES].to_numpy(np.float32)
    if numeric_mean is None:
        numeric_mean = numeric.mean(axis=0)
    if numeric_std is None:
        numeric_std = numeric.std(axis=0)
    numeric_std = np.where(numeric_std < 1e-6, 1.0, numeric_std).astype(np.float32)
    numeric_scaled = (numeric - numeric_mean) / numeric_std
    return np.column_stack([categorical, numeric_scaled]).astype(np.float32), numeric_mean, numeric_std


def build_input_row(
    created_date: dt.date,
    sub_council: str,
    ward: str,
    suburb: str,
    complaint_type: str,
    work_center: str,
    coordinate_state: str,
) -> pd.DataFrame:
    if not complaint_type or complaint_type == "Missing":
        raise ValueError("Complaint type is required.")
    if created_date < SUPPORTED_START:
        raise ValueError("Creation date is outside the supported period (from 1 April 2026).")
    if coordinate_state not in {"Available", "Missing", "Recorded as 0,0"}:
        raise ValueError("Coordinate quality must be Available, Missing, or Recorded as 0,0.")

    return pd.DataFrame([{
        "Sub_Council": str(sub_council),
        "Ward": str(ward),
        "Suburb": str(suburb),
        "C3_Complaint_Type": str(complaint_type),
        "Work_Center": str(work_center),
        "day_of_week": created_date.strftime("%A"),
        "day_index": float((created_date - SUPPORTED_START).days),
        "day_of_month": float(created_date.day),
        "is_weekend": float(created_date.weekday() >= 5),
        "coord_missing": float(coordinate_state == "Missing"),
        "coord_zero": float(coordinate_state == "Recorded as 0,0"),
    }], columns=FEATURES)
