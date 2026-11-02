-- Read-only evaluator queries for the configured application database.
USE learnpath_ai;
SELECT c.course_id,c.course_name,d.department_name,cp.program_level
FROM courses c JOIN departments d ON d.department_id=c.department_id
LEFT JOIN course_programs cp ON cp.course_id=c.course_id ORDER BY c.course_id;

-- Current active roster counts per assignment. This never assumes a class size of 50.
SELECT a.assignment_id,a.title,d.department_name,c.course_name,
COALESCE(cp.program_level,'UNCLASSIFIED') AS program_level,sec.section_name,s.subject_name,
COUNT(DISTINCT u.user_id) AS active_enrolled,
COUNT(DISTINCT CASE WHEN sub.submission_id IS NOT NULL THEN u.user_id END) AS submitted,
COUNT(DISTINCT u.user_id)-COUNT(DISTINCT CASE WHEN sub.submission_id IS NOT NULL THEN u.user_id END) AS not_submitted
FROM assignments a JOIN subjects s ON s.subject_id=a.subject_id
JOIN sections sec ON sec.section_id=a.section_id JOIN courses c ON c.course_id=sec.course_id
JOIN departments d ON d.department_id=c.department_id LEFT JOIN course_programs cp ON cp.course_id=c.course_id
LEFT JOIN student_enrollments e ON e.section_id=sec.section_id AND e.status='ACTIVE'
LEFT JOIN users u ON u.user_id=e.student_id AND u.role='STUDENT' AND u.is_active=1
LEFT JOIN submissions sub ON sub.assignment_id=a.assignment_id AND sub.student_id=u.user_id
GROUP BY a.assignment_id,a.title,d.department_name,c.course_name,cp.program_level,sec.section_name,s.subject_name;

SELECT tt.slot_id,u.full_name,s.subject_name,c.course_name,cp.program_level,
tt.weekday,tt.starts_at,tt.ends_at,tt.room,tt.session_type,tt.is_active
FROM faculty_timetable tt JOIN users u ON u.user_id=tt.faculty_id
JOIN subjects s ON s.subject_id=tt.subject_id JOIN courses c ON c.course_id=s.course_id
LEFT JOIN course_programs cp ON cp.course_id=c.course_id ORDER BY tt.weekday,tt.starts_at;

SELECT l.leave_id,u.full_name,l.start_date,l.end_date,l.leave_type,l.status,
r.full_name AS reviewed_by,l.reviewed_at
FROM faculty_leave_requests l JOIN users u ON u.user_id=l.requester_id
LEFT JOIN users r ON r.user_id=l.reviewed_by ORDER BY l.leave_id DESC;
