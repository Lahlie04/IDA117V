# Dataset source, licence and approval status

## Dataset used

- Local filename expected by the code: `Service_Requests_01_April_2026_until_30_May_2026.xlsx`
- Subject: municipal SAP C3 service-request notifications
- Coverage in the verified package run: April-May 2026
- Source context recorded in the assignment: City of Cape Town Open Data Portal service-request item
- Source page recorded in the assignment: `https://odp-ccgis.opendata.arcgis.com/datasets/service-requests-2023-until-10-september-2026/explore`
- Policy reference recorded in the assignment: City of Cape Town Open Data Policy 27781

## Evidence and approval matrix

| Item | Current status | Evidence available | Still required |
|---|---|---|---|
| Public portal context | Recorded, not independently archived in this package | Assignment text records an SAP C3 Notifications item and City of Cape Town Corporate GIS ownership | Save a dated screenshot/PDF/export of the exact item page and metadata |
| Licence label | Recorded, not independently archived in this package | Assignment text records the portal item as Public with a `Custom License` | Archive the exact item-level Custom License wording and its effective date |
| Source-to-file chain of custody | Not evidenced | Schema and early records were reported as matching the portal item | Written confirmation that the supplied workbook/CSV is an unchanged authorised export of that exact item |
| Raw-data redistribution approval | Not evidenced; **approval is not claimed** | No written approval is included | Written permission or clear licence wording allowing GitHub redistribution of the supplied raw file |
| Lecturer acceptance of licence evidence | Not evidenced | None supplied | Dated lecturer email, LMS message, signed note or marked approval if required by the course |
| POPIA/lawful-basis and retention approval | Not evidenced; **approval is not claimed** | Schema review found no directly named person fields, but location may be quasi-identifying | Determination by the responsible organisation/information officer before operational use |

## Public-package control

The public repository package excludes raw XLSX/CSV files through `.gitignore`. Only code, documentation, aggregate figures, saved model artifacts and derived result evidence are included. An authorised local user can reproduce the analysis by placing the source workbook at the path documented in `02_Data/raw/README.md`.

Do not publish the raw dataset until the exact licence terms, chain of custody and redistribution rights are evidenced. The absence of raw data from the public package is intentional and is not evidence that redistribution has been approved.

## Acknowledgement rule

Use the exact owner name and acknowledgement language from the verified source record. Do not infer ownership or licence clearance from the filename, schema or public visibility alone.
