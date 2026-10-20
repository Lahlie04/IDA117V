# IDA117V: Seven-Day Municipal Service-Request Risk

This package contains an executed student data-science prototype for identifying newly created municipal service requests that may not be completed within seven calendar days. It uses the supplied April-May 2026 service-request workbook and a leakage-safe chronological evaluation protocol.

> **Important:** This is an educational human-review aid, not an official municipal decision system. It must not deny, close or automatically deprioritise a request.

## Submission record

- **Manual-upload package:** Completed and verified locally
- **Target repository URL:** `https://github.com/mahlatseselowa/IDA117V.git` (supplied target; public accessibility and branch are unverified in this package)
- **Target final commit hash:** Pending; obtain it from this exact repository after upload/commit
- **Local Streamlit launch and test cases:** Verified
- **Public Streamlit link:** Not created / not verified
- **Dataset redistribution approval:** Not evidenced; raw data excluded
- **Entity-embedding lecturer approval:** Required by the template; not evidenced and not claimed
- **Presentation recording:** Not created / not verified
- **Signed contribution statement:** Blank one-page template included; not signed
- **Package folder:** `IDA117V_Streamlit_Deployment/`
- **Python:** 3.12
- **Seed:** 42

Do not insert or transfer a commit hash from the reference repository. After this package is committed to the target repository, run `git rev-parse HEAD` there and record that exact 40-character value in the assignment.

## Package structure

```text
IDA117V_Streamlit_Deployment/
├── 01_Report/
│   ├── IDA117V_Final_Compiled_Assignment_Plain_Simple.docx
│   ├── IDA117V_Final_Compiled_Assignment_Plain_Simple.pdf
│   ├── IDA117V_Reproducibility_Appendix.pdf
│   ├── CONTRIBUTION_STATEMENT_TEMPLATE.docx
│   ├── CONTRIBUTION_STATEMENT_TEMPLATE.pdf
│   ├── CONTRIBUTION_FORM.md
│   └── Reference/IDA117V_Project_Template_2.pdf
├── 02_Data/
│   ├── raw/                    # Placement instructions only; raw workbook excluded pending licence proof
│   └── processed/              # Non-identifying schema sample
├── 03_Code/
│   ├── Data_Science_Project.ipynb
│   ├── app.py
│   ├── build_report.py
│   ├── final_model.joblib
│   ├── make_documentation.py
│   ├── model_comparison_bundle.joblib
│   ├── neural.py
│   ├── predict.py
│   ├── prepare_data.py
│   ├── run_analysis.py
│   └── verify_interface.py
├── 04_Figures/                # Twelve generated analytical figures
├── 05_Results/                # Audits, trials, metrics, predictions and UI tests
├── 06_Documentation/          # Data dictionary, source/licence, approvals and snapshot notes
├── 07_Presentation/           # Presentation guide and Streamlit demonstration evidence
├── README.md
├── STREAMLIT_DEPLOYMENT.md
└── requirements.txt
```

## Question 8.2 evidence map

| Template requirement | Package evidence |
|---|---|
| README | This file: setup, execution order, outputs, limitations and verification |
| Environment/requirements | `requirements.txt` and `05_Results/environment.json` |
| Fixed seeds | `SEED = 42` in `03_Code/prepare_data.py` and `03_Code/run_analysis.py` |
| Execution order | This README, `03_Code/Data_Science_Project.ipynb` and ordered scripts in `03_Code/` |
| Source links/licence/approvals | `06_Documentation/SOURCE_AND_LICENCE.md` and `APPROVALS_AND_OPEN_ITEMS.md` |
| Data dictionary | `06_Documentation/DATA_DICTIONARY.md` |
| Saved model/pipeline | `03_Code/final_model.joblib` and `03_Code/model_comparison_bundle.joblib` |
| User-interface code and demo evidence | `03_Code/app.py`, `03_Code/predict.py`, `STREAMLIT_DEPLOYMENT.md` and `07_Presentation/STREAMLIT_DEMONSTRATION_EVIDENCE.md` |
| Figures and experimental evidence | `04_Figures/` and `05_Results/` |
| Raw-data control | Raw XLSX/CSV files excluded by `.gitignore`; placement instructions in `02_Data/raw/README.md` |
| Assignment/template/contributions | `01_Report/`, `01_Report/Reference/` and the blank one-page contribution-statement template |

## Start in Windows PowerShell

Clone the target repository after access has been confirmed:

```powershell
git clone https://github.com/mahlatseselowa/IDA117V.git
cd .\IDA117V\IDA117V_Streamlit_Deployment
```

Create the environment and install the exact dependencies:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r .\requirements.txt
```

The source workbook must be present locally as:

```text
02_Data/raw/Service_Requests_01_April_2026_until_30_May_2026.xlsx
```

Rebuild all evidence and launch the app:

```powershell
.\.venv\Scripts\python.exe .\03_Code\run_analysis.py
.\.venv\Scripts\python.exe .\03_Code\make_documentation.py
.\.venv\Scripts\python.exe .\03_Code\build_report.py
.\.venv\Scripts\python.exe .\03_Code\verify_interface.py
.\.venv\Scripts\python.exe -m streamlit run .\03_Code\app.py
```

Open the local URL printed by Streamlit, normally <http://localhost:8501/>. Calling the virtual-environment Python directly avoids changing the PowerShell activation policy.

## Start on macOS or Linux

```bash
python3.12 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/python -m pip install -r requirements.txt
./.venv/bin/python 03_Code/run_analysis.py
./.venv/bin/python 03_Code/make_documentation.py
./.venv/bin/python 03_Code/build_report.py
./.venv/bin/python 03_Code/verify_interface.py
./.venv/bin/python -m streamlit run 03_Code/app.py
```

## Notebook route

Install `03_Code/requirements_notebook.txt` with the same virtual-environment Python. Then select that environment as the VS Code Python/Jupyter kernel and open `03_Code/Data_Science_Project.ipynb`.

The script route remains authoritative because it recreates all outputs in a fixed order.

## Execution order

1. `prepare_data.py` parses the workbook, excludes rows without a usable creation timestamp, derives the seven-day target and creation-time features, and creates the chronological split.
2. `run_analysis.py` audits the source, creates EDA figures, trains the baseline and four substantive models, optimises LightGBM on validation only, evaluates the locked test period, runs ablations, learning curves, McNemar analysis, subgroup checks and capacity scenarios, and saves all artifacts.
3. `make_documentation.py` refreshes the data dictionary and source-snapshot note.
4. `build_report.py` regenerates the reproducibility appendix PDF.
5. `verify_interface.py` scores three valid held-out profiles, checks one invalid complaint case and verifies the Streamlit health endpoint.
6. `app.py` loads `final_model.joblib`; it does not train during prediction.

## Leakage controls

The model uses only information intended to be available when a request is created:

- sub-council, ward and suburb;
- complaint type and work centre;
- derived creation-date features; and
- coordinate missing/zero quality flags.

`Completed_Date` is used only to create the target. `Changed_on`, notification identifiers, `Notifications_Created`, `ObjectId` and raw coordinates are excluded from model inputs. All learned encoders, maps, scalers and early-stopping decisions are fitted on training data only.

## Code-derived data snapshot

The packaged workbook produced the following verified run values:

- **Source rows / columns:** 247,305 / 14
- **Rows excluded for missing or invalid creation time:** 131
- **Modelling rows:** 247,174
- **Date coverage:** 1 April-30 May 2026
- **Within seven days:** 152,437
- **At risk:** 94,737 (38.3%)
- **Chronological split:** 168,427 training / 43,234 validation / 35,513 locked test
- **Source SHA-256:** `ca6e1f6a2648e33bf0ee0cf2f269544be705c26051c79c82a6544b7487dfd0fc`

These values differ from some earlier report-draft quantities that referred to a different CSV snapshot. For this package, `05_Results/dataset_audit.json` and `05_Results/run_summary.json` are authoritative.

## Model set

The package trains the following on identical chronological partitions:

1. Dummy prior baseline
2. Regularised logistic regression
3. LightGBM gradient boosting
4. Dense multilayer perceptron
5. NumPy entity-embedding tabular neural network

The optimized LightGBM deployment model is selected and tuned using the validation period only. The locked test period is evaluated after model and threshold selection.

The entity-embedding network is the implemented second tabular neural architecture. The project template requires lecturer approval for an approved tabular neural network. No approval evidence is included, so approval is not claimed. See `06_Documentation/APPROVALS_AND_OPEN_ITEMS.md`.

## Recorded run results

- **Selected deployment model:** Optimized LightGBM
- **Selected threshold:** 0.65
- **Validation macro-F1:** 0.7170
- **Locked-test accuracy:** 0.6459
- **Locked-test macro-F1:** 0.6458
- **Locked-test at-risk precision:** 0.5815
- **Locked-test at-risk recall:** 0.7073
- **Locked-test ROC-AUC:** 0.7273
- **Locked-test average precision:** 0.7227

Full reports, model comparisons and confusion matrices are stored in `05_Results/`. These results apply only to the packaged code, source snapshot and recorded environment.

McNemar's test in this project uses paired correct/incorrect outcomes on the same locked cases and tests whether the two discordant cells are balanced. It does **not** test macro-F1 or the difference between macro-F1 scores. Macro-F1, precision and recall are interpreted separately.

## Demonstration

Local launch and the saved demonstration cases are verified. Public app link: **[NOT CREATED / NOT VERIFIED]**. Presentation/recording link: **[NOT CREATED / NOT VERIFIED]**.

1. Run `03_Code/verify_interface.py`.
2. Launch `python -m streamlit run 03_Code/app.py`.
3. Demonstrate the three held-out profiles in `05_Results/demo_valid_inputs.csv`.
4. Demonstrate the invalid blank-complaint case; the verified message is `Complaint type is required.`
5. For batch scoring, upload a CSV containing the eleven columns listed in `06_Documentation/DATA_DICTIONARY.md`.

Authoritative evidence: `05_Results/interface_ui_tests.json` and `07_Presentation/STREAMLIT_DEMONSTRATION_EVIDENCE.md`.

## Interpretation and ethical limits

- The seven-day horizon is a project assumption and must be checked against complaint-specific service standards.
- The availability and stability of `Work_Center` at creation time require confirmation from the data owner.
- The extract covers only two months; seasonal and longer-term generalisation are not established.
- A missing/invalid completion timestamp is treated conservatively as at risk; source-system status semantics require confirmation.
- Ward, suburb and coordinate information may be quasi-identifying when linked with other information.
- The model cannot establish causation and must not replace urgency, safety, vulnerability or operational-capacity judgement.
- Monitor recall and false-positive rates by service and location before any pilot.
- Do not enter names, phone numbers, email addresses, exact street addresses, credentials or free-text personal information.

## Data source and reuse

The assignment research associated the schema with a municipal SAP C3 service-request open-data item displayed with a Custom License. The exact archived item-level licence wording was not independently supplied during package construction. Therefore raw-data redistribution is not claimed as approved.

The public repository package does not include the source workbook; `.gitignore` excludes raw XLSX/CSV files. Publish the raw file only after archiving the exact source URL and licence text and confirming redistribution conditions. See `06_Documentation/SOURCE_AND_LICENCE.md`.

## Security note

Load only the trusted joblib files supplied with this package. Python pickle/joblib files from unknown sources can execute code when loaded. Do not commit Streamlit secrets, credentials or access tokens.

## Group completion checklist

Before final submission:

- Insert the verified student number, group number, lecturer, other members and submission date.
- Record only actual contributions and obtain required signatures.
- Obtain and archive lecturer approval for the entity-embedding network as the second tabular neural architecture; none is currently evidenced.
- Archive the exact data-source URL, item-level licence terms, chain of custody and written redistribution permission; none is currently sufficient to publish the raw file.
- Ensure each member understands the problem, data preparation, models, metrics, limitations and code.
- Complete the one-page contribution statement with real member names, student numbers, roles, specific outputs, dates and signatures.
- Rehearse a 10-12 minute presentation with every member participating; add a real recording link only if one is created.
- Commit the package to `https://github.com/mahlatseselowa/IDA117V.git`.
- Run `git rev-parse HEAD` in that exact target repository and insert the returned hash in the assignment.

## AI assistance disclosure

AI assistance was used for code development, execution support, documentation and presentation preparation. Every group member must review, understand and be able to defend the work and must follow the institution's disclosure rules.
