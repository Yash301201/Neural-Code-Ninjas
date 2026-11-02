# LearnPathAI classroom and exam upgrade

The project now has connected role-specific classroom workflows backed by FastAPI and MySQL.

## Faculty

- Attendance: choose subject, section, class date, and start time. Absent is on the left and Present on the right for each learner. Counts update as you click. Nothing is assumed for an unmarked student.
- Save only after every learner has a mark. The backend commits the whole class together. Optional Late and Leave statuses remain supported.
- Student totals: present, absent, late, leave, recorded-class count, and attendance percentage for each student ID. CSV export is available.
- Class history: filter by student ID and reopen a session. Corrections require a reason and create an audit entry. Version checks prevent silently overwriting another teacher's saved correction.
- Exam Studio: select the subject and section, choose approved MCQs, and set Daily, Weekly, or Final schedules. Daily means every calendar day, including weekends. Weekly means every seven days. Final creates one paper.
- A finite schedule creates up to 30 draft exams for the selected subject. Repeat the setup for each subject. The selected paper repeats across occurrences; no background process invents new questions. Review each paper before publishing.

## Students

- Attendance shows their own present/absent totals, recorded classes, percentage, class history and an overview across enrolled subjects.
- Online Tests separates Daily, Weekly, Final and earlier Practice assessments. Dates and opening windows use local display time, while the backend stores UTC.
- Scheduled MCQ selections autosave to MySQL. The timer uses the earlier of attempt duration or exam closing time. At expiry, the browser finalizes only server-saved answers. The server refuses answer changes after the deadline.
- If a browser closes or disconnects, use Start / resume while the exam window is open, or Submit saved answers in result history to finalize an in-progress scheduled exam. Answers never saved before the deadline cannot receive credit. Network loss may require the learner to return and finalize saved work; there is no background worker finalizing closed browser tabs.
- Each scheduled exam permits one attempt. Existing practice papers keep their existing attempt limits and behavior. Older practice papers may include non-MCQ questions.

## HOD

Department Operations shows only department student/faculty records, active account counts, enrollment counts and teaching workload. The HOD can edit names/reference numbers and active status for those users, assign teaching for department subjects and sections, export a directory, and view department campus activity history. HODs cannot promote roles, edit administrators or manage another department's people.

## Admin

Institution Operations provides a directory for students, faculty, HODs and administrators, audited profile maintenance, teaching coverage and campus activity history. Existing User Management handles creation, role selection and password resets. Existing academic mapping handles enrollment. Existing catalog screens manage departments, courses, subjects, sections and topics. Account disabling preserves academic history.

Creating a subject saves it in the catalog. Teaching assignment is a separate operation under Institution/Department Operations > Teaching coverage. Faculty receives a clear message after subject creation rather than an implication that it is automatically assigned.

## Charts

Private academic charts now require a selected learner and show the student ID. Attendance uses counts and tables instead of unnecessary charts. The public OULAD research explorer remains a separately labeled research page and does not represent live college attendance.

## Database changes

The additive migration backend/db/009_campus_workflows.sql has already been applied to the configured local learnpath_ai database. It creates:

| Table | Data |
|---|---|
| attendance_registers | Session version, last editor and update time |
| campus_audit | Attendance corrections, management changes, teaching assignments and exam-series actions |
| exam_series | Idempotent scheduling request identity |
| exam_schedules | Daily/Weekly/Final metadata linked to existing tests |
| exam_answer_drafts | Student MCQ selections saved before the exam deadline |

Existing class_sessions, attendance_records, tests, test_questions, test_attempts and student_answers remain the academic system of record. Existing accounts, emails, passwords and provider/JWT keys remain unchanged.

For another installation, apply the migration explicitly:

```powershell
cd backend
.\.venv\Scripts\python.exe -m scripts.setup_campus
```

Fresh database initialization and Compose initialization include the new schema. Existing Docker volumes need the explicit migration. Re-running setup_campus leaves existing rows intact.

In MySQL Workbench connected to 127.0.0.1:3307, select learnpath_ai and run the read-only queries in backend/db/010_campus_reporting_queries.sql to see saved attendance, scheduled exams and recent actions. UI filters and unsaved button selections remain browser state until Save.

## Run and verify

The integrated application runs at http://127.0.0.1:8001/app/. Reload the browser to load the new frontend. After Python changes, stop the old API process and restart through start-project.ps1. Do not run a second backend on the same port.

Verification: 20 MySQL-backed integration tests passed in the isolated learnpath_ai_test database and the TypeScript/Vite production build passed. Checks cover roster completeness, attendance ownership/corrections, stale version rejection, schedule idempotency, future windows, MCQ-only schedules, department access, persisted answers and late-answer rejection. One existing Starlette/httpx deprecation warning remains.

Browser checks verified faculty login, live Present/Absent counts, per-student totals, historical register reopening and MCQ scheduling controls. Browser test clicks were left unsaved to avoid adding artificial attendance to existing student histories. End-to-end database write tests ran in the disposable test database.
