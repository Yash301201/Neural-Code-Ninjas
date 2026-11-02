# Admin and HOD operations

Open http://127.0.0.1:8001/app/ and refresh the browser.

- Student Directory: filter by UG/PG, department, course/major, account status and name. Classification comes from active enrollments, not email or role. Unenrolled students remain under All. Counts use unique user IDs; students with multiple programs can appear in both program totals.
- Faculty & HOD Directory: profiles show department, teaching assignments, weekly slots and scheduled hours. Three fictional faculty profiles are labeled [DEMO], use demo.learnpath.invalid email addresses and cannot sign in. Existing credentials were preserved.
- HOD: Institution/Department Operations > Teaching coverage assigns an active department faculty member to a subject and section. Weekly Timetable then schedules that assigned class. Faculty sees their own assignments; HOD manages their department; admin oversees all departments.
- Admin: User Management creates accounts and roles. Institution Operations edits names, reference numbers and account status with a reason and audit trail. Existing academic history stays linked to user IDs. Department transfer and role conversion are not provided by the new directory.
- Extra controls: missing enrollment visibility, disabled-account filters, faculty workload details and existing audit logs.

Data persists in MySQL users, student_enrollments, course_programs, faculty_subject_assignments, faculty_timetable and campus_audit. No new schema was needed.

Verification: 25 tests passed using learnpath_ai_test; TypeScript and production build passed; live admin/HOD directory access and faculty/student denial verified.

Recovery note: a test-launcher error initially used the live database. Its records were restored from MySQL binary logs to the pre-test state and compared across all 42 tables before demo profiles were added. The suite now checks the actual engine database before any destructive fixture runs.
