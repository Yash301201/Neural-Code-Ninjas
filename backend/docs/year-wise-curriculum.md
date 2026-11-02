# Year-wise academic curriculum and teaching guide

Open http://127.0.0.1:8001/app/ and refresh with Ctrl+F5. Faculty, HOD and Admin have a **Years, Curriculum & Teaching** sidebar entry.

## Degree structures populated

| Program | Duration | Classified curriculum subjects |
| --- | --- | --- |
| B.Tech programs (7 degrees) | 4 years | 24 per degree, 6 per year |
| Bachelor of Computer Applications (BCA) | 3 years | 18, 6 per year |
| MCA and M.Tech | 2 years | 15 per degree: 8 in Year 1, 7 in Year 2 |

The ten degree curricula contain 216 classified subject records and 648 topics. Each subject has an explicit study year and semester; semester is within that year (Year 2 uses semesters 3 and 4). These are locally generated illustrative curricula, not a claim to match an accredited university syllabus.

## Students, years and sections

The sample collection now contains 232 named students across the ten degrees. Each study year has A/B sample cohorts. The whole live workspace currently has 235 actively enrolled students: 232 sample students plus three older enrolled students whose cohort year was not recorded. Those older records remain explicitly unassigned rather than guessed.

Year of study and calendar academic year are different fields. Example: UG / B.Tech CSE / Year 2 / Year 2 A / 2026–2027. The original generated CSE class is now classified as Year 2, matching its DBMS and Networks subjects. Existing student IDs, exam marks, attendance rows and password hashes were preserved. New sample students were added for the other years and sections.

## Frontend walkthrough

1. Sign in as Faculty, HOD or Admin and open Years, Curriculum & Teaching.
2. Select UG/PG, degree, study year and section. The distribution table counts distinct students per level/year; the cohort table shows section counts.
3. Student roster shows name, ID, email, degree, current enrolled year, section and calendar academic year.
4. Year-wise subjects shows the saved year, semester and topics for each subject.
5. Faculty & topic coverage shows faculty name, degree, year, semester, subject, section and topic plan. Staff can save Planned / In Progress / Completed. The selection is persisted in MySQL and audited.
6. HOD/Admin can classify an unassigned cohort using Assign year. The operation rejects a year beyond the course duration and refuses to overwrite an existing cohort year. Create a new cohort and enroll appropriately when promoting students, so history stays intact.
7. HOD/Admin use Department/Institution Operations > Teaching coverage to assign a faculty member. Subject choices include degree, year and semester; sections are filtered to the matching year. The backend rejects cross-year assignments even if a client bypasses the selector.

The shared academic scope selector now includes Year of study, so attendance, assignments, exams and individual performance use the selected year/section. Students can access their enrolled year, not arbitrary later-year subjects. Faculty can access their assigned classes; HOD can manage their department; Admin can manage all departments.

Older unclassified subjects remain available for their historical records and are not counted toward the 216 classified curriculum subjects. The college catalogue can show extra legacy subjects above the curriculum minimums.

## MySQL storage and proof

- courses.duration_years and course_programs.program_level: degree structure.
- section_study_years: cohort's year of study; student_enrollments links students to it.
- subject_curriculum: subject year and semester.
- faculty_subject_assignments: faculty + subject + section; year comes from the linked records.
- topics and teaching_topic_progress: planned syllabus topics and saved coverage per teaching assignment.

Open backend/db/016_year_curriculum_reports.sql in Workbench connected to port 3307 / schema learnpath_ai. It contains read-only reports for curriculum minimums, year/section counts, named student enrollments, semester subjects and faculty topic coverage.

## Setup and snapshots

From backend, if applying these changes to another initialized copy:

```powershell
.\.venv\Scripts\python.exe -m scripts.setup_years
.\.venv\Scripts\python.exe -m scripts.prefill_years
```

The population command is idempotent. It does not generate new students on each page load. A private pre-change database backup was saved outside the repository.

The engineering CSV snapshots now include study_year and semester, curriculum.csv, topics.csv and topic_coverage.csv. Refresh the UI for live database changes; regenerate CSVs explicitly with:

```powershell
.\.venv\Scripts\python.exe -m scripts.export_college_dataset
```

Existing account credentials are unchanged. New sample accounts use the existing local sample password convention; password hashes and JWTs are never exported.

## Validation

30 integration tests pass against learnpath_ai_test. Tests cover 24/18/15 subject minimums, every year and semester, preserved grades/passwords, BCA duration, cross-year assignment rejection, student isolation, topic-coverage persistence, cohort classification limits and seed idempotence. The TypeScript/Vite build passes. Live API checks confirmed all ten curricula and all four role workspaces; MySQL health is connected.
