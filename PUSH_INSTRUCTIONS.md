# Target repository hand-off

Target repository (must be used exactly):

`https://github.com/mahlatseselowa/IDA117V.git`

The target repository could not be retrieved publicly or accessed through Git from the package-building session, so no target commit was created and no target commit hash is claimed.

## Access needed to complete the GitHub commit

Use either of these routes:

1. **Repository collaborator route:** A GitHub user with write access clones the exact target repository and copies the contents of this hand-off into that clone.
2. **Mounted clone route:** Provide this environment with a current writable clone of the exact target repository, including its `.git` directory and existing history, through an authenticated GitHub integration. Do not send passwords or access tokens in chat.

## Commit procedure

From a clone of the exact target repository:

```bash
git remote get-url origin
# Must output: https://github.com/mahlatseselowa/IDA117V.git

git pull --ff-only
# Copy the hand-off files into the clone.

git add .gitignore README.md MANUAL_GITHUB_UPLOAD_GUIDE.md PUSH_INSTRUCTIONS.md PACKAGE_MANIFEST.txt VERIFICATION_REPORT.md IDA117V_Streamlit_Deployment
# The raw XLSX is excluded by .gitignore pending licence confirmation.

git status --short
git commit -m "Add reproducible IDA117V service-request risk package"
git push origin HEAD

git rev-parse HEAD
git status --short
```

Use the 40-character value returned by the final `git rev-parse HEAD` as the assignment's final commit hash. `git status --short` should return no output. Confirm that the commit is visible in the exact target repository before inserting the hash in the assignment.

Do not use a commit hash from the reference repository or any other repository.
