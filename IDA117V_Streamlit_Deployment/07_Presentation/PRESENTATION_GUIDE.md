# IDA117V 10-12 minute presentation and demonstration guide

## Evidence status

- Presentation plan: **completed**
- Local Streamlit launch: **verified**
- Demonstration evidence: **three valid cases and one invalid case verified**
- Streamlit health endpoint: **HTTP 200 verified**
- Public Streamlit link: **[NOT CREATED / NOT VERIFIED]**
- Presentation/recording link: **[NOT CREATED / NOT VERIFIED]**
- Signed contribution statement: **blank one-page template included; not signed**

## Suggested flow

| Time | Speaker topic | Evidence to show |
|---|---|---|
| 0:00-1:00 | Problem and stakeholder | Seven-day non-completion target and human-review purpose |
| 1:00-2:30 | Data, provenance and ethics | Snapshot audit, leakage exclusions, licence evidence gaps and POPIA limits |
| 2:30-4:00 | EDA and chronological split | Target, missingness, complaint/sub-council and daily-risk figures |
| 4:00-6:00 | Model set | Baseline, logistic, LightGBM, dense MLP and entity-embedding network; state that lecturer approval for the entity-embedding architecture is required and not evidenced |
| 6:00-7:30 | Evaluation and optimisation | Macro-F1, recall, threshold, locked test and learning curve |
| 7:30-9:00 | Ablation and paired test | Feature-group changes; explain that McNemar tests paired correctness on the same cases, not macro-F1 |
| 9:00-10:30 | Streamlit demonstration | Run the three valid examples and one invalid blank-complaint case |
| 10:30-12:00 | Recommendation and limits | Capacity scenario, subgroup audit, licence/repository/deployment limitations and responsible-use controls |

## Streamlit demonstration cases

Decision threshold: `0.65`.

| Case | Date | Complaint | Saved probability | Expected prediction | Saved observed class / test status |
|---|---|---|---:|---|---|
| Example 1 | 2026-05-23 | Suspect Tampering | 79.7% | At risk | Observed at risk; verification passed |
| Example 2 | 2026-05-28 | Meter: Damaged / Faulty | 68.2% | At risk | Observed at risk; verification passed |
| Example 3 | 2026-05-30 | MTR: Customer Reconnection Request | 51.6% | Below review threshold | Observed within 7 days; verification passed |
| Invalid | - | Blank complaint type | - | Validation error | `Complaint type is required.`; verification passed |

Authoritative machine-readable evidence: `05_Results/interface_ui_tests.json`, `demo_valid_inputs.csv` and `demo_invalid_input.csv`.

## Local launch

From `IDA117V_Streamlit_Deployment`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv\Scripts\python.exe .\03_Code\verify_interface.py
.\.venv\Scripts\python.exe -m streamlit run .\03_Code\app.py
```

Normally open `http://localhost:8501/` after Streamlit starts.

## Presenter controls

- Say that McNemar evaluates paired correct/incorrect outcomes and discordant pairs. Do not describe it as a macro-F1 test.
- Do not claim lecturer approval of the entity-embedding network without evidence.
- Do not claim dataset redistribution approval; the public package excludes the raw data.
- Do not show names, phone numbers, emails, addresses, credentials or raw personal data.
- Replace speaker names only with real group members and claim only work actually performed.
- Add public deployment or recording links only after they exist and have been tested.
