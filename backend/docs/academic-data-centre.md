# LearnPath Academic Data Centre

The admin page is now **Academic Data Centre** at http://127.0.0.1:8001/app/admin/academic-data. The former /admin/demo-showcase URL remains compatible. The OULAD selector and research-link form were removed from this page; the original research archive remains separate and has not been falsely relabeled.

The populated collection now has 110 students, 11 faculty, 5 HODs, 9 courses, 18 subject records, 110 enrollments, 19 teaching mappings and 220 student-subject performance rows. Six new B.Tech degrees have ten enrolled students and two subjects each:

- Artificial Intelligence and Machine Learning: Python Programming, Machine Learning.
- Data Science: Data Structures, Data Analytics.
- Electronics and Communication Engineering: Digital Electronics, Communication Systems.
- Electrical and Electronics Engineering: Electrical Circuits, Control Systems.
- Mechanical Engineering: Engineering Mechanics, Thermodynamics.
- Civil Engineering: Structural Analysis, Surveying.

Each added course includes saved exam results, a published practice paper, assignments, submissions, attendance, study plans, feedback and timetable slots. Faculty portfolios and HOD records are linked by department.

Visible names and titles no longer include [DEMO]. Sample student references use LP prefixes and the old showcase sections are named 2026 Cohort. A pre-existing DBMS subject was preserved; its separate sample counterpart uses Applied Database Management Systems where a unique name was required. No record IDs or existing mark totals were merged or discarded. Existing emails and password hashes were preserved.

These are fictional prefilled academic records for a local presentation. Their provenance remains explicit in the manifest and documentation rather than appended to people's names. Passwords and JWTs are excluded from CSV snapshots.

## Stable prefilled data

The seed runs once. It does not generate random data when a page opens. MySQL remains the source of truth, and deliberate CRUD changes are still persisted. Course coverage is read from stored records rather than old showcase-summary totals.

From backend, the explicit idempotent command is:

```powershell
.\.venv\Scripts\python.exe -m scripts.prefill_academic
```

Regenerate CSV snapshots after deliberate changes with:

```powershell
.\.venv\Scripts\python.exe -m scripts.export_college_dataset
```

The CSV exports are snapshots, not an automatically synchronized second database. Do not rerun the original sample seeder to reset passwords or duplicate courses.

## Verification

29 integration tests passed using learnpath_ai_test, including repeat-seed protection, six populated programs, existing password preservation, removal of the name suffix, existing-subject name collisions and admin-only catalogue access. TypeScript/Vite build passed. Live API verification confirmed nine courses, correct enrollment counts, plain display names, working role logins and a healthy MySQL connection.

A private pre-change database backup is retained outside the repository. No Git push was performed.
