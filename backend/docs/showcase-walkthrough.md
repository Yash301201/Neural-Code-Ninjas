# LearnPathAI four-role demo walkthrough

> Dataset update: the main Engineering Dataset now uses named MySQL college records. OULAD is a separate optional research explorer. See [the engineering dataset guide](engineering-dataset.md) for current CSV exports.

Open http://127.0.0.1:8001/app/login and refresh after the update.

## Demo accounts

All the accounts below use the local demo password `DemoLearn2026!`.
Choose the matching role on the login screen.

| Role | Email |
| --- | --- |
| Student | student-001@demo.learnpath.dev |
| Faculty | faculty-1@demo.learnpath.dev |
| HOD | hod-1@demo.learnpath.dev |
| Admin | admin-showcase@demo.learnpath.dev |

Existing non-demo account credentials were preserved. Demo names include [DEMO]; records use dedicated DEMO-Showcase sections. Demo accounts are active for this local demonstration. Passwords in MySQL are Argon2 hashes; JWTs authorize sessions and do not store passwords.

## What was populated

50 synthetic students total across the three existing courses (not 50 per course):

- B.Tech Computer Science and Engineering, UG: 17.
- Master of Computer application, PG: 17.
- Master of technology, PG: 16.

Seven synthetic faculty, one synthetic HOD and one synthetic admin. The previous three disabled demo faculty profiles were reused and enabled as part of the seven; non-demo faculty were not changed.

There are two demo subjects per course, 36 scheduled MCQ papers across daily/weekly/final categories (completed examples and published practice windows), 1,380 evaluated answers, class attendance, submitted/graded/missing assignments, study plans, teaching mappings, seven weekly timetable slots, leave requests and staff portfolios. All synthetic academic data is clearly labeled. Research titles, resumes and feedback are fictional examples; they are not claims about real people or publications.

## Student demonstration

1. Sign in as Student. Demo accounts initially select a demo subject.
2. Open Exam Performance. One line shows this student's exam percentage in the selected subject. The topic-by-exam heatmap shows numeric marks percentages: green >=75, amber 40–74, red below 40, grey not assessed. It is not an attendance or personality score.
3. Change subject / UG-PG course where enrolled. Access to another student's results is denied by the backend.
4. Open Online Test / Exam Studio to take a published daily practice paper. Weekly and final practice windows show their scheduled opening times. Completed examples remain in result history; closed papers cannot be started.
5. Open Assignments to see marks and feedback, or submit a missing response. Attendance shows actual saved demo class records.
6. Teaching Feedback lets the student rate only a faculty member assigned to their enrolled class. Saving again updates the same response. The author ID is retained in MySQL, so this is confidential rather than anonymous.

## Faculty demonstration

1. Sign in as Faculty. Use UG/PG course, subject and section controls to select assigned classes.
2. Assignments shows actual eligible, submitted, missing, awaiting grading and graded counts. Review a response, save marks/feedback and export the register.
3. Learner Register and Exam Performance let the faculty select an authorized student ID and inspect that student's marks and topic heatmap.
4. Attendance supports roll call and saved corrections with a reason. Weekly Timetable shows assigned teaching slots. Leave Requests shows example statuses and allows a new request.
5. My Professional Portfolio contains skills (explicitly self-rated), a fictional resume summary, research examples, training and collaboration evidence. Add, edit or archive a record. Edits to verified records return them to SUBMITTED status for review.
6. Student feedback and colleague feedback are shown separately. Averages are hidden until three responses; individual respondent names and comments are not exposed on the portfolio. They are subjective ratings, not an objective ranking.
7. The portfolio includes an archived demo training record and audit trail to illustrate create, modify and archive operations.

## HOD demonstration

The HOD can use faculty classroom tools across their own department: attendance, learner results, assignments, question bank, exam studio, answer evaluation and AI question generation (if a provider is configured).

Department Operations > Teaching coverage assigns an active department faculty member to a subject and section. Weekly Timetable schedules that mapping and rejects overlapping faculty or class-section times.

Staff Development lets the HOD review department faculty evidence, verify or return it with a note, and view separate research and feedback summaries. HOD cannot verify their own evidence. Faculty leave approvals are department-scoped. Student and staff directories are grouped by program/major and department.

## Admin demonstration

Admin has institution-wide access to the HOD and faculty management workflows, including student/staff directories, accounts, status maintenance, teaching coverage, timetable, exams, assignments, portfolio reviews, HOD evidence review and leave decisions. Individual students still take their own exams; administration does not impersonate them.

Demo Showcase & Dataset Link shows the generated totals and reference links. Re-running the same demo generation is idempotent and does not duplicate the cohort. It will not layer a different requested cohort size over an existing run.

## OULAD connection

The existing READY OULAD import in MySQL is linked to each demo course through course_dataset_links. The initial reference is BBB / 2014J. Admin can select another real imported cohort.

The OULAD reference is retained in the research API; the college Exam Performance screen shows the selected student’s own exams. The cohort has different learners, assessments and curriculum: its average is context only, not a student ranking or a prediction. Imported VLE clicks are not classroom attendance. Synthetic college exam answers were not copied from OULAD.

Dataset Analytics retains the original source attribution, research learner IDs and labeled fictional display aliases. Use it to inspect a selected research learner independently of college student IDs. No fabricated model accuracy or outcome improvements are shown.

## Database proof

Open backend/db/014_showcase_reporting.sql in Workbench connected to 127.0.0.1:3307, schema learnpath_ai. These are read-only reports for accounts, program counts, faculty workload, evidence, specific-student exam marks and OULAD links.

New schema: backend/db/013_showcase_development.sql. New data stays in MySQL, including staff_evidence, staff_feedback, course_dataset_links and demo_showcase_runs, alongside the existing academic tables.

Setup on a fresh checkout (from backend):

```powershell
.\.venv\Scripts\python.exe -m scripts.setup_showcase
# Existing OULAD import must be READY before generating the showcase.
.\.venv\Scripts\python.exe -m scripts.create_showcase
```

The admin UI can generate the same demo. DEMO_SHOWCASE_PASSWORD can override the default only at initial creation. Do not edit a JSON login file expecting an automatic password reset.

Run backend tests safely:

```powershell
.\.venv\Scripts\python.exe -m scripts.check_backend
```

The launcher uses a fresh process and the suite checks the actual SQLAlchemy engine points to learnpath_ai_test before any fixture resets data. A private pre-change backup was saved outside the repository.

## Verification and limits

27 MySQL integration tests pass, including additive/idempotent demo generation, password preservation, role scope, staff review, feedback privacy, email login, default demo scope, result history and OULAD reference calculations. TypeScript and Vite production build pass. Live role logins and the student heatmap/dataset reference were checked through the API.

Visual browser verification could not be completed because the computer-use tool stopped when it could not reliably determine the browser URL. No new screenshots are claimed. No remote Git push was performed.
