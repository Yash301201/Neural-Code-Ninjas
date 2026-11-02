-- Read-only showcase reports. Run in MySQL Workbench connected to port 3307.
USE learnpath_ai;
SELECT u.role,COUNT(*) AS demo_accounts FROM users u
WHERE u.email LIKE '%@demo.learnpath.dev' GROUP BY u.role;

SELECT cp.program_level,c.course_name,sec.section_name,COUNT(DISTINCT u.user_id) AS demo_students
FROM student_enrollments e JOIN users u ON u.user_id=e.student_id
JOIN sections sec ON sec.section_id=e.section_id JOIN courses c ON c.course_id=sec.course_id
LEFT JOIN course_programs cp ON cp.course_id=c.course_id
WHERE u.email LIKE '%@demo.learnpath.dev' AND e.status='ACTIVE'
GROUP BY cp.program_level,c.course_name,sec.section_name;

SELECT u.user_id,u.full_name,d.department_name,COUNT(DISTINCT f.faculty_assignment_id) AS teaching_mappings,
COUNT(DISTINCT tt.slot_id) AS weekly_slots FROM users u
LEFT JOIN departments d ON d.department_id=u.department_id
LEFT JOIN faculty_subject_assignments f ON f.faculty_id=u.user_id
LEFT JOIN faculty_timetable tt ON tt.faculty_id=u.user_id AND tt.is_active=1
WHERE u.role='FACULTY' AND u.email LIKE '%@demo.learnpath.dev'
GROUP BY u.user_id,u.full_name,d.department_name;

SELECT u.full_name,ev.category,ev.title,ev.status,ev.skill_level,reviewer.full_name AS reviewed_by
FROM staff_evidence ev JOIN users u ON u.user_id=ev.owner_id
LEFT JOIN users reviewer ON reviewer.user_id=ev.reviewed_by
WHERE u.email LIKE '%@demo.learnpath.dev' ORDER BY u.user_id,ev.evidence_id;

-- Specific student exam history. Change this email to another demo student.
SELECT u.user_id,u.full_name,t.title,a.status,a.score,maxima.max_marks,
ROUND(100*a.score/NULLIF(maxima.max_marks,0),1) AS exam_percentage
FROM test_attempts a JOIN users u ON u.user_id=a.student_id JOIN tests t ON t.test_id=a.test_id
JOIN (SELECT test_id,SUM(marks) AS max_marks FROM test_questions GROUP BY test_id) maxima ON maxima.test_id=t.test_id
WHERE u.email='student-001@demo.learnpath.dev' ORDER BY a.submitted_at;

SELECT c.course_name,l.batch_id,l.code_module,l.code_presentation,i.status AS import_status
FROM course_dataset_links l JOIN courses c ON c.course_id=l.course_id
JOIN oulad_imports i ON i.batch_id=l.batch_id;

SELECT action,COUNT(*) AS recorded_actions FROM campus_audit
WHERE reason LIKE '%demo%' OR reason LIKE '%fictional%' OR action LIKE 'EVIDENCE%'
GROUP BY action;
