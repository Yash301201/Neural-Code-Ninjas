-- LearnPath AI: project-specific MySQL reporting queries.
-- Run after 001_schema.sql and 003_calendar.sql; optional demo rows: 002_sample_data.sql.
-- Change these IDs to select your project records. This file only reads academic data.
-- These are administrator/Workbench reports; API role checks still apply in the backend.
USE learnpath_ai;
SET time_zone = '+00:00';
SET @department_id = 1;
SET @student_id = 4;
SET @faculty_id = 3;
SET @subject_id = 1;
SET @section_id = 1;
SET @test_id = 1;

-- 1. Department courses and subjects.
SELECT d.department_name, c.course_code, c.course_name,
       s.subject_id, s.subject_code, s.subject_name, s.semester
FROM departments d
JOIN courses c ON c.department_id = d.department_id
LEFT JOIN subjects s ON s.course_id = c.course_id
WHERE d.department_id = @department_id
ORDER BY c.course_name, s.semester, s.subject_name;

-- 2. Active students enrolled in a section (no password hashes).
SELECT u.user_id, u.registration_number, u.full_name, u.email,
       sec.section_name, sec.academic_year, c.course_name
FROM student_enrollments e
JOIN users u ON u.user_id = e.student_id
JOIN sections sec ON sec.section_id = e.section_id
JOIN courses c ON c.course_id = sec.course_id
WHERE e.section_id = @section_id AND e.status = 'ACTIVE'
  AND u.role = 'STUDENT' AND u.is_active = TRUE
ORDER BY u.full_name;

-- 3. Faculty teaching allocations.
SELECT f.faculty_assignment_id, u.full_name, s.subject_name,
       sec.section_name, sec.academic_year
FROM faculty_subject_assignments f
JOIN users u ON u.user_id = f.faculty_id
JOIN subjects s ON s.subject_id = f.subject_id
JOIN sections sec ON sec.section_id = f.section_id
WHERE f.faculty_id = @faculty_id
ORDER BY sec.academic_year, sec.section_name, s.subject_name;

-- 4. Subject syllabus/topics.
SELECT t.topic_id, s.subject_name, t.topic_name, t.description
FROM topics t JOIN subjects s ON s.subject_id = t.subject_id
WHERE t.subject_id = @subject_id ORDER BY t.topic_id;

-- 5. Approved question-bank coverage by topic and difficulty.
SELECT t.topic_id, t.topic_name, q.difficulty, COUNT(q.question_id) AS approved_questions
FROM topics t
LEFT JOIN questions q ON q.topic_id = t.topic_id
 AND q.review_status = 'APPROVED' AND q.is_active = TRUE
WHERE t.subject_id = @subject_id
GROUP BY t.topic_id, t.topic_name, q.difficulty
ORDER BY t.topic_name, q.difficulty;

-- 6. Generated questions awaiting faculty review (staff report).
SELECT q.question_id, t.topic_name, q.question_text, q.question_type,
       q.difficulty, q.created_at
FROM questions q JOIN topics t ON t.topic_id = q.topic_id
WHERE t.subject_id = @subject_id AND q.question_source = 'GENAI'
  AND q.review_status = 'PENDING_REVIEW'
ORDER BY q.created_at, q.question_id;

-- 7. Tests currently open to an enrolled student.
SELECT te.test_id, te.title, te.duration_minutes, te.start_at, te.end_at,
       te.max_attempts, s.subject_name
FROM tests te JOIN subjects s ON s.subject_id = te.subject_id
WHERE te.status = 'PUBLISHED'
  AND (te.start_at IS NULL OR te.start_at <= CURRENT_TIMESTAMP)
  AND (te.end_at IS NULL OR te.end_at >= CURRENT_TIMESTAMP)
  AND EXISTS (SELECT 1 FROM student_enrollments e
              WHERE e.student_id = @student_id AND e.section_id = te.section_id
                AND e.status = 'ACTIVE')
ORDER BY te.start_at, te.test_id;

-- 8. Test paper preview without exposing answer keys.
-- Deliver to a student only after the backend verifies an authorized active attempt.
SELECT tq.question_order, q.question_id, q.question_text,
       q.question_type, q.choice_options, tq.marks
FROM test_questions tq JOIN questions q ON q.question_id = tq.question_id
WHERE tq.test_id = @test_id ORDER BY tq.question_order;

-- 9. Student assessment history, with percentages from evaluated attempts only.
SELECT a.attempt_id, te.title, a.attempt_number, a.started_at,
       a.submitted_at, a.status, a.score, totals.max_marks,
       CASE WHEN a.status = 'EVALUATED'
         THEN ROUND(100 * a.score / NULLIF(totals.max_marks, 0), 2)
         ELSE NULL END AS score_percent
FROM test_attempts a JOIN tests te ON te.test_id = a.test_id
JOIN (SELECT test_id, SUM(marks) AS max_marks FROM test_questions GROUP BY test_id) totals
 ON totals.test_id = te.test_id
WHERE a.student_id = @student_id AND te.subject_id = @subject_id
ORDER BY a.started_at DESC, a.attempt_id DESC;

-- 10. Student topic performance; absent observations remain NULL, not zero.
SELECT t.topic_id, t.topic_name, p.evaluated_attempts,
       p.marks_earned, p.marks_possible, p.performance_percent
FROM topics t LEFT JOIN student_topic_performance p
 ON p.topic_id = t.topic_id AND p.student_id = @student_id
WHERE t.subject_id = @subject_id
ORDER BY p.performance_percent IS NOT NULL, p.performance_percent, t.topic_name;

-- 11. Student attendance per subject. PRESENT and LATE count as attendance.
SELECT s.subject_name, a.recorded_sessions, a.attended_sessions,
       a.absent_sessions, a.attendance_percent
FROM student_attendance_summary a JOIN subjects s ON s.subject_id = a.subject_id
WHERE a.student_id = @student_id ORDER BY s.subject_name;

-- 12. Department students needing faculty attention.
SELECT u.user_id, u.full_name, u.registration_number, s.subject_name,
       d.average_topic_score, d.attendance_percent, d.risk_score,
       d.risk_level, d.risk_explanation
FROM student_subject_dashboard d
JOIN users u ON u.user_id = d.student_id
JOIN subjects s ON s.subject_id = d.subject_id
JOIN courses c ON c.course_id = d.course_id
WHERE c.department_id = @department_id AND d.needs_attention = TRUE
ORDER BY d.risk_score DESC, u.full_name, s.subject_name;

-- 13. Latest risk indicator for this student and subject.
SELECT prediction_id, risk_score, risk_level, model_version,
       input_features, explanation, predicted_at
FROM risk_predictions
WHERE student_id = @student_id AND subject_id = @subject_id
ORDER BY predicted_at DESC, prediction_id DESC LIMIT 1;

-- 14. Weak topics across a department, equally weighting assessed students.
SELECT s.subject_name, t.topic_name, COUNT(*) AS assessed_students,
       ROUND(AVG(p.performance_percent), 2) AS mean_student_percent
FROM student_topic_performance p
JOIN topics t ON t.topic_id = p.topic_id
JOIN subjects s ON s.subject_id = p.subject_id
JOIN courses c ON c.course_id = s.course_id
WHERE c.department_id = @department_id
GROUP BY s.subject_id, s.subject_name, t.topic_id, t.topic_name
HAVING AVG(p.performance_percent) < 50
ORDER BY mean_student_percent, s.subject_name, t.topic_name;

-- 15. Available assignments the student has not submitted.
SELECT a.assignment_id, a.title, s.subject_name, a.due_at, a.max_marks
FROM assignments a JOIN subjects s ON s.subject_id = a.subject_id
WHERE a.due_at >= CURRENT_TIMESTAMP
  AND EXISTS (SELECT 1 FROM student_enrollments e
              WHERE e.student_id = @student_id AND e.section_id = a.section_id
                AND e.status = 'ACTIVE')
  AND NOT EXISTS (SELECT 1 FROM submissions sub
                  WHERE sub.assignment_id = a.assignment_id AND sub.student_id = @student_id)
ORDER BY a.due_at, a.assignment_id;

-- 16. Student assignment grades and feedback.
SELECT a.title, sub.submitted_at, sub.status, sub.marks_awarded,
       a.max_marks, sub.feedback
FROM submissions sub JOIN assignments a ON a.assignment_id = sub.assignment_id
WHERE sub.student_id = @student_id ORDER BY sub.submitted_at DESC;

-- 17. Faculty descriptive-answer grading queue.
SELECT sa.answer_id, ta.attempt_id, u.full_name, te.title,
       q.question_text, sa.answer_text, tq.marks AS maximum_marks
FROM student_answers sa
JOIN test_attempts ta ON ta.attempt_id = sa.attempt_id
JOIN tests te ON te.test_id = ta.test_id
JOIN questions q ON q.question_id = sa.question_id
JOIN test_questions tq ON tq.test_id = te.test_id AND tq.question_id = q.question_id
JOIN users u ON u.user_id = ta.student_id
WHERE ta.status = 'SUBMITTED' AND sa.awarded_marks IS NULL
  AND q.question_type IN ('SHORT_ANSWER', 'DESCRIPTIVE')
  AND EXISTS (SELECT 1 FROM faculty_subject_assignments f
              WHERE f.faculty_id = @faculty_id AND f.subject_id = te.subject_id
                AND f.section_id = te.section_id)
ORDER BY ta.submitted_at, sa.answer_id;

-- 18. Personalized study-plan tasks and completion state.
SELECT p.plan_id, p.title, p.start_date, p.end_date, p.status AS plan_status,
       i.plan_item_id, t.topic_name, i.scheduled_date, i.recommendation,
       i.estimated_minutes, i.status AS task_status
FROM study_plans p JOIN study_plan_items i ON i.plan_id = p.plan_id
JOIN topics t ON t.topic_id = i.topic_id
WHERE p.student_id = @student_id AND p.subject_id = @subject_id
ORDER BY p.plan_id DESC, i.scheduled_date, i.plan_item_id;

-- 19. Section/subject dashboard summary (one row per student/subject in the view).
SELECT COUNT(*) AS enrolled_students,
       COUNT(d.average_topic_score) AS assessed_students,
       ROUND(AVG(d.average_topic_score), 2) AS average_topic_score,
       ROUND(AVG(d.attendance_percent), 2) AS average_attendance,
       COALESCE(SUM(d.needs_attention), 0) AS students_needing_attention
FROM student_subject_dashboard d
WHERE d.subject_id = @subject_id
  AND EXISTS (SELECT 1 FROM student_enrollments e
              WHERE e.student_id = d.student_id AND e.section_id = @section_id
                AND e.status = 'ACTIVE');

-- 20. Upcoming/current academic calendar events.
SELECT event_id, title, starts_on, ends_on, description
FROM academic_events WHERE ends_on >= CURRENT_DATE
ORDER BY starts_on, event_id;

-- 21. Faculty GenAI workflow usage (metadata only).
SELECT generation_type, model_name, COUNT(*) AS generation_count,
       MAX(created_at) AS most_recent_generation
FROM ai_generation_history WHERE user_id = @faculty_id
GROUP BY generation_type, model_name ORDER BY generation_type, model_name;
