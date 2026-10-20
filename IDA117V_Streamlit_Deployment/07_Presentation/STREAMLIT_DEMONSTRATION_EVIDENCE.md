# Streamlit demonstration evidence

## Verified local status

The included verification script loaded the saved model and recorded:

- three valid held-out profiles scored successfully;
- one invalid blank-complaint case rejected with `Complaint type is required.`; and
- HTTP 200 from the local Streamlit health endpoint.

No public Streamlit URL is claimed. No presentation recording URL is claimed.

## Re-run the verification

From `IDA117V_Streamlit_Deployment`:

```powershell
.\.venv\Scripts\python.exe .\03_Code\verify_interface.py
.\.venv\Scripts\python.exe -m streamlit run .\03_Code\app.py
```

## Recorded valid cases

| Case | Date | Sub-council | Ward | Suburb | Complaint | Work centre | Probability | Prediction | Observed class |
|---|---|---|---|---|---|---|---:|---|---|
| Example 1 | 2026-05-23 | Sub-Council 8 | 85 | STRAND | Suspect Tampering | REVENUE PROTECTION: EK - MOBI_REVP166 | 79.7% | At risk | At risk |
| Example 2 | 2026-05-28 | Sub-Council 11 | 60 | LANSDOWNE | Meter: Damaged / Faulty | Tygerberg | 68.2% | At risk | At risk |
| Example 3 | 2026-05-30 | Sub-Council 3 | 55 | RUGBY | MTR: Customer Reconnection Request | Water and Sanitation Revenue | 51.6% | Below 0.65 threshold | Within 7 days |

## Recorded invalid case

Complaint type is blank. Expected and verified error:

```text
Complaint type is required.
```

## Link placeholders

- Public Streamlit link: `[NOT CREATED / NOT VERIFIED]`
- Presentation/recording link: `[NOT CREATED / NOT VERIFIED]`

Do not replace these placeholders with guessed or fabricated URLs.
