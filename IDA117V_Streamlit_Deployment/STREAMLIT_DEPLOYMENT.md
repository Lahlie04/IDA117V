# Streamlit deployment and demonstration status

## Current status

- Local launch: **verified**
- Saved model loading: **verified**
- Three valid demonstration cases: **verified**
- One invalid blank-complaint case: **verified**
- Local health endpoint: **HTTP 200 verified**
- Public Streamlit link: **[NOT CREATED / NOT VERIFIED]**
- Presentation/recording link: **[NOT CREATED / NOT VERIFIED]**

## Local deployment

From `IDA117V_Streamlit_Deployment`:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
.\.venv\Scripts\python.exe .\03_Code\verify_interface.py
.\.venv\Scripts\python.exe -m streamlit run .\03_Code\app.py
```

The interface loads `03_Code/final_model.joblib` and does not require the raw workbook for prediction. Streamlit normally prints a local URL such as `http://localhost:8501/`.

Verification writes `05_Results/interface_ui_tests.json` and checks three valid profiles, the expected invalid error and the local health endpoint. See `07_Presentation/STREAMLIT_DEMONSTRATION_EVIDENCE.md`.

## Public deployment - not yet completed

Target repository supplied for upload:

`https://github.com/mahlatseselowa/IDA117V.git`

Public accessibility, branch and final commit hash are not verified in this package. After the package has been committed and is accessible to the reviewer:

1. Select the actual target repository and branch in Streamlit Community Cloud.
2. Set the app file to `IDA117V_Streamlit_Deployment/03_Code/app.py`.
3. Ensure `IDA117V_Streamlit_Deployment/requirements.txt` and `03_Code/final_model.joblib` are committed.
4. Do **not** publish the raw workbook unless redistribution rights are evidenced.
5. Do not add credentials or secrets; this app requires none.
6. Test all four documented demonstration cases.
7. Insert the real tested URL below.

Public Streamlit link: `[NOT CREATED / NOT VERIFIED]`

## Stable submission reference

After upload and commit to the exact target repository, record:

```powershell
git remote get-url origin
git rev-parse HEAD
git status --short
```

The remote must be exactly `https://github.com/mahlatseselowa/IDA117V.git`. Insert only that repository’s 40-character `HEAD` hash. Do not reuse another repository’s hash.
