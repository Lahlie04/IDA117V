"""Verify three valid cases, one invalid case and the Streamlit health endpoint."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pandas as pd

from predict import load_bundle, predict_frame
from prepare_data import FEATURES, build_input_row

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "05_Results"


def wait_for_health(url: str, timeout: float = 30.0) -> int:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                return response.status
        except Exception:
            time.sleep(0.5)
    raise TimeoutError(f"Streamlit did not become healthy at {url}")


def main() -> None:
    bundle = load_bundle()
    demo_path = RESULTS / "demo_valid_inputs.csv"
    demo = pd.read_csv(demo_path)
    scored = predict_frame(demo[FEATURES], bundle)
    valid_results = []
    for index, row in scored.iterrows():
        probability = float(row["probability_at_risk"])
        prediction = int(row["prediction_at_risk"])
        assert 0.0 <= probability <= 1.0
        assert prediction in {0, 1}
        valid_results.append({
            "case": str(demo.loc[index, "case"]),
            "probability_at_risk": probability,
            "prediction_at_risk": prediction,
            "passed": True,
        })

    invalid_message = None
    try:
        build_input_row(
            pd.Timestamp("2026-05-30").date(), "1", "1", "Example", "", "Example", "Available"
        )
    except ValueError as error:
        invalid_message = str(error)
    assert invalid_message == "Complaint type is required."

    environment = os.environ.copy()
    environment["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    command = [
        sys.executable, "-m", "streamlit", "run", str(ROOT / "03_Code" / "app.py"),
        "--server.headless", "true", "--server.port", "8765",
    ]
    process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, env=environment)
    try:
        status = wait_for_health("http://127.0.0.1:8765/_stcore/health")
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)

    result = {
        "three_valid_cases": valid_results,
        "invalid_case": {"message": invalid_message, "passed": True},
        "streamlit_health": {"http_status": status, "passed": status == 200},
        "all_passed": all(item["passed"] for item in valid_results) and status == 200,
    }
    (RESULTS / "interface_ui_tests.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
