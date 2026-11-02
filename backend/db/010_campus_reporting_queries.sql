-- Read-only queries for the live application database.
USE learnpath_ai;
SELECT cs.session_id, cs.session_date, s.subject_name, ar.student_id, u.full_name, ar.status
FROM class_sessions cs JOIN subjects s ON s.subject_id=cs.subject_id
JOIN attendance_records ar ON ar.session_id=cs.session_id JOIN users u ON u.user_id=ar.student_id
ORDER BY cs.session_date DESC, cs.session_id DESC, ar.student_id;
SELECT ar.student_id, u.full_name, COUNT(*) AS recorded_classes,
SUM(ar.status='PRESENT') AS present, SUM(ar.status='ABSENT') AS absent,
SUM(ar.status='LATE') AS late, SUM(ar.status='LEAVE') AS on_leave
FROM attendance_records ar JOIN users u ON u.user_id=ar.student_id GROUP BY ar.student_id,u.full_name;
SELECT t.test_id, t.title, s.subject_name, e.exam_type, t.status, t.start_at, t.end_at
FROM tests t JOIN exam_schedules e ON e.test_id=t.test_id JOIN subjects s ON s.subject_id=t.subject_id ORDER BY t.start_at;
SELECT audit_id, actor_id, action, entity_type, entity_id, reason, created_at FROM campus_audit ORDER BY audit_id DESC LIMIT 100;
