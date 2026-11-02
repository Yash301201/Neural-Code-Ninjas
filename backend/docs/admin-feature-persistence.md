# Admin frontend-to-MySQL verification guide

Every successful supported data-changing form follows:

**Frontend Save → authenticated FastAPI validation → MySQL transaction → commit → refresh from MySQL.**

You do not need to manually run INSERT/UPDATE after saving a frontend form. The SQL file is for observing the saved result. It contains SELECT/WITH queries and connection-local SET/USE setup; no business rows are written or deleted by the verification pack.

Filters, tab changes, chart selection, opening a directory/profile and downloading a CSV are read-only interactions. They should not create duplicate academic rows. The current System Settings screen displays configuration status; it is not an editable database-settings form.

## How to use the SQL pack

1. Connect Workbench to the same MySQL instance as the backend (local port 3307, schema learnpath_ai).
2. Open **backend/db/017_admin_feature_verification.sql**. Run the setup block at the top once.
3. Change @subject_id, @section_id and @student_id to the IDs selected in the frontend. Set @actor_email to the signed-in administrator for feedback/profile/conversation checks. Then rerun dependent @course_id, @faculty_id, @assignment_id, @test_id and @session_id setup lines. The initial defaults choose the first subject/section; they are not automatically read from your browser.
4. In the frontend, perform one action and wait for success. For attendance, local Present/Absent clicks are not saved until you press the save button.
5. Refresh the page or sign out and in. In Workbench, select the matching numbered SQL section and run it. Match the record IDs and values.
6. A blank query result can be correct: for example, no successful AI generation, no feedback by that administrator, no saved exam draft, or no matching selected assignment. It is not an instruction to fabricate rows.

Example setup for the screenshot's first Data Structures class (verify IDs locally):

```sql
USE learnpath_ai;
SET @subject_id = 1;
SET @section_id = 1;
SET @student_id = 4;
SET @actor_email = 'admin@learnpath.dev';
```

Use User Management, Subjects and Sections queries to find IDs. To inspect a newly created assignment or test, set @assignment_id or @test_id to the returned record ID instead of assuming the largest ID belongs to the same class.

## Admin feature map

| Admin feature | SQL section | Frontend page | FastAPI operation(s) | MySQL records |
| --- | --- | --- | --- | --- |
| Years, Curriculum & Teaching | 02 | `/admin/curriculum` | PUT /api/academics/sections/{id}/year; PUT /api/academics/teaching/{id}/topics/{topic_id} | section_study_years, subject_curriculum, faculty_subject_assignments, topics, teaching_topic_progress |
| AI Question Generator | 03 | `/admin/question-generator` | POST /api/ai/questions | questions, ai_generation_history |
| Answer Evaluation | 04 | `/admin/evaluation` | PATCH /api/answers/{id}/grade; POST /api/ai/answers/{id}/feedback | student_answers, test_attempts, ai_generation_history |
| Exam Performance | 05 | `/admin/performance-insights` | GET /api/development/learner-insights | tests, test_attempts, test_questions, questions, topics, student_answers |
| Colleague Feedback | 06 | `/admin/teaching-feedback` | PUT /api/development/feedback | staff_feedback |
| Staff Development | 07 | `/admin/staff-development` | POST /api/development/staff/{id}/evidence; PUT /api/development/evidence/{id}; PATCH /api/development/evidence/{id}/review; DELETE /api/development/evidence/{id} | staff_evidence, campus_audit |
| Academic Data Centre | 08 | `/admin/academic-data` | GET /api/college-data/catalog | users, courses, departments, course_programs, sections, student_enrollments, faculty_subject_assignments, subjects, tests, student_answers |
| Question Bank | 09 | `/admin/question-bank` | POST /api/questions; PUT /api/questions/{id}; PATCH /api/questions/{id}/review | questions, topics |
| Assignments | 10 | `/admin/assignments` | POST /api/assignments; POST /api/assignments/{id}/submit (student); PATCH /api/submissions/{id}/grade | assignments, submissions, student_enrollments, users |
| Student Directory | 11 | `/admin/student-directory` | GET /api/campus/management | users, student_enrollments, sections, courses, course_programs, section_study_years |
| Faculty & HOD Directory | 12 | `/admin/staff-directory` | GET /api/campus/management | users, departments, faculty_subject_assignments |
| Institution Operations | 13 | `/admin/management` | PATCH /api/campus/people/{id}; POST /api/campus/teaching; GET /api/campus/audit | users, faculty_subject_assignments, student_enrollments, campus_audit |
| Exam Studio | 14 | `/admin/exam-studio` | POST /api/campus/exam-series; POST /api/tests; PATCH /api/tests/{id}/status | tests, test_questions, exam_series, exam_schedules, test_attempts, exam_answer_drafts |
| Attendance Register | 15 | `/admin/attendance` | POST /api/campus/attendance/register | class_sessions, attendance_records, attendance_registers, campus_audit |
| Learner Register | 16 | `/admin/learner-register` | GET /api/faculty-ops/class-register | student_enrollments, attendance_records, class_sessions, assignments, submissions, tests, test_attempts |
| Weekly Timetable | 17 | `/admin/timetable` | POST /api/faculty-ops/timetable; DELETE /api/faculty-ops/timetable/{id} | faculty_timetable, campus_audit |
| Faculty Leave Approvals | 18 | `/admin/faculty-leave` | PATCH /api/faculty-ops/leave/{id}/review | faculty_leave_requests, users, campus_audit |
| UG / PG Programs | 19 | `/admin/programs` | PUT /api/faculty-ops/programs/{course_id} | courses, course_programs, campus_audit |
| AI Knowledge Assistant | 20 | `/admin/rag-assistant` | POST /api/rag/ask; POST /api/rag/reindex | rag_conversations, rag_messages, rag_chunks |
| Engineering Dataset | 21 | `/admin/dataset-analytics` | GET /api/college-data | users, courses, departments, sections, student_enrollments, faculty_subject_assignments, section_study_years, subject_curriculum and academic-result tables |
| Dashboard | 01 / 22 | `/admin` | GET /api/portal/workspace; POST /api/study-plans when explicitly requested | student_enrollments, tests, test_attempts, test_questions, student_answers, attendance_records, class_sessions, study_plans, study_plan_items |
| User Management | 23 | `/admin/users` | POST /api/users; PATCH /api/users/{id}/status; PATCH /api/portal/users/{id}/password; POST /api/enrollments; POST /api/faculty-assignments | users, student_enrollments, faculty_subject_assignments |
| Departments | 24 | `/admin/departments` | POST /api/departments; PUT /api/departments/{id} | departments, campus_audit |
| Courses | 25 | `/admin/courses` | POST /api/courses; PUT /api/courses/{id} | courses, course_programs, campus_audit |
| Subjects | 26 | `/admin/subjects` | POST /api/subjects; PUT /api/subjects/{id} | subjects, subject_curriculum, campus_audit |
| Topics | 27 | `/admin/topics` | POST /api/topics; PUT /api/topics/{id} | topics, campus_audit |
| Sections | 28 | `/admin/sections` | POST /api/sections; PUT /api/sections/{id} | sections, student_enrollments, section_study_years, campus_audit |
| Academic Calendar | 29 | `/admin/calendar` | POST /api/academic_events | academic_events, campus_audit |
| System Settings | 30 | `/admin/settings` | GET /api/portal/workspace; GET /health | No editable settings table: database connectivity plus backend environment configuration |
| Profile | 31 | `/admin/profile` | GET /api/auth/me; GET /api/portal/workspace | users, departments |

## What each save/read proves

### Years, Curriculum & Teaching — SQL 02

Save a cohort year or topic status, refresh, then compare the section/assignment/topic IDs.

### AI Question Generator — SQL 03

A successful provider response saves GENAI drafts as PENDING_REVIEW plus generation history. An unavailable provider saves no pretend result.

### Answer Evaluation — SQL 04

Final marks and feedback are stored in student_answers; evaluated attempt totals are recomputed. AI suggestions are saved in generation history and require teacher review.

### Exam Performance — SQL 05

Read-only trend and topic heatmap. Compare the same student, subject and section.

### Colleague Feedback — SQL 06

Saving the same author/recipient/context updates the same feedback row. The profile shows averages only after three responses.

### Staff Development — SQL 07

Create, edit, review and archive evidence. Editing resets review state; archive retains an ARCHIVED row.

### Academic Data Centre — SQL 08

Read-only summary of stored records. Student/faculty/HOD cards count the prefilled account collection; course-level enrollment counts also include existing accounts.

### Question Bank — SQL 09

Create/edit/review questions. Questions used by published or closed tests are frozen; use a new question instead.

### Assignments — SQL 10

Create an assignment, submit as an enrolled student and grade. Coverage counts use active, enabled student roster members.

### Student Directory — SQL 11

Directory is a read view. Account/profile/enrollment changes are made through the linked management forms.

### Faculty & HOD Directory — SQL 12

Directory and profile summaries read the same user and teaching records, not separate copies of staff.

### Institution Operations — SQL 13

Profile/status updates and teaching assignments persist. Use IDs and the latest audit entries as proof.

### Exam Studio — SQL 14

Finite daily/weekly/final schedules start as drafts, then publish. Student attempts and saved drafts are separate records.

### Attendance Register — SQL 15

Only Save class attendance/Save correction writes the register. Counts before saving can reflect unsaved marks. Corrections increment the register version and keep an audit.

### Learner Register — SQL 16

Read-only combined view of the selected class. Missing submissions are derived by joining the roster to submission rows.

### Weekly Timetable — SQL 17

Adding saves a slot. Archive sets is_active=0; it does not erase timetable history.

### Faculty Leave Approvals — SQL 18

Approval/rejection saves status, reviewed_by, review_note and reviewed_at. Request and cancellation originate from staff accounts.

### UG / PG Programs — SQL 19

The degree ID stays the same; program_level is saved in its linked course_programs row.

### AI Knowledge Assistant — SQL 20

Question, answer, answer mode and citations persist. Conversations are owner-scoped. Reindex updates the separate public knowledge index.

### Engineering Dataset — SQL 21

Read-only linked dataset. It uses the same saved MySQL records; downloading a CSV does not insert another copy into MySQL.

### Dashboard — SQL 01 / 22

Charts/cards are calculated from saved data. Changing a filter changes the view, not grades or enrollment. The SQL reproduces the API weighted-score calculation.

### User Management — SQL 23

Accounts, statuses, enrollments and teaching mappings persist. Password reset stores an Argon2 hash, never the original password. Compare the hash fingerprint before/after.

### Departments — SQL 24

Saved name/code appears on the same department_id. Catalog saves now record before/after fields in the audit.

### Courses — SQL 25

Degree name/code/duration and program classification save in one transaction. Existing curriculum/cohort years cannot be removed by shortening the duration.

### Subjects — SQL 26

For a classified subject, a same-year semester edit updates both subject and curriculum rows. Moving a taught subject to another year/course is rejected to preserve history.

### Topics — SQL 27

Name/description updates persist. A topic with linked questions, progress or history cannot be moved to another subject.

### Sections — SQL 28

Calendar year and section name persist. Year of study is classified separately through the Years page. A used section cannot be moved to another course.

### Academic Calendar — SQL 29

Add event saves title, start/end dates and description. The API also supports catalog updates; the current calendar screen exposes Add event.

### System Settings — SQL 30

This screen displays status. LLM keys and JWT secret stay in backend/.env. There is no Save settings action, and a chart/filter click does not create a settings row.

### Profile — SQL 31

Read-only current account identity. Changes saved through Institution Operations update this same user row.

## Important verification details

- Dashboard and Academic Data Centre use different scopes. Dashboard cards use the selected subject/section; the Data Centre account cards count the prefilled account collection. Do not expect those counts to match.
- The dashboard query deliberately matches app/analytics.py: roster from the selected active section; weighted evaluated answer marks and attendance across that student's history in the selected subject. Exam Performance and Learner Register are class-specific. Missing observations stay NULL, not invented zeros.
- The Academic Data Centre card labeled Evaluated answers currently counts stored student_answers rows. The query pack includes a separate count where awarded_marks IS NOT NULL, so you can distinguish stored rows from scored rows.
- Passwords are not saved as JWTs. users.password_hash holds Argon2 hashes. The pack uses an algorithm check and a SHA-256 fingerprint of the stored hash as password-reset evidence, without exporting passwords or full hashes.
- Archive/disable operations retain records with status/is_active changes. Generic permanent deletion is not provided for every entity. Do not manually DELETE rows to simulate an unavailable UI action.
- campus_audit records workflow changes implemented with auditing, including the newly audited catalog saves. It is not a universal database trigger logging every external Workbench edit or every application action. The underlying feature tables remain the primary evidence.
- CSV snapshots in backend/data/engineering are regenerated explicitly. They are not a second automatically synchronized database. The frontend reads MySQL through FastAPI.
- AI suggestions do not silently change final marks. Successful AI requests save history; teachers explicitly save reviewed grades or approve question drafts.
- Direct Workbench queries do not enforce the application's role permissions. Use an authorized local administrator connection; use the application to test role isolation.

## Persistence issue fixed in this change

A subject semester edit could previously update subjects.semester while subject_curriculum.semester remained stale and the UI reused the old curriculum value. The API now saves both rows in one transaction for an allowed same-year edit. It rejects moving taught/history-linked subjects to another year/course, moving used sections/topics across parents, and shortening a course below existing cohort/curriculum years. Catalog create/edit actions save their public before/after fields in campus_audit. No passwords or provider secrets are placed in those entries.

## Suggested evaluator evidence

Create a small verification account/assignment through the UI, inspect its ID in SQL, edit an allowed field, reload and compare the same ID. Save attendance, grade one submission, update topic coverage, review staff evidence and approve a leave request. Record expected value, API outcome, matching SQL row and pass/fail. Do destructive or exhaustive automated checks only in learnpath_ai_test.

## Validation

All 30 admin menu routes are covered by this map. All 53 read queries plus 11 connection-local setup statements executed successfully against the configured local MySQL database without changing business rows. 31 integration tests pass against learnpath_ai_test, including semester synchronization, history-preserving edit rejection, catalog audit creation and calendar persistence. Existing student/faculty/HOD/admin credentials and application data were not changed by the verification queries.
