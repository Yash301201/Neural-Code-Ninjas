# LearnPathAI faculty UG/PG operations

The requested faculty features are implemented across React, FastAPI and MySQL. Counts use actual active enrolled students only. No 50-student demo cohort or new login credentials were created.

## Assignment submission counts

Open Assignments, then select Program level, Course, Subject and Section. Every assignment shows Submitted, Pending/Not submitted, Enrolled, Graded and Awaiting grading counts. View submitted and pending students opens the class register, filters completion status, reads the answer and saves marks/feedback. Export register produces a CSV with program, course and student ID.

The denominator is the current active roster, not a fixed class size. In the verified existing Data Structures class, the saved data showed 3 enrolled, 1 submitted and 2 pending. That count will change as enrollment and submissions change. Missing-submission totals across assignments count missing pieces of work; the same learner can contribute more than once. Historical submissions outside the current active roster remain in MySQL and are counted separately.

## UG and PG separation

An additional course_programs table classifies each existing course as UG, PG or UNCLASSIFIED. The existing B.Tech course is UG, and the existing Master of Computer application and Master of technology courses are PG. Unknown courses remain unclassified until an HOD/admin chooses their level.

HOD/admin: open UG / PG Programs to correct classification. New courses can specify program level in the course form. Teaching access still requires an actual faculty subject/section assignment under Department/Institution Operations > Teaching coverage.

Faculty: My Subjects groups assigned subjects under Undergraduate, Postgraduate and Unclassified. The Program/Course selector now appears in attendance, assignments, exam scheduling, question-bank workflows and academic scope screens. Selecting a program with no assigned subjects displays an empty state instead of unrelated records.

Existing tables store academic data with subject_id, section_id and student_id. Those IDs relate to courses and course_programs. UG and PG do not need duplicate databases or duplicate student records. Queries use the exact subject/section/course relationships to keep marks, attendance and coursework separate. No department or role privileges were expanded beyond the requested operations.

## Learner Register and faculty duties

The new Learner Register combines each class's student IDs with attended/recorded classes, absences, assignment completion and evaluated exam percentage. View records shows individual assignment marks and exam attempt scores. The percentage weights the marks available in evaluated attempts and excludes unfinished/ungraded attempts. These calculations use the selected subject and section, including when a faculty member teaches both UG and PG.

The existing Question Bank and AI Question Generator remain available for creating/reviewing questions. My Subjects now provides a Create questions shortcut for each assigned subject. Exam Studio remains the scheduling/publishing interface. Students see their own published papers after starting an authorized attempt. The new assignment register adds a grading queue and missing-work list without adding unnecessary graphs.

## Weekly timetable

Faculty: Weekly Timetable displays active classes by weekday, sorted from morning to evening, with start/end times, UG/PG label, course, section, room and session type. Counts show UG/PG teaching load and contact hours.

HOD/admin: choose a faculty member in Weekly Timetable, click Schedule class, choose an existing assigned subject/section, then enter weekday, start/end, room and Lecture/Lab/Tutorial. The backend rejects overlapping active slots for the same faculty member or class section. Archive removes a weekly slot from the active view and preserves academic attendance history.

No synthetic timetable was added. Save the actual department schedule to populate it. Weekly clock times represent campus local time. Archive old active schedules when the academic year changes. Room names are descriptive; room-level collision checking is not implemented.

## Faculty leave requests

Faculty: My Leave Requests > Request leave supports dates, type and brief reason. Requests are at most 31 calendar days. Overlapping pending/approved requests are rejected. Faculty can withdraw their own pending request.

HOD: Faculty Leave Approvals lists department faculty requests plus the HOD's own requests. The HOD can approve/reject department faculty requests with a reviewer note. Admin can review faculty and HOD requests. Nobody can approve their own request. Reviewed requests retain the reviewer and decision timestamp.

The list shows affected weekly class count for the date range so coordinators can arrange coverage. Approval does not automatically cancel classes, alter attendance or notify people by email. Day totals are calendar days, including weekends; there is no policy-specific leave balance or payroll integration.

## MySQL additions

Migration backend/db/011_faculty_operations.sql is already applied locally:

| Table | Persistent records |
|---|---|
| course_programs | Course classification |
| faculty_timetable | Weekly teaching slots and active/archive state |
| faculty_leave_requests | Requests, status, reviewer and timestamps |

Existing assignments/submissions, attendance_records/class_sessions and tests/test_attempts/student_answers continue to store academic data. Existing campus_audit records program, timetable and leave workflow changes. The shared audit log records leave status events, not private leave reason text.

For another existing database, run from backend:

```powershell
.\.venv\Scripts\python.exe -m scripts.setup_faculty
```

Fresh schema initialization and Compose initialization include this migration. Existing Docker volumes require an explicit schema update. The setup script classifies recognizable B.Tech/M.Tech/master course names when first creating program mappings and leaves existing mappings unchanged.

Use backend/db/012_faculty_reporting_queries.sql in MySQL Workbench to demonstrate course levels, class submission counts, timetable records and leave decisions. These queries contain no password fields.

## Validation and delivery

24 MySQL-backed integration tests passed in isolated learnpath_ai_test. The TypeScript/Vite production build passed. Tests cover real-roster counts, submission grading, UG/PG learner isolation, section validation, timetable collisions/adjacency, leave overlap, authorization, self-approval prevention and decision history. One existing Starlette/httpx deprecation warning remains.

Browser verification covered faculty login, assignment counts and student completion rows, UG scope labels, leave request controls and program-aware navigation. No artificial leave requests, timetable slots or academic marks were added to the live database for testing. Backend write tests use the disposable test database.

The local app is running on http://127.0.0.1:8001/app/. Reload the browser to load the new frontend. Existing emails, passwords, JWT secret and provider keys remain unchanged. Source changes are mirrored into the local Neural-Code-Ninjas repository, with no new remote push in this task.
