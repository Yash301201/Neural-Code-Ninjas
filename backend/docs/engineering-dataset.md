# LearnPathAI engineering-college dataset

This is a locally generated, fictional relational demonstration dataset, exported from MySQL. It is not a public Kaggle dataset and does not identify real students or employees. Names and credentials are demo identities; password hashes, original passwords, JWTs and provider keys are excluded.

The CSV files contain 50 students, seven faculty, one HOD, one admin, six subject records, 50 enrollments, seven teaching mappings, 100 student-subject performance rows and 57 staff evidence records. Subjects are Database Management Systems and Computer Networks in the three existing degrees. B.Tech and M.Tech are engineering programs; MCA remains correctly labeled a computing program.

Join students.user_id to enrollments.student_id and student_subject_performance.student_id. Join subject_id to subjects.subject_id. Faculty and HOD IDs are linked in teaching_assignments and performance rows. Staff evidence links owner_id and reviewed_by to faculty, HOD and admin user IDs. Review status and research examples are synthetic demonstrations, not verified real publication claims.

All rows retain clear [DEMO] labeling. Marks are synthetic. Refining the demo question text and answer choices retained existing correct/incorrect outcomes and mark totals.

## Live application

Dataset Analytics is now Engineering Dataset and reads the role-scoped /api/college-data endpoint. Student sees their own data, faculty their assigned classes, HOD their department, admin the institution. The API returns no password fields.

The main dataset uses live MySQL records. CSV files are explicit snapshots and do not automatically change when users edit the application. Refresh Engineering Dataset to see current MySQL changes; regenerate snapshots from backend with:

```powershell
.\.venv\Scripts\python.exe -m scripts.export_college_dataset
```

Run the idempotent engineering refinement for existing clearly labeled demo subjects only:

```powershell
.\.venv\Scripts\python.exe -m scripts.prepare_engineering
```

OULAD remains available only as a separate research explorer; it is not relabeled into engineering students, faculty, HODs or exam grades. Public anonymized data cannot supply this application's full named administrative relationships. No new external dataset was misrepresented as containing them.

The manifest includes counts, field names and SHA-256 checksums. Faculty professional skills, resume summaries, research, training and collaboration records remain available in Staff Development; student and faculty trends and topic heatmaps remain tied to selected student IDs.
