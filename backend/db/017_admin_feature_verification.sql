-- LearnPathAI admin feature-by-feature database verification.
-- READ-ONLY business data: SELECT / WITH / SHOW plus session-variable SET / USE only.
-- Do NOT run INSERT or UPDATE after saving a frontend form. FastAPI already saves it.
-- Choose the same subject, section, student and signed-in administrator as the UI.
USE learnpath_ai;
SET @subject_id = (SELECT MIN(subject_id) FROM subjects);
SET @course_id = (SELECT course_id FROM subjects WHERE subject_id=@subject_id);
SET @section_id = (SELECT MIN(section_id) FROM sections WHERE course_id=@course_id);
SET @student_id = (SELECT MIN(student_id) FROM student_enrollments WHERE section_id=@section_id AND status='ACTIVE');
SET @actor_email = 'admin@learnpath.dev';
SET @actor_id = COALESCE((SELECT user_id FROM users WHERE email=@actor_email LIMIT 1),(SELECT MIN(user_id) FROM users WHERE role='ADMIN'));
SET @faculty_id = (SELECT MIN(faculty_id) FROM faculty_subject_assignments WHERE subject_id=@subject_id AND section_id=@section_id);
SET @assignment_id = (SELECT MAX(assignment_id) FROM assignments WHERE subject_id=@subject_id AND section_id=@section_id);
SET @test_id = (SELECT MAX(test_id) FROM tests WHERE subject_id=@subject_id AND section_id=@section_id);
SET @session_id = (SELECT MAX(session_id) FROM class_sessions WHERE subject_id=@subject_id AND section_id=@section_id);
SELECT @actor_id AS administrator_id,@subject_id AS subject_id,@section_id AS section_id,@student_id AS student_id,@faculty_id AS faculty_id;

-- 01 / 22. DASHBOARD: matches the API's per-student weighted score and subject-wide attendance.
-- Current active section enrollments select the roster. Subject history covers all sections,
-- as implemented in app/analytics.py. Missing observations stay NULL, not zero.
WITH roster AS (
 SELECT DISTINCT u.user_id FROM users u JOIN student_enrollments e ON e.student_id=u.user_id
 WHERE u.role='STUDENT' AND e.section_id=@section_id AND e.status='ACTIVE'
), scores AS (
 SELECT a.student_id,ROUND(100*SUM(COALESCE(sa.awarded_marks,0))/NULLIF(SUM(tq.marks),0),2) AS score_percent
 FROM test_attempts a JOIN tests t ON t.test_id=a.test_id JOIN test_questions tq ON tq.test_id=t.test_id
 LEFT JOIN student_answers sa ON sa.attempt_id=a.attempt_id AND sa.question_id=tq.question_id
 WHERE a.status='EVALUATED' AND t.subject_id=@subject_id GROUP BY a.student_id
), attendance AS (
 SELECT ar.student_id,ROUND(100*SUM(ar.status IN ('PRESENT','LATE'))/NULLIF(COUNT(*),0),2) AS attendance_percent
 FROM attendance_records ar JOIN class_sessions cs ON cs.session_id=ar.session_id
 WHERE cs.subject_id=@subject_id GROUP BY ar.student_id
)
SELECT COUNT(*) AS enrolled_students,ROUND(AVG(s.score_percent),1) AS average_assessment_percent,
ROUND(AVG(atd.attendance_percent),1) AS classroom_attendance_percent,
SUM(CASE WHEN s.score_percent<40 OR atd.attendance_percent<60 THEN 1 ELSE 0 END) AS students_needing_attention
FROM roster r LEFT JOIN scores s ON s.student_id=r.user_id LEFT JOIN attendance atd ON atd.student_id=r.user_id;

-- 02. YEARS, CURRICULUM & TEACHING: stored study-year cohorts and counts.
SELECT c.course_id,c.course_name,p.program_level,c.duration_years,sy.study_year,sec.section_id,
sec.section_name,sec.academic_year,COUNT(DISTINCT e.student_id) AS enrolled_students
FROM sections sec JOIN courses c ON c.course_id=sec.course_id
LEFT JOIN course_programs p ON p.course_id=c.course_id LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id
LEFT JOIN student_enrollments e ON e.section_id=sec.section_id AND e.status='ACTIVE'
GROUP BY c.course_id,c.course_name,p.program_level,c.duration_years,sy.study_year,sec.section_id,sec.section_name,sec.academic_year
ORDER BY c.course_id,sy.study_year,sec.section_name;
SELECT s.subject_id,s.subject_name,c.course_name,cur.study_year,cur.semester,s.semester AS subject_semester,
(cur.semester=s.semester) AS semester_records_agree
FROM subjects s JOIN subject_curriculum cur ON cur.subject_id=s.subject_id JOIN courses c ON c.course_id=s.course_id
ORDER BY c.course_id,cur.study_year,cur.semester,s.subject_id;
SELECT f.faculty_assignment_id,u.full_name AS faculty,s.subject_name,c.course_name,cur.study_year,cur.semester,
sec.section_name,t.topic_id,t.topic_name,COALESCE(p.status,'PLANNED') AS coverage,p.updated_by,p.updated_at
FROM faculty_subject_assignments f JOIN users u ON u.user_id=f.faculty_id JOIN subjects s ON s.subject_id=f.subject_id
JOIN courses c ON c.course_id=s.course_id JOIN sections sec ON sec.section_id=f.section_id
LEFT JOIN subject_curriculum cur ON cur.subject_id=s.subject_id LEFT JOIN topics t ON t.subject_id=s.subject_id
LEFT JOIN teaching_topic_progress p ON p.faculty_assignment_id=f.faculty_assignment_id AND p.topic_id=t.topic_id
WHERE f.subject_id=@subject_id AND f.section_id=@section_id ORDER BY f.faculty_assignment_id,t.topic_id;

-- 03. AI QUESTION GENERATOR: successful requests persist history plus GENAI drafts.
-- Provider errors do not create pretend questions. An empty result means no successful saved generation.
SELECT h.generation_id,h.user_id,h.generation_type,h.model_name,h.created_at,h.output_data
FROM ai_generation_history h WHERE h.generation_type='QUESTION_PAPER' ORDER BY h.generation_id DESC LIMIT 30;
SELECT q.question_id,tp.topic_name,q.question_text,q.question_source,q.review_status,q.created_by,q.created_at
FROM questions q JOIN topics tp ON tp.topic_id=q.topic_id WHERE q.question_source='GENAI'
ORDER BY q.question_id DESC LIMIT 30;

-- 04. ANSWER EVALUATION: teacher-awarded marks, feedback and evaluator.
SELECT sa.answer_id,a.attempt_id,u.full_name AS student,t.title,q.question_text,sa.answer_text,
sa.awarded_marks,sa.feedback,ev.full_name AS evaluated_by,a.score AS attempt_total,a.status
FROM student_answers sa JOIN test_attempts a ON a.attempt_id=sa.attempt_id JOIN users u ON u.user_id=a.student_id
JOIN tests t ON t.test_id=a.test_id JOIN questions q ON q.question_id=sa.question_id
LEFT JOIN users ev ON ev.user_id=sa.evaluated_by
WHERE t.subject_id=@subject_id AND t.section_id=@section_id ORDER BY sa.answer_id DESC LIMIT 50;
SELECT generation_id,user_id,model_name,created_at,input_data,output_data
FROM ai_generation_history WHERE generation_type='ANSWER_FEEDBACK' ORDER BY generation_id DESC LIMIT 20;

-- 05. EXAM PERFORMANCE: one student's evaluated attempt trend and topic heatmap.
SELECT a.attempt_id,t.title,a.submitted_at,a.score,m.maximum,
ROUND(100*a.score/NULLIF(m.maximum,0),2) AS percentage
FROM test_attempts a JOIN tests t ON t.test_id=a.test_id
JOIN (SELECT test_id,SUM(marks) AS maximum FROM test_questions GROUP BY test_id) m ON m.test_id=t.test_id
WHERE a.student_id=@student_id AND t.subject_id=@subject_id AND t.section_id=@section_id AND a.status='EVALUATED'
ORDER BY a.submitted_at,a.attempt_id;
SELECT a.attempt_id,t.title,tp.topic_id,tp.topic_name,SUM(sa.awarded_marks) AS earned,SUM(tq.marks) AS possible,
ROUND(100*SUM(sa.awarded_marks)/NULLIF(SUM(tq.marks),0),1) AS topic_percent
FROM student_answers sa JOIN test_attempts a ON a.attempt_id=sa.attempt_id JOIN tests t ON t.test_id=a.test_id
JOIN questions q ON q.question_id=sa.question_id JOIN topics tp ON tp.topic_id=q.topic_id
JOIN test_questions tq ON tq.test_id=t.test_id AND tq.question_id=sa.question_id
WHERE a.student_id=@student_id AND t.subject_id=@subject_id AND t.section_id=@section_id
AND a.status='EVALUATED' AND sa.awarded_marks IS NOT NULL
GROUP BY a.attempt_id,t.title,tp.topic_id,tp.topic_name ORDER BY a.attempt_id,tp.topic_id;

-- 06. COLLEAGUE FEEDBACK: verify the signed-in administrator's own saved feedback.
SELECT f.feedback_id,f.author_id,recipient.full_name AS colleague,f.context_key,f.clarity,f.interaction,f.comments,f.updated_at
FROM staff_feedback f JOIN users recipient ON recipient.user_id=f.faculty_id
WHERE f.author_id=@actor_id ORDER BY f.updated_at DESC LIMIT 30;
-- Portfolio averages respect the three-response display threshold.
SELECT f.faculty_id,recipient.full_name,author.role AS source_role,COUNT(*) AS responses,
CASE WHEN COUNT(*)>=3 THEN ROUND(AVG(f.clarity),2) END AS displayed_clarity,
CASE WHEN COUNT(*)>=3 THEN ROUND(AVG(f.interaction),2) END AS displayed_interaction
FROM staff_feedback f JOIN users recipient ON recipient.user_id=f.faculty_id JOIN users author ON author.user_id=f.author_id
GROUP BY f.faculty_id,recipient.full_name,author.role ORDER BY f.faculty_id,author.role;

-- 07. STAFF DEVELOPMENT: creation, edit/resubmission, review and archive all remain visible here.
SELECT e.evidence_id,u.full_name AS owner,u.role,e.category,e.title,e.details,e.skill_level,e.reference_url,
e.status,e.review_note,reviewer.full_name AS reviewed_by,e.created_at,e.updated_at
FROM staff_evidence e JOIN users u ON u.user_id=e.owner_id LEFT JOIN users reviewer ON reviewer.user_id=e.reviewed_by
ORDER BY e.evidence_id DESC LIMIT 60;
SELECT owner_id,SUM(category='RESEARCH' AND status='VERIFIED') AS verified_research_records,
SUM(category='RESEARCH' AND status='SUBMITTED') AS research_awaiting_review
FROM staff_evidence GROUP BY owner_id ORDER BY owner_id;

-- 08. ACADEMIC DATA CENTRE: first three cards describe the seeded collection.
SELECT
(SELECT COUNT(*) FROM users WHERE role='STUDENT' AND email LIKE '%@demo.learnpath.dev') AS prefilled_students,
(SELECT COUNT(*) FROM users WHERE role='FACULTY' AND email LIKE '%@demo.learnpath.dev') AS prefilled_faculty,
(SELECT COUNT(*) FROM users WHERE role='HOD' AND email LIKE '%@demo.learnpath.dev') AS prefilled_hods,
(SELECT COUNT(*) FROM courses) AS courses,(SELECT COUNT(*) FROM tests) AS stored_exams,
(SELECT COUNT(*) FROM student_answers) AS stored_answer_rows;
-- The UI's evaluated-answers card currently counts stored answer rows, including any ungraded row.
SELECT COUNT(*) AS answers_with_awarded_marks FROM student_answers WHERE awarded_marks IS NOT NULL;
SELECT c.course_id,c.course_name,d.department_name,p.program_level,c.duration_years,
(SELECT COUNT(DISTINCT e.student_id) FROM student_enrollments e JOIN sections sec ON sec.section_id=e.section_id WHERE sec.course_id=c.course_id AND e.status='ACTIVE') AS students,
(SELECT COUNT(DISTINCT f.faculty_id) FROM faculty_subject_assignments f JOIN sections sec ON sec.section_id=f.section_id WHERE sec.course_id=c.course_id) AS faculty,
(SELECT COUNT(*) FROM subjects s WHERE s.course_id=c.course_id) AS subjects
FROM courses c JOIN departments d ON d.department_id=c.department_id LEFT JOIN course_programs p ON p.course_id=c.course_id ORDER BY c.course_id;

-- 09. QUESTION BANK: manual and generated questions plus review state.
SELECT q.question_id,tp.topic_name,s.subject_name,q.question_text,q.question_type,q.difficulty,
q.question_source,q.review_status,q.is_active,q.created_by,q.created_at
FROM questions q JOIN topics tp ON tp.topic_id=q.topic_id JOIN subjects s ON s.subject_id=tp.subject_id
WHERE s.subject_id=@subject_id ORDER BY q.question_id DESC LIMIT 50;

-- 10. ASSIGNMENTS: counts use the same active roster as the faculty assignment coverage endpoint.
SELECT a.assignment_id,a.title,a.due_at,a.max_marks,COUNT(DISTINCT roster.user_id) AS eligible,
COUNT(DISTINCT sub.student_id) AS submitted,
COUNT(DISTINCT roster.user_id)-COUNT(DISTINCT sub.student_id) AS not_submitted,
COUNT(DISTINCT CASE WHEN sub.status='GRADED' THEN sub.student_id END) AS graded,
COUNT(DISTINCT CASE WHEN sub.status='SUBMITTED' THEN sub.student_id END) AS awaiting_grading,
COUNT(DISTINCT CASE WHEN sub.status='RETURNED' THEN sub.student_id END) AS returned
FROM assignments a LEFT JOIN student_enrollments e ON e.section_id=a.section_id AND e.status='ACTIVE'
LEFT JOIN users roster ON roster.user_id=e.student_id AND roster.role='STUDENT' AND roster.is_active=1
LEFT JOIN submissions sub ON sub.assignment_id=a.assignment_id AND sub.student_id=roster.user_id
WHERE a.subject_id=@subject_id AND a.section_id=@section_id
GROUP BY a.assignment_id,a.title,a.due_at,a.max_marks ORDER BY a.assignment_id DESC;
SELECT sub.submission_id,sub.assignment_id,a.title,u.user_id,u.full_name,sub.answer_text,sub.file_url,
sub.status,sub.marks_awarded,a.max_marks,sub.feedback,sub.submitted_at
FROM submissions sub JOIN assignments a ON a.assignment_id=sub.assignment_id JOIN users u ON u.user_id=sub.student_id
WHERE sub.assignment_id=@assignment_id ORDER BY sub.submission_id DESC;

-- 11. STUDENT DIRECTORY: email, degree, year, section, enrollment and account status.
SELECT u.user_id,u.full_name,u.email,u.registration_number,u.is_active,c.course_name,p.program_level,
sy.study_year,sec.section_id,sec.section_name,sec.academic_year,e.status AS enrollment_status
FROM users u LEFT JOIN student_enrollments e ON e.student_id=u.user_id
LEFT JOIN sections sec ON sec.section_id=e.section_id LEFT JOIN courses c ON c.course_id=sec.course_id
LEFT JOIN course_programs p ON p.course_id=c.course_id LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id
WHERE u.role='STUDENT' ORDER BY u.user_id,sec.section_id;

-- 12. FACULTY & HOD DIRECTORY: profile records and actual teaching mappings.
SELECT u.user_id,u.full_name,u.email,u.role,u.registration_number,u.is_active,d.department_name,
COUNT(DISTINCT f.faculty_assignment_id) AS teaching_mappings
FROM users u LEFT JOIN departments d ON d.department_id=u.department_id
LEFT JOIN faculty_subject_assignments f ON f.faculty_id=u.user_id
WHERE u.role IN ('FACULTY','HOD') GROUP BY u.user_id,u.full_name,u.email,u.role,u.registration_number,u.is_active,d.department_name ORDER BY u.role,u.user_id;

-- 13. INSTITUTION OPERATIONS: profile/status changes, enrollments, teaching and audit.
SELECT user_id,full_name,email,role,department_id,registration_number,is_active FROM users ORDER BY user_id DESC LIMIT 50;
SELECT e.enrollment_id,u.full_name,c.course_name,sy.study_year,sec.section_name,e.status,e.enrolled_on
FROM student_enrollments e JOIN users u ON u.user_id=e.student_id JOIN sections sec ON sec.section_id=e.section_id
JOIN courses c ON c.course_id=sec.course_id LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id ORDER BY e.enrollment_id DESC LIMIT 50;
SELECT f.faculty_assignment_id,u.full_name AS faculty,c.course_name,s.subject_name,cur.study_year,cur.semester,
sec.section_name,f.assigned_at FROM faculty_subject_assignments f JOIN users u ON u.user_id=f.faculty_id
JOIN subjects s ON s.subject_id=f.subject_id JOIN courses c ON c.course_id=s.course_id JOIN sections sec ON sec.section_id=f.section_id
LEFT JOIN subject_curriculum cur ON cur.subject_id=s.subject_id ORDER BY f.faculty_assignment_id DESC LIMIT 50;
SELECT a.audit_id,a.created_at,u.full_name AS actor,a.action,a.entity_type,a.entity_id,a.reason,a.before_data,a.after_data
FROM campus_audit a JOIN users u ON u.user_id=a.actor_id ORDER BY a.audit_id DESC LIMIT 100;

-- 14. EXAM STUDIO: draft/published/closed papers, schedules and question marks.
SELECT t.test_id,t.title,s.subject_name,sec.section_name,t.created_by,t.status,t.duration_minutes,t.max_attempts,
t.start_at,t.end_at,t.created_at,es.exam_type,es.occurrence_number,es.request_key
FROM tests t JOIN subjects s ON s.subject_id=t.subject_id JOIN sections sec ON sec.section_id=t.section_id
LEFT JOIN exam_schedules es ON es.test_id=t.test_id
WHERE t.subject_id=@subject_id AND t.section_id=@section_id ORDER BY t.test_id DESC;
SELECT tq.test_id,t.title,tq.question_order,tq.question_id,q.question_text,tq.marks
FROM test_questions tq JOIN tests t ON t.test_id=tq.test_id JOIN questions q ON q.question_id=tq.question_id
WHERE tq.test_id=@test_id ORDER BY tq.question_order;
SELECT d.attempt_id,a.student_id,d.question_id,d.answer_text,d.updated_at
FROM exam_answer_drafts d JOIN test_attempts a ON a.attempt_id=d.attempt_id
WHERE a.test_id=@test_id ORDER BY d.attempt_id,d.question_id;

-- 15. ATTENDANCE REGISTER: save, correction version and individual marks.
SELECT cs.session_id,s.subject_name,sec.section_name,cs.session_date,cs.starts_at,u.full_name AS marked_by,
r.version,r.updated_by,r.updated_at,COUNT(ar.attendance_id) AS marked_students,
SUM(ar.status='PRESENT') AS present,SUM(ar.status='ABSENT') AS absent,SUM(ar.status='LATE') AS late,SUM(ar.status='LEAVE') AS on_leave
FROM class_sessions cs JOIN subjects s ON s.subject_id=cs.subject_id JOIN sections sec ON sec.section_id=cs.section_id
LEFT JOIN users u ON u.user_id=cs.marked_by LEFT JOIN attendance_registers r ON r.session_id=cs.session_id
LEFT JOIN attendance_records ar ON ar.session_id=cs.session_id
WHERE cs.subject_id=@subject_id AND cs.section_id=@section_id
GROUP BY cs.session_id,s.subject_name,sec.section_name,cs.session_date,cs.starts_at,u.full_name,r.version,r.updated_by,r.updated_at ORDER BY cs.session_id DESC;
SELECT ar.attendance_id,ar.session_id,u.user_id,u.full_name,ar.status,ar.remarks,ar.recorded_at
FROM attendance_records ar JOIN users u ON u.user_id=ar.student_id WHERE ar.session_id=@session_id ORDER BY u.full_name;

-- 16. LEARNER REGISTER: class-specific saved records for the selected student.
SELECT cs.session_id,cs.session_date,cs.starts_at,ar.status FROM attendance_records ar JOIN class_sessions cs ON cs.session_id=ar.session_id
WHERE ar.student_id=@student_id AND cs.subject_id=@subject_id AND cs.section_id=@section_id ORDER BY cs.session_date,cs.starts_at;
SELECT a.assignment_id,a.title,a.due_at,sub.submission_id,COALESCE(sub.status,'NOT_SUBMITTED') AS submission_state,sub.marks_awarded,sub.feedback
FROM assignments a LEFT JOIN submissions sub ON sub.assignment_id=a.assignment_id AND sub.student_id=@student_id
WHERE a.subject_id=@subject_id AND a.section_id=@section_id ORDER BY a.assignment_id DESC;
SELECT a.attempt_id,t.test_id,t.title,a.status,a.score,a.started_at,a.submitted_at
FROM test_attempts a JOIN tests t ON t.test_id=a.test_id
WHERE a.student_id=@student_id AND t.subject_id=@subject_id AND t.section_id=@section_id ORDER BY a.attempt_id DESC;

-- 17. WEEKLY TIMETABLE: inactive rows prove the archive operation instead of physical deletion.
SELECT tt.slot_id,u.full_name AS faculty,c.course_name,p.program_level,sy.study_year,s.subject_name,
sec.section_name,tt.weekday,TIME_FORMAT(tt.starts_at,'%H:%i') AS starts_at,TIME_FORMAT(tt.ends_at,'%H:%i') AS ends_at,
tt.room,tt.session_type,tt.is_active,tt.created_by,tt.created_at
FROM faculty_timetable tt JOIN users u ON u.user_id=tt.faculty_id JOIN subjects s ON s.subject_id=tt.subject_id
JOIN courses c ON c.course_id=s.course_id JOIN sections sec ON sec.section_id=tt.section_id
LEFT JOIN course_programs p ON p.course_id=c.course_id LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id
ORDER BY tt.slot_id DESC;

-- 18. FACULTY LEAVE APPROVALS: requester, decision, reviewer and dates.
SELECT l.leave_id,u.full_name AS requester,u.role,d.department_name,l.start_date,l.end_date,l.leave_type,l.reason,
l.status,reviewer.full_name AS reviewed_by,l.review_note,l.reviewed_at,l.created_at
FROM faculty_leave_requests l JOIN users u ON u.user_id=l.requester_id LEFT JOIN departments d ON d.department_id=u.department_id
LEFT JOIN users reviewer ON reviewer.user_id=l.reviewed_by ORDER BY l.leave_id DESC;

-- 19. UG / PG PROGRAMS: program classification and curriculum totals.
SELECT c.course_id,c.course_name,c.duration_years,p.program_level,p.updated_at,COUNT(cur.subject_id) AS classified_subjects
FROM courses c LEFT JOIN course_programs p ON p.course_id=c.course_id
LEFT JOIN subjects s ON s.course_id=c.course_id LEFT JOIN subject_curriculum cur ON cur.subject_id=s.subject_id
GROUP BY c.course_id,c.course_name,c.duration_years,p.program_level,p.updated_at ORDER BY c.course_id;

-- 20. AI KNOWLEDGE ASSISTANT: own conversation/message history, retrieval evidence and answer mode.
SELECT conv.conversation_id,conv.user_id,conv.title,m.message_id,m.question,m.answer,m.answer_mode,m.model_name,m.citations,m.created_at
FROM rag_conversations conv LEFT JOIN rag_messages m ON m.conversation_id=conv.conversation_id
WHERE conv.user_id=@actor_id ORDER BY conv.conversation_id DESC,m.message_id DESC LIMIT 50;
SELECT chunk_id,source_key,title,source_kind,cohort,content_sha256,created_at FROM rag_chunks ORDER BY chunk_id DESC LIMIT 30;

-- 21. ENGINEERING DATASET: linked names and academic identifiers (not a second copy of the grades).
SELECT u.user_id AS student_id,u.full_name AS student,u.email,c.course_name,p.program_level,sy.study_year,
sec.section_id,sec.section_name,s.subject_id,s.subject_name,s.semester,
(SELECT GROUP_CONCAT(DISTINCT teacher.full_name ORDER BY teacher.full_name SEPARATOR ', ') FROM faculty_subject_assignments f JOIN users teacher ON teacher.user_id=f.faculty_id WHERE f.subject_id=s.subject_id AND f.section_id=sec.section_id) AS faculty,
(SELECT GROUP_CONCAT(DISTINCT h.full_name ORDER BY h.full_name SEPARATOR ', ') FROM users h WHERE h.department_id=c.department_id AND h.role='HOD' AND h.is_active=1) AS hod_accounts
FROM users u JOIN student_enrollments e ON e.student_id=u.user_id AND e.status='ACTIVE'
JOIN sections sec ON sec.section_id=e.section_id JOIN courses c ON c.course_id=sec.course_id
JOIN subjects s ON s.course_id=c.course_id LEFT JOIN course_programs p ON p.course_id=c.course_id
LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id LEFT JOIN subject_curriculum cur ON cur.subject_id=s.subject_id
WHERE u.role='STUDENT' AND (cur.subject_id IS NULL OR cur.study_year=sy.study_year)
ORDER BY u.user_id,c.course_id,s.subject_id LIMIT 100;

-- 22. DASHBOARD PERFORMANCE OVERVIEW: selected learner's weighted subject marks.
SELECT s.subject_id,s.subject_name,SUM(COALESCE(sa.awarded_marks,0)) AS earned,SUM(tq.marks) AS possible,
ROUND(100*SUM(COALESCE(sa.awarded_marks,0))/NULLIF(SUM(tq.marks),0),2) AS percentage
FROM test_attempts a JOIN tests t ON t.test_id=a.test_id JOIN subjects s ON s.subject_id=t.subject_id
JOIN test_questions tq ON tq.test_id=t.test_id LEFT JOIN student_answers sa ON sa.attempt_id=a.attempt_id AND sa.question_id=tq.question_id
WHERE a.student_id=@student_id AND a.status='EVALUATED' GROUP BY s.subject_id,s.subject_name ORDER BY s.subject_id;
SELECT p.plan_id,p.title,p.student_id,p.subject_id,p.status,i.plan_item_id,i.topic_id,i.scheduled_date,i.recommendation,i.status AS milestone_status
FROM study_plans p LEFT JOIN study_plan_items i ON i.plan_id=p.plan_id WHERE p.student_id=@student_id ORDER BY p.plan_id DESC,i.scheduled_date;

-- 23. USER MANAGEMENT: account creation, role/status and password-reset verification.
-- Fingerprint changes on password reset. The original password is never stored in this table.
SELECT user_id,full_name,email,role,department_id,registration_number,is_active,created_at,
(password_hash LIKE '$argon2id$%') AS uses_argon2id,SHA2(password_hash,256) AS password_hash_fingerprint
FROM users ORDER BY user_id DESC LIMIT 60;

-- 24. DEPARTMENTS: verify saved names/codes by department_id.
SELECT department_id,department_name,department_code,created_at FROM departments ORDER BY department_id DESC;

-- 25. COURSES: verify saved degree name/code/duration and linked program level.
SELECT c.course_id,c.course_name,c.course_code,c.duration_years,c.department_id,d.department_name,p.program_level,c.created_at
FROM courses c JOIN departments d ON d.department_id=c.department_id LEFT JOIN course_programs p ON p.course_id=c.course_id ORDER BY c.course_id DESC;

-- 26. SUBJECTS: semester edits must agree with the curriculum row when classified.
SELECT s.subject_id,s.course_id,s.subject_name,s.subject_code,s.semester,cur.study_year,cur.semester AS curriculum_semester,
CASE WHEN cur.subject_id IS NULL THEN 'Year unclassified' WHEN cur.semester=s.semester THEN 'Consistent' ELSE 'Mismatch' END AS curriculum_check
FROM subjects s LEFT JOIN subject_curriculum cur ON cur.subject_id=s.subject_id ORDER BY s.subject_id DESC LIMIT 80;

-- 27. TOPICS: topic changes and question linkage.
SELECT tp.topic_id,tp.topic_name,tp.description,s.subject_id,s.subject_name,COUNT(q.question_id) AS linked_questions,tp.created_at
FROM topics tp JOIN subjects s ON s.subject_id=tp.subject_id LEFT JOIN questions q ON q.topic_id=tp.topic_id
WHERE s.subject_id=@subject_id GROUP BY tp.topic_id,tp.topic_name,tp.description,s.subject_id,s.subject_name,tp.created_at ORDER BY tp.topic_id DESC;

-- 28. SECTIONS: section names, calendar year and separately saved year of study.
SELECT sec.section_id,c.course_name,sec.section_name,sec.academic_year,sy.study_year,
COUNT(DISTINCT CASE WHEN e.status='ACTIVE' THEN e.student_id END) AS active_enrollments
FROM sections sec JOIN courses c ON c.course_id=sec.course_id LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id
LEFT JOIN student_enrollments e ON e.section_id=sec.section_id
GROUP BY sec.section_id,c.course_name,sec.section_name,sec.academic_year,sy.study_year ORDER BY sec.section_id DESC;

-- 29. ACADEMIC CALENDAR: new calendar events persist here.
SELECT event_id,title,starts_on,ends_on,description FROM academic_events ORDER BY event_id DESC;

-- 30. SYSTEM SETTINGS: this screen is read-only connection/provider status, not an editable settings table.
-- SQL verifies this Workbench connection only. Use /health to verify the FastAPI connection.
-- Provider keys and JWT signing keys remain in backend/.env and must not be queried/exported.
SELECT DATABASE() AS database_name,@@port AS mysql_port,VERSION() AS mysql_version,CURRENT_USER() AS mysql_connection_account;

-- 31. PROFILE: the profile screen reads users. Changes through Institution Operations affect this same row.
SELECT u.user_id,u.full_name,u.email,u.role,u.registration_number,u.is_active,d.department_name,u.created_at
FROM users u LEFT JOIN departments d ON d.department_id=u.department_id WHERE u.user_id=@actor_id;

-- EXTRA. Latest catalog audit evidence: actor, exact before/after fields, timestamp.
SELECT audit_id,created_at,actor_id,action,entity_type,entity_id,before_data,after_data
FROM campus_audit WHERE action IN ('CATALOG_CREATED','CATALOG_UPDATED') ORDER BY audit_id DESC LIMIT 30;
