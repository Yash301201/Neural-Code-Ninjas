# LearnPath AI - Kaggle OULAD integration

The selected Kaggle OULAD dataset has been downloaded and imported into the project's configured MySQL database. The richer React dashboard is available in **Dataset Analytics** in every role's sidebar, with a spotlight link on the regular dashboard.

Open http://127.0.0.1:8001/app/admin/dataset-analytics after signing in. Faculty, HOD and Student use the same `dataset-analytics` route under their own role prefix. Existing emails, passwords, JWT settings, IDs and academic mappings are preserved.

## Imported and verified

| Records | Count |
| --- | ---: |
| Course presentations | 22 |
| Course enrollments | 32,593 |
| Distinct anonymous learners | 28,785 |
| Assessment definitions | 206 |
| Assessment score records | 173,912 |
| Source VLE log records processed | 10,655,280 |
| Source clicks reconciled | 39,605,099 |
| Stored learner-week aggregates | 627,031 |

The Kaggle ZIP contains two identical copies of every CSV. The importer validates the copies and reads one copy only. All VLE source rows are processed; weekly aggregates are stored for fast queries. Aggregated log counts and click totals are checked against the raw source totals before marking the batch READY. Incomplete/failed batches never appear in the dashboard. Importing the same archive again is idempotent by SHA-256.

## Dashboard features

- Module, course-presentation and course-week filters, plus full available-course range.
- Cohort enrollment, active-learner, click, assessment-score, historical pass-rate and no-activity metrics.
- Area/line charts for weekly participation and score trends.
- Clickable learner-by-week engagement heatmap with most/least-active sorting and sample-size selection.
- Learner drill-down with weekly engagement and actual assessment submissions.
- Historical outcome donut, resource-usage horizontal bars, and stacked outcome bars across modules.
- Score-versus-engagement scatter plot, explicitly descriptive rather than causal.
- Search within the visible learner sample and attributed CSV export of that sample.
- Source provenance, license, import batch, raw record counts, checksum and transformation notes.

## Meaning and limits

OULAD is historical, public, anonymized UK Open University data from 2013-2014. It is separate from the college workspace and creates no login accounts. It does not contain original student names, engineering topic labels or classroom attendance. VLE clicks are online engagement, not attendance. Course codes such as AAA/BBB remain the original anonymous module codes.

Displayed research names are clearly labelled fictional Andhra/Telugu aliases. Five known fictional student/faculty display names in the regular workspace were also localized as previously requested. Their IDs, emails, password hashes, roles and departments were compared before/after and confirmed unchanged. The name-update command is idempotent and skips other/custom accounts.

Missing grades remain null; prior banked credits are excluded from current-period score averages. Weeks without scored submissions are gaps in the score line. Full-course final outcomes are shown separately from selected-week activity and are not used to produce early attention signals. No trained risk model or predictive accuracy is claimed. The scatter uses a deterministic sample of up to 300 assessed learners; the heatmap/table/export use the explicitly selected sample size. Summaries cover the entire selected cohort.

## Run the application

From the project root or backend folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-project.ps1
```

To download/import on another prepared installation, run from backend:

```powershell
.\.venv\Scripts\python.exe -m scripts.download_oulad
.\.venv\Scripts\python.exe -m scripts.import_oulad
```

Then restart FastAPI. This installation is already imported and running. If Kaggle requires access on another machine, download the selected dataset manually and place the ZIP at `backend/data/oulad/raw/oulad.zip` before running the importer. Initial database setup also includes the dataset table definitions; rows are loaded only by the explicit importer.

## Project files

- `backend/db/005_oulad_analytics.sql`: nine separate dataset/import tables.
- `backend/db/006_oulad_reporting_queries.sql`: project-specific read-only reporting queries.
- `backend/scripts/download_oulad.py`: validated public archive download.
- `backend/scripts/import_oulad.py`: streaming import, weekly aggregation, reconciliation and batch publishing.
- `backend/scripts/localize_display_names.py`: guarded fictional-name updates, no credential changes.
- `backend/app/dataset_analytics.py`: authenticated catalog, cohort analytics and learner detail APIs.
- `backend/data/oulad/manifest.json`: source, checksum, selected CSV members and actual counts.
- `frontend-react/src/pages/DatasetAnalytics.tsx` and `src/dataset-analytics.css`: interactive dashboard.

The raw ZIP is retained locally and excluded from Git/Docker contexts. The archive's SHA-256 is `22ba62b7db14e7ccd0679d35bdf8873efd0cb112dec6e02e28d291494690dd07`. No database data directory was replaced.

## Validation

Production TypeScript and Vite build passed. **14 MySQL integration tests passed**: existing workflows plus dataset reconciliation, score/NULL handling, banked-credit exclusion, zero-activity counts, range validation, authenticated drill-downs, duplicate-copy handling and malformed archives. A separate check against the full imported dataset reconciled cohort outcomes, timelines and heatmaps. Default BBB/2014J analytics returned in approximately 0.7 seconds in the local check; no college-scale concurrency benchmark is claimed.

The source download and import completed successfully from Kaggle. Docker setup was updated for the additional schema, but Docker execution was not tested. Live LLM provider behavior is unrelated to this import and still needs a configured provider key.

## Attribution

Kuzilek, J., Hlosta, M., & Zdrahal, Z. (2015). Open University Learning Analytics Dataset. DOI: 10.24432/C5KK69. CC BY 4.0.

[Kaggle source](https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset) · [Official documentation](https://archive.ics.uci.edu/dataset/349/open+university+learning+analytics+dataset) · [License](https://creativecommons.org/licenses/by/4.0/).
