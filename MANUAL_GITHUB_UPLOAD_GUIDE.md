# Manual GitHub upload guide

Target repository:

`https://github.com/mahlatseselowa/IDA117V.git`

## Browser upload

1. Extract the ZIP.
2. Open the target repository in GitHub and sign in with an account that has write access.
3. Choose **Add file > Upload files**.
4. Open the extracted `IDA117V` folder and upload:
   - `.gitignore`
   - `README.md`
   - `MANUAL_GITHUB_UPLOAD_GUIDE.md`
   - `PUSH_INSTRUCTIONS.md`
   - `VERIFICATION_REPORT.md`
   - `PACKAGE_MANIFEST.txt`
   - the complete `IDA117V_Streamlit_Deployment` folder
5. Confirm that `02_Data/raw/Service_Requests_01_April_2026_until_30_May_2026.xlsx` is **not** included. The public package contains only `02_Data/raw/README.md`.
6. Use commit message: `Add reproducible IDA117V Question 8.2 package`.
7. Commit directly to the intended branch or create a pull request according to the group's process.

GitHub's browser uploader may require uploading large folders in smaller batches. Preserve the paths exactly.

## Git command-line upload

From an authenticated clone of the exact target repository:

```bash
git remote get-url origin
# Must be: https://github.com/mahlatseselowa/IDA117V.git

git pull --ff-only
# Copy the extracted package contents into this clone.

git add .gitignore README.md MANUAL_GITHUB_UPLOAD_GUIDE.md PUSH_INSTRUCTIONS.md VERIFICATION_REPORT.md PACKAGE_MANIFEST.txt IDA117V_Streamlit_Deployment
git status --short
git commit -m "Add reproducible IDA117V Question 8.2 package"
git push origin HEAD
```

## Record the final commit

After the upload succeeds:

```bash
git rev-parse HEAD
git status --short
```

- Insert the returned 40-character hash into the assignment only after confirming that the commit is visible in the exact target repository.
- `git status --short` should return no output.
- Do not use a commit hash from a different repository.

## Final checks on GitHub

Confirm that GitHub displays:

- the main repository README;
- `IDA117V_Streamlit_Deployment/requirements.txt`;
- the ordered scripts/notebook in `03_Code`;
- both saved `.joblib` model artifacts;
- the Streamlit app and deployment guide;
- figures and result evidence;
- documentation and report files; and
- no raw source dataset.
