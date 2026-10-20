"""Generate the package data dictionary and reproducibility note from saved evidence."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "05_Results"
DOCS = ROOT / "06_Documentation"


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    audit = json.loads((RESULTS / "dataset_audit.json").read_text(encoding="utf-8"))
    dictionary = """# Data dictionary

| Source field | Type | Model use | Meaning / treatment |
|---|---|---|---|
| Sub_Council | Categorical | Yes | Administrative/service grouping; missing values retained as `Missing`. |
| Ward | Categorical label | Yes | Ward label preserved as text; missing/odd labels monitored. |
| Suburb | Categorical | Yes | High-cardinality place label; privacy-sensitive when linked. |
| C3_Complaint_Type | Categorical | Yes | Primary complaint category. |
| Work_Center | Categorical | Yes, subject to confirmation | Routing/work-centre label assumed available at creation time. |
| Notification | Identifier-like | No | Excluded to avoid memorisation and leakage. |
| Notification_type | Mixed identifier/text | No | Excluded because it is high-cardinality and identifier-like. |
| X_Y_Co_ordinate_1 / 2 | Numeric coordinates | Flags only | Raw values excluded; only missing and `0,0` quality flags are used. |
| Created_On_Date | Datetime | Derived features | Creation timestamp used for chronological split and date features. |
| Changed_on | Datetime | No | Excluded as post-creation leakage. |
| Completed_Date | Datetime | Target only | Used only to derive the seven-day outcome. |
| Notifications_Created | Count | No | Excluded because it is nearly constant. |
| ObjectId | Identifier | No | Excluded from model features. |
| risk_7d | Binary target | Target | `1` when not completed within 0-7 days inclusive; missing/invalid completion is treated as at risk. |

## Derived model features

- `day_of_week`
- `day_index` from 1 April 2026
- `day_of_month`
- `is_weekend`
- `coord_missing`
- `coord_zero`
"""
    (DOCS / "DATA_DICTIONARY.md").write_text(dictionary, encoding="utf-8")

    note = f"""# Reproducibility and source-snapshot note

The packaged workbook contains **{audit['source_rows']:,} rows and {audit['source_columns']} columns**. After excluding **{audit['excluded_missing_creation_timestamp']:,}** rows without a usable creation timestamp, the modelling protocol uses **{audit['model_rows']:,} rows**.

- Training rows: {audit['splits']['train']:,}
- Validation rows: {audit['splits']['validation']:,}
- Locked-test rows: {audit['splits']['test']:,}
- At-risk rows: {audit['at_risk']:,} ({audit['at_risk_rate']:.1%})
- Source SHA-256: `{audit['source_sha256']}`

These values were computed from the authorised local workbook used for the verified run. The raw workbook is not included in the public repository package because redistribution clearance is not evidenced. They differ from some quantities in earlier assignment drafts that referred to a separate CSV snapshot. Do not silently combine metrics from different snapshots. The JSON and CSV files in `05_Results` are authoritative for this package run.

The target repository is exactly:

`https://github.com/mahlatseselowa/IDA117V.git`

Repository accessibility and its final commit hash must be verified from that exact repository. Do not transfer a hash from another repository.
"""
    (DOCS / "REPRODUCIBILITY_NOTE.md").write_text(note, encoding="utf-8")
    print("Documentation generated.")


if __name__ == "__main__":
    main()
