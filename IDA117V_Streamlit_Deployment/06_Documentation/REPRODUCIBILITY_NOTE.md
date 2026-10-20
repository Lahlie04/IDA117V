# Reproducibility and source-snapshot note

The packaged workbook contains **247,305 rows and 14 columns**. After excluding **131** rows without a usable creation timestamp, the modelling protocol uses **247,174 rows**.

- Training rows: 168,427
- Validation rows: 43,234
- Locked-test rows: 35,513
- At-risk rows: 94,737 (38.3%)
- Source SHA-256: `ca6e1f6a2648e33bf0ee0cf2f269544be705c26051c79c82a6544b7487dfd0fc`

These values were computed from the authorised local workbook used for the verified run. The raw workbook is not included in the public repository package because redistribution clearance is not evidenced. The values differ from some quantities in earlier assignment drafts that referred to a separate CSV snapshot. Do not silently combine metrics from different snapshots. The JSON and CSV files in `05_Results` are authoritative for this package run; the must-fix documentation changes did not rerun or alter those results.

The target repository is exactly:

`https://github.com/mahlatseselowa/IDA117V.git`

Repository accessibility and its final commit hash must be verified from that exact repository. Do not transfer a hash from another repository.
