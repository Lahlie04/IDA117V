# IDA117V - Seven-Day Municipal Service-Request Risk

This repository contains the complete Question 8.2 reproducibility package for the IDA117V group assignment. The project identifies newly created municipal service requests that may not be completed within seven calendar days and provides a human-review Streamlit prototype.

> Educational use only. The score must not deny, close or automatically deprioritise a request.

## Repository package

The complete package is in [`IDA117V_Streamlit_Deployment/`](IDA117V_Streamlit_Deployment/README.md).

It includes:

- finalized assignment report and project-template reference;
- pinned Python dependencies;
- ordered scripts and a reproduction notebook;
- fixed seed (`42`) and chronological split-before-fit workflow;
- data dictionary, source/licence evidence status and approval/open-item register;
- saved model and model-comparison bundles;
- Streamlit interface, local verification evidence, and explicit placeholders for any public app or recording link;
- figures, metrics, predictions, trials, ablations, paired-correctness McNemar evidence and subgroup evidence;
- a one-page blank contribution-statement template; and
- manual upload and deployment instructions.


## Status boundary

- Manual-upload package: **completed and locally verified**
- Target repository URL: `https://github.com/mahlatseselowa/IDA117V.git`; public accessibility and final commit hash are **unverified/pending**
- Dataset redistribution approval: **not evidenced; raw data excluded**
- Entity-embedding lecturer approval: **required but not evidenced; approval not claimed**
- Local Streamlit demonstration: **verified**
- Public Streamlit link and presentation recording: **not created / not verified**
- Contribution statement: **blank template included; no contributions or signatures claimed**
- McNemar interpretation: **paired correctness test, not a macro-F1 test**

## Raw-data policy

The source workbook is **not included in the public repository package** because the exact item-level redistribution terms have not been independently archived. Place an authorised local copy at:

```text
IDA117V_Streamlit_Deployment/02_Data/raw/Service_Requests_01_April_2026_until_30_May_2026.xlsx
```

See [`02_Data/raw/README.md`](IDA117V_Streamlit_Deployment/02_Data/raw/README.md) and [`SOURCE_AND_LICENCE.md`](IDA117V_Streamlit_Deployment/06_Documentation/SOURCE_AND_LICENCE.md).

## Quick start

```bash
cd IDA117V_Streamlit_Deployment
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python 03_Code/run_analysis.py
./.venv/bin/python 03_Code/make_documentation.py
./.venv/bin/python 03_Code/build_report.py
./.venv/bin/python 03_Code/verify_interface.py
./.venv/bin/python -m streamlit run 03_Code/app.py
```

Windows PowerShell commands and full instructions are in the [package README](IDA117V_Streamlit_Deployment/README.md).

## GitHub upload

Use [`MANUAL_GITHUB_UPLOAD_GUIDE.md`](MANUAL_GITHUB_UPLOAD_GUIDE.md). After committing to the exact target repository, record the final hash with:

```bash
git rev-parse HEAD
```

Do not transfer a commit hash from another repository.
