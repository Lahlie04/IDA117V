# Revised package verification report

Verification date: 19 October 2026

## Must-fix completion

1. **McNemar wording corrected:** the assignment, technical appendix, README and presentation now state that McNemar tests paired correctness through the discordant cells on the same cases. It does not test macro-F1 or the difference between macro-F1 scores.
2. **Dataset licence status added:** the recorded Public/Custom License metadata is distinguished from evidence still required. Exact item-level terms, chain of custody and written redistribution approval are not evidenced; approval is not claimed and raw data remains excluded.
3. **Entity-embedding approval status added:** lecturer approval is required for the implemented second tabular neural architecture. No approval evidence is present and approval is not claimed.
4. **Question 8.2 updated:** the report lists the actual completed manual-upload package contents and accurately marks target repository accessibility, final commit hash, public deployment link and licence clearance as unverified or pending.
5. **Contribution template created:** one-page DOCX and PDF templates provide six blank member rows for real names, student numbers, roles, specific outputs/evidence, signatures and dates. No entries or signatures are invented.
6. **Presentation and Streamlit evidence updated:** three valid cases, one invalid case, local launch instructions and HTTP 200 are recorded. Public app and recording links remain clearly marked as not created/not verified.

## Preserved evidence boundary

The model results, figures and saved prediction evidence were not rerun or altered for these documentation corrections. The authoritative source-snapshot and metrics remain in `05_Results/`.

## Structure and Question 8.2 coverage

- Root and package READMEs present.
- Ten direct runtime dependencies pinned with exact `==` versions.
- Ordered scripts and reproduction notebook present.
- Seed 42 recorded in preparation and analysis code.
- Data dictionary, source/licence status and approval/open-item register present.
- Saved deployment model and model-comparison bundle present.
- Streamlit UI, prediction helper, deployment guide and verification script present.
- Twelve figures and complete result evidence present.
- Revised assignment included in DOCX and PDF.
- Revised reproducibility appendix included in PDF.
- Original project template included under `01_Report/Reference`.
- Raw dataset absent from the public package; `.gitignore` excludes raw XLSX/CSV files.

## Code and interface checks

- All Python files passed `py_compile`.
- Both saved joblib artifacts loaded successfully from the documented `03_Code` working directory.
- All ten direct pinned versions matched the verified environment.
- The existing interface evidence records three valid cases, the invalid blank-complaint error and HTTP 200.

## Document checks

- Revised assignment rendered to 49 pages and was visually reviewed.
- One-page contribution template rendered and was visually reviewed.
- Revised reproducibility appendix rendered to 3 pages and was visually reviewed.
- Assignment, appendix, contribution template and attached project-template PDFs passed preflight.

## GitHub boundary

The package is ready for manual upload to `https://github.com/mahlatseselowa/IDA117V.git`. Public accessibility and the final target-repository commit hash are not claimed. After upload/commit, verify with `git remote get-url origin`, `git rev-parse HEAD` and a clean `git status --short`.
