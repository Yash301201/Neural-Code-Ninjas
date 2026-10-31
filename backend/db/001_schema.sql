-- LearnPath AI - MySQL database schema and query pack
-- Based on the project brief and the team's draft schema.
-- Target: MySQL 8.0.16+ with InnoDB (for enforced CHECK constraints, JSON, CTEs and window functions).
-- Run in MySQL Workbench or the mysql client. This creates/uses the learnpath_ai database.
-- After creating the schema, run learnpath_ai_sample_data.sql for synthetic demo rows.
-- MySQL DDL implicitly commits; run this in a new project database, not over a production database.
-- Passwords must be hashed by the application (Argon2id or bcrypt); never store plaintext.
-- The application must enforce role-based access and must never expose correct_answer to students.
-- Use bound parameters for application queries. Use public or synthetic data only.

CREATE DATABASE IF NOT EXISTS learnpath_ai
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_0900_ai_ci;
USE learnpath_ai;

-- 1. ORGANIZATION AND COURSE STRUCTURE

CREATE TABLE IF NOT EXISTS departments (
    department_id BIGINT NOT NULL AUTO_INCREMENT,
    department_name VARCHAR(120) NOT NULL,
    department_code VARCHAR(20) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (department_id),
    UNIQUE KEY uq_departments_name (department_name),
    UNIQUE KEY uq_departments_code (department_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS courses (
    course_id BIGINT NOT NULL AUTO_INCREMENT,
    department_id BIGINT NOT NULL,
    course_name VARCHAR(120) NOT NULL,
    course_code VARCHAR(30) NULL,
    duration_years SMALLINT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (course_id),
    UNIQUE KEY uq_courses_code (course_code),
    UNIQUE KEY uq_courses_department_name (department_id, course_name),
    KEY idx_courses_department (department_id),
    CONSTRAINT fk_courses_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id),
    CONSTRAINT chk_courses_duration CHECK (duration_years IS NULL OR duration_years > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS sections (
    section_id BIGINT NOT NULL AUTO_INCREMENT,
    course_id BIGINT NOT NULL,
    academic_year VARCHAR(9) NOT NULL,
    section_name VARCHAR(30) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (section_id),
    UNIQUE KEY uq_sections_course_year_name (course_id, academic_year, section_name),
    KEY idx_sections_course_year (course_id, academic_year),
    CONSTRAINT fk_sections_course FOREIGN KEY (course_id)
        REFERENCES courses(course_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT NOT NULL AUTO_INCREMENT,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(254) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    department_id BIGINT NULL,
    registration_number VARCHAR(50) NULL,
    phone VARCHAR(25) NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_users_email (email),
    UNIQUE KEY uq_users_registration (registration_number),
    KEY idx_users_department_role (department_id, role),
    CONSTRAINT fk_users_department FOREIGN KEY (department_id)
        REFERENCES departments(department_id),
    CONSTRAINT chk_users_role CHECK (role IN ('ADMIN', 'HOD', 'FACULTY', 'STUDENT'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS subjects (
    subject_id BIGINT NOT NULL AUTO_INCREMENT,
    course_id BIGINT NOT NULL,
    subject_name VARCHAR(120) NOT NULL,
    subject_code VARCHAR(30) NULL,
    semester SMALLINT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (subject_id),
    UNIQUE KEY uq_subjects_course_name (course_id, subject_name),
    UNIQUE KEY uq_subjects_course_code (course_id, subject_code),
    KEY idx_subjects_course_semester (course_id, semester),
    CONSTRAINT fk_subjects_course FOREIGN KEY (course_id)
        REFERENCES courses(course_id),
    CONSTRAINT chk_subjects_semester CHECK (semester IS NULL OR semester BETWEEN 1 AND 16)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS topics (
    topic_id BIGINT NOT NULL AUTO_INCREMENT,
    subject_id BIGINT NOT NULL,
    topic_name VARCHAR(160) NOT NULL,
    description TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (topic_id),
    UNIQUE KEY uq_topics_subject_name (subject_id, topic_name),
    KEY idx_topics_subject (subject_id),
    CONSTRAINT fk_topics_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS student_enrollments (
    enrollment_id BIGINT NOT NULL AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    section_id BIGINT NOT NULL,
    enrolled_on DATE NOT NULL DEFAULT (CURRENT_DATE),
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    PRIMARY KEY (enrollment_id),
    UNIQUE KEY uq_enrollment_student_section (student_id, section_id),
    KEY idx_enrollments_section_status (section_id, status),
    KEY idx_enrollments_student_status (student_id, status),
    CONSTRAINT fk_enrollments_student FOREIGN KEY (student_id)
        REFERENCES users(user_id),
    CONSTRAINT fk_enrollments_section FOREIGN KEY (section_id)
        REFERENCES sections(section_id),
    CONSTRAINT chk_enrollments_status CHECK (status IN ('ACTIVE', 'COMPLETED', 'WITHDRAWN'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS faculty_subject_assignments (
    faculty_assignment_id BIGINT NOT NULL AUTO_INCREMENT,
    faculty_id BIGINT NOT NULL,
    subject_id BIGINT NOT NULL,
    section_id BIGINT NOT NULL,
    assigned_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (faculty_assignment_id),
    UNIQUE KEY uq_faculty_subject_section (faculty_id, subject_id, section_id),
    KEY idx_faculty_assignments_faculty (faculty_id, section_id),
    CONSTRAINT fk_faculty_assignments_faculty FOREIGN KEY (faculty_id)
        REFERENCES users(user_id),
    CONSTRAINT fk_faculty_assignments_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),
    CONSTRAINT fk_faculty_assignments_section FOREIGN KEY (section_id)
        REFERENCES sections(section_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 2. QUESTION BANK AND TESTS

CREATE TABLE IF NOT EXISTS questions (
    question_id BIGINT NOT NULL AUTO_INCREMENT,
    topic_id BIGINT NOT NULL,
    created_by BIGINT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(20) NOT NULL,
    difficulty VARCHAR(10) NOT NULL,
    choice_options JSON NOT NULL,
    correct_answer TEXT NULL,
    explanation TEXT NULL,
    question_source VARCHAR(20) NOT NULL DEFAULT 'FACULTY',
    review_status VARCHAR(20) NOT NULL DEFAULT 'APPROVED',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (question_id),
    KEY idx_questions_topic_review (topic_id, review_status, is_active),
    KEY idx_questions_created_by (created_by),
    CONSTRAINT fk_questions_topic FOREIGN KEY (topic_id)
        REFERENCES topics(topic_id),
    CONSTRAINT fk_questions_creator FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT chk_questions_type CHECK (question_type IN ('MCQ', 'TRUE_FALSE', 'SHORT_ANSWER', 'DESCRIPTIVE')),
    CONSTRAINT chk_questions_difficulty CHECK (difficulty IN ('EASY', 'MEDIUM', 'HARD')),
    CONSTRAINT chk_questions_source CHECK (question_source IN ('FACULTY', 'GENAI')),
    CONSTRAINT chk_questions_review CHECK (review_status IN ('DRAFT', 'PENDING_REVIEW', 'APPROVED', 'REJECTED')),
    CONSTRAINT chk_questions_objective_answer
        CHECK (question_type NOT IN ('MCQ', 'TRUE_FALSE') OR correct_answer IS NOT NULL)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS tests (
    test_id BIGINT NOT NULL AUTO_INCREMENT,
    subject_id BIGINT NOT NULL,
    section_id BIGINT NOT NULL,
    created_by BIGINT NULL,
    title VARCHAR(160) NOT NULL,
    description TEXT NULL,
    duration_minutes INT NULL,
    start_at DATETIME NULL,
    end_at DATETIME NULL,
    max_attempts SMALLINT NOT NULL DEFAULT 1,
    status VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (test_id),
    KEY idx_tests_section_status (section_id, status, start_at),
    KEY idx_tests_subject (subject_id),
    CONSTRAINT fk_tests_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),
    CONSTRAINT fk_tests_section FOREIGN KEY (section_id)
        REFERENCES sections(section_id),
    CONSTRAINT fk_tests_creator FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT chk_tests_duration CHECK (duration_minutes IS NULL OR duration_minutes > 0),
    CONSTRAINT chk_tests_attempts CHECK (max_attempts > 0),
    CONSTRAINT chk_tests_status CHECK (status IN ('DRAFT', 'PUBLISHED', 'CLOSED')),
    CONSTRAINT chk_tests_dates CHECK (end_at IS NULL OR start_at IS NULL OR end_at > start_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS test_questions (
    test_id BIGINT NOT NULL,
    question_id BIGINT NOT NULL,
    marks DECIMAL(8, 2) NOT NULL,
    question_order INT NOT NULL,
    PRIMARY KEY (test_id, question_id),
    UNIQUE KEY uq_test_question_order (test_id, question_order),
    KEY idx_test_questions_question (question_id),
    CONSTRAINT fk_test_questions_test FOREIGN KEY (test_id)
        REFERENCES tests(test_id) ON DELETE CASCADE,
    CONSTRAINT fk_test_questions_question FOREIGN KEY (question_id)
        REFERENCES questions(question_id),
    CONSTRAINT chk_test_questions_marks CHECK (marks > 0),
    CONSTRAINT chk_test_questions_order CHECK (question_order > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS test_attempts (
    attempt_id BIGINT NOT NULL AUTO_INCREMENT,
    test_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    attempt_number SMALLINT NOT NULL DEFAULT 1,
    started_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    submitted_at DATETIME NULL,
    score DECIMAL(8, 2) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'IN_PROGRESS',
    PRIMARY KEY (attempt_id),
    UNIQUE KEY uq_attempt_number (test_id, student_id, attempt_number),
    KEY idx_attempts_student_status (student_id, status),
    KEY idx_attempts_test_student (test_id, student_id),
    CONSTRAINT fk_attempts_test FOREIGN KEY (test_id)
        REFERENCES tests(test_id),
    CONSTRAINT fk_attempts_student FOREIGN KEY (student_id)
        REFERENCES users(user_id),
    CONSTRAINT chk_attempt_number CHECK (attempt_number > 0),
    CONSTRAINT chk_attempt_score CHECK (score IS NULL OR score >= 0),
    CONSTRAINT chk_attempt_status CHECK (status IN ('IN_PROGRESS', 'SUBMITTED', 'EVALUATED', 'CANCELLED')),
    CONSTRAINT chk_attempt_dates CHECK (submitted_at IS NULL OR submitted_at >= started_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS student_answers (
    answer_id BIGINT NOT NULL AUTO_INCREMENT,
    attempt_id BIGINT NOT NULL,
    question_id BIGINT NOT NULL,
    answer_text TEXT NULL,
    awarded_marks DECIMAL(8, 2) NULL,
    feedback TEXT NULL,
    evaluated_by BIGINT NULL,
    answered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (answer_id),
    UNIQUE KEY uq_answer_attempt_question (attempt_id, question_id),
    KEY idx_answers_question (question_id),
    CONSTRAINT fk_answers_attempt FOREIGN KEY (attempt_id)
        REFERENCES test_attempts(attempt_id) ON DELETE CASCADE,
    CONSTRAINT fk_answers_question FOREIGN KEY (question_id)
        REFERENCES questions(question_id),
    CONSTRAINT fk_answers_evaluator FOREIGN KEY (evaluated_by)
        REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT chk_answers_marks CHECK (awarded_marks IS NULL OR awarded_marks >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 3. ASSIGNMENTS AND ATTENDANCE

CREATE TABLE IF NOT EXISTS assignments (
    assignment_id BIGINT NOT NULL AUTO_INCREMENT,
    subject_id BIGINT NOT NULL,
    section_id BIGINT NOT NULL,
    created_by BIGINT NULL,
    title VARCHAR(160) NOT NULL,
    description TEXT NULL,
    due_at DATETIME NOT NULL,
    max_marks DECIMAL(8, 2) NOT NULL DEFAULT 100,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (assignment_id),
    KEY idx_assignments_section_due (section_id, due_at),
    CONSTRAINT fk_assignments_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),
    CONSTRAINT fk_assignments_section FOREIGN KEY (section_id)
        REFERENCES sections(section_id),
    CONSTRAINT fk_assignments_creator FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT chk_assignments_max_marks CHECK (max_marks > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS submissions (
    submission_id BIGINT NOT NULL AUTO_INCREMENT,
    assignment_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    file_url TEXT NULL,
    answer_text TEXT NULL,
    submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    marks_awarded DECIMAL(8, 2) NULL,
    feedback TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'SUBMITTED',
    PRIMARY KEY (submission_id),
    UNIQUE KEY uq_submission_assignment_student (assignment_id, student_id),
    KEY idx_submissions_student (student_id),
    CONSTRAINT fk_submissions_assignment FOREIGN KEY (assignment_id)
        REFERENCES assignments(assignment_id) ON DELETE CASCADE,
    CONSTRAINT fk_submissions_student FOREIGN KEY (student_id)
        REFERENCES users(user_id),
    CONSTRAINT chk_submissions_payload CHECK (file_url IS NOT NULL OR answer_text IS NOT NULL),
    CONSTRAINT chk_submissions_marks CHECK (marks_awarded IS NULL OR marks_awarded >= 0),
    CONSTRAINT chk_submissions_status CHECK (status IN ('SUBMITTED', 'GRADED', 'RETURNED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS class_sessions (
    session_id BIGINT NOT NULL AUTO_INCREMENT,
    subject_id BIGINT NOT NULL,
    section_id BIGINT NOT NULL,
    topic_id BIGINT NULL,
    session_date DATE NOT NULL,
    starts_at TIME NULL,
    marked_by BIGINT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (session_id),
    UNIQUE KEY uq_class_session (section_id, subject_id, session_date, starts_at),
    KEY idx_class_sessions_subject_date (subject_id, session_date),
    CONSTRAINT fk_sessions_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),
    CONSTRAINT fk_sessions_section FOREIGN KEY (section_id)
        REFERENCES sections(section_id),
    CONSTRAINT fk_sessions_topic FOREIGN KEY (topic_id)
        REFERENCES topics(topic_id),
    CONSTRAINT fk_sessions_marker FOREIGN KEY (marked_by)
        REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS attendance_records (
    attendance_id BIGINT NOT NULL AUTO_INCREMENT,
    session_id BIGINT NOT NULL,
    student_id BIGINT NOT NULL,
    status VARCHAR(15) NOT NULL,
    remarks TEXT NULL,
    recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (attendance_id),
    UNIQUE KEY uq_attendance_session_student (session_id, student_id),
    KEY idx_attendance_student_status (student_id, status),
    CONSTRAINT fk_attendance_session FOREIGN KEY (session_id)
        REFERENCES class_sessions(session_id) ON DELETE CASCADE,
    CONSTRAINT fk_attendance_student FOREIGN KEY (student_id)
        REFERENCES users(user_id),
    CONSTRAINT chk_attendance_status CHECK (status IN ('PRESENT', 'ABSENT', 'LATE', 'LEAVE'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 4. AI-ASSISTED STUDY PLANS AND RISK SIGNALS

CREATE TABLE IF NOT EXISTS study_plans (
    plan_id BIGINT NOT NULL AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    subject_id BIGINT NULL,
    created_by BIGINT NULL,
    generated_by VARCHAR(20) NOT NULL DEFAULT 'AI',
    title VARCHAR(160) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (plan_id),
    KEY idx_study_plans_student_status (student_id, status),
    CONSTRAINT fk_study_plans_student FOREIGN KEY (student_id)
        REFERENCES users(user_id),
    CONSTRAINT fk_study_plans_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),
    CONSTRAINT fk_study_plans_creator FOREIGN KEY (created_by)
        REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT chk_study_plans_source CHECK (generated_by IN ('AI', 'FACULTY', 'STUDENT')),
    CONSTRAINT chk_study_plans_status CHECK (status IN ('ACTIVE', 'COMPLETED', 'CANCELLED')),
    CONSTRAINT chk_study_plans_dates CHECK (end_date >= start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS study_plan_items (
    plan_item_id BIGINT NOT NULL AUTO_INCREMENT,
    plan_id BIGINT NOT NULL,
    topic_id BIGINT NOT NULL,
    scheduled_date DATE NOT NULL,
    recommendation TEXT NOT NULL,
    estimated_minutes INT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    PRIMARY KEY (plan_item_id),
    UNIQUE KEY uq_study_plan_topic_date (plan_id, topic_id, scheduled_date),
    KEY idx_study_plan_items_topic (topic_id),
    CONSTRAINT fk_study_plan_items_plan FOREIGN KEY (plan_id)
        REFERENCES study_plans(plan_id) ON DELETE CASCADE,
    CONSTRAINT fk_study_plan_items_topic FOREIGN KEY (topic_id)
        REFERENCES topics(topic_id),
    CONSTRAINT chk_study_plan_minutes CHECK (estimated_minutes IS NULL OR estimated_minutes > 0),
    CONSTRAINT chk_study_plan_item_status CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'SKIPPED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS risk_predictions (
    prediction_id BIGINT NOT NULL AUTO_INCREMENT,
    student_id BIGINT NOT NULL,
    subject_id BIGINT NULL,
    risk_score DECIMAL(5, 2) NULL,
    risk_level VARCHAR(10) NULL,
    model_version VARCHAR(80) NULL,
    input_features JSON NOT NULL,
    explanation TEXT NULL,
    predicted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (prediction_id),
    KEY idx_risk_predictions_latest (student_id, subject_id, predicted_at, prediction_id),
    CONSTRAINT fk_risk_predictions_student FOREIGN KEY (student_id)
        REFERENCES users(user_id),
    CONSTRAINT fk_risk_predictions_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id),
    CONSTRAINT chk_risk_score CHECK (risk_score IS NULL OR risk_score BETWEEN 0 AND 100),
    CONSTRAINT chk_risk_level CHECK (risk_level IS NULL OR risk_level IN ('LOW', 'MEDIUM', 'HIGH'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE IF NOT EXISTS ai_generation_history (
    generation_id BIGINT NOT NULL AUTO_INCREMENT,
    user_id BIGINT NULL,
    generation_type VARCHAR(30) NOT NULL,
    input_data JSON NOT NULL,
    output_data JSON NOT NULL,
    model_name VARCHAR(120) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (generation_id),
    KEY idx_ai_history_user_type_date (user_id, generation_type, created_at),
    CONSTRAINT fk_ai_history_user FOREIGN KEY (user_id)
        REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT chk_ai_generation_type
        CHECK (generation_type IN ('QUESTION_PAPER', 'DOUBT_EXPLANATION', 'STUDY_PLAN', 'ANSWER_FEEDBACK'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- 5. ANALYTICS VIEWS

-- Performance by student and topic, using completed/evaluated attempts only.
CREATE OR REPLACE VIEW student_topic_performance AS
SELECT
    ta.student_id,
    t.subject_id,
    q.topic_id,
    COUNT(DISTINCT ta.attempt_id) AS evaluated_attempts,
    SUM(COALESCE(sa.awarded_marks, 0)) AS marks_earned,
    SUM(tq.marks) AS marks_possible,
    ROUND(100.0 * SUM(COALESCE(sa.awarded_marks, 0)) / NULLIF(SUM(tq.marks), 0), 2) AS performance_percent
FROM test_attempts ta
JOIN tests te ON te.test_id = ta.test_id
JOIN test_questions tq ON tq.test_id = te.test_id
JOIN questions q ON q.question_id = tq.question_id
JOIN topics t ON t.topic_id = q.topic_id
LEFT JOIN student_answers sa
    ON sa.attempt_id = ta.attempt_id
   AND sa.question_id = q.question_id
WHERE ta.status = 'EVALUATED'
GROUP BY ta.student_id, t.subject_id, q.topic_id;

-- Attendance percentage by student and subject. LATE counts as attended; LEAVE remains in the denominator.
CREATE OR REPLACE VIEW student_attendance_summary AS
SELECT
    ar.student_id,
    cs.subject_id,
    COUNT(*) AS recorded_sessions,
    SUM(CASE WHEN ar.status IN ('PRESENT', 'LATE') THEN 1 ELSE 0 END) AS attended_sessions,
    SUM(CASE WHEN ar.status = 'ABSENT' THEN 1 ELSE 0 END) AS absent_sessions,
    ROUND(
        100.0 * SUM(CASE WHEN ar.status IN ('PRESENT', 'LATE') THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
        2
    ) AS attendance_percent
FROM attendance_records ar
JOIN class_sessions cs ON cs.session_id = ar.session_id
GROUP BY ar.student_id, cs.subject_id;

-- Latest model output plus simple attention flags for faculty/HOD review.
-- The 40% score and 60% attendance thresholds are demo defaults; tune them with faculty.
CREATE OR REPLACE VIEW student_subject_dashboard AS
WITH active_student_subjects AS (
    SELECT DISTINCT e.student_id, sec.course_id, sub.subject_id
    FROM student_enrollments e
    JOIN sections sec ON sec.section_id = e.section_id
    JOIN subjects sub ON sub.course_id = sec.course_id
    WHERE e.status = 'ACTIVE'
), performance AS (
    SELECT student_id, subject_id, ROUND(AVG(performance_percent), 2) AS average_topic_score
    FROM student_topic_performance
    GROUP BY student_id, subject_id
), latest_prediction_ranked AS (
    SELECT student_id, subject_id, risk_score, risk_level, explanation, predicted_at,
           ROW_NUMBER() OVER (
               PARTITION BY student_id, subject_id
               ORDER BY predicted_at DESC, prediction_id DESC
           ) AS row_num
    FROM risk_predictions
    WHERE subject_id IS NOT NULL
), latest_prediction AS (
    SELECT student_id, subject_id, risk_score, risk_level, explanation, predicted_at
    FROM latest_prediction_ranked
    WHERE row_num = 1
)
SELECT
    ass.student_id,
    ass.course_id,
    ass.subject_id,
    p.average_topic_score,
    a.attendance_percent,
    lp.risk_score,
    lp.risk_level,
    lp.explanation AS risk_explanation,
    lp.predicted_at AS risk_predicted_at,
    COALESCE(
        lp.risk_level = 'HIGH'
        OR (p.average_topic_score IS NOT NULL AND p.average_topic_score < 40)
        OR (a.attendance_percent IS NOT NULL AND a.attendance_percent < 60),
        FALSE
    ) AS needs_attention
FROM active_student_subjects ass
LEFT JOIN performance p
    ON p.student_id = ass.student_id AND p.subject_id = ass.subject_id
LEFT JOIN student_attendance_summary a
    ON a.student_id = ass.student_id AND a.subject_id = ass.subject_id
LEFT JOIN latest_prediction lp
    ON lp.student_id = ass.student_id AND lp.subject_id = ass.subject_id;

-- 6. COMMON APPLICATION QUERIES
-- Examples below are commented so they do not run during setup. Replace example IDs with bound parameters.

-- A. Published tests available to one enrolled student.
-- SELECT te.test_id, te.title, te.duration_minutes, te.start_at, te.end_at
-- FROM tests te
-- JOIN student_enrollments e ON e.section_id = te.section_id
-- WHERE e.student_id = 1
--   AND e.status = 'ACTIVE'
--   AND te.status = 'PUBLISHED'
--   AND (te.start_at IS NULL OR te.start_at <= CURRENT_TIMESTAMP)
--   AND (te.end_at IS NULL OR te.end_at >= CURRENT_TIMESTAMP)
-- ORDER BY (te.start_at IS NOT NULL), te.start_at, te.title;

-- B. Student's topic-wise performance for one subject.
-- SELECT t.topic_name, p.evaluated_attempts, p.marks_earned,
--        p.marks_possible, p.performance_percent
-- FROM student_topic_performance p
-- JOIN topics t ON t.topic_id = p.topic_id
-- WHERE p.student_id = 1 AND p.subject_id = 1
-- ORDER BY p.performance_percent, t.topic_name;

-- C. Student's attendance by subject.
-- SELECT s.subject_name, a.recorded_sessions, a.attended_sessions,
--        a.absent_sessions, a.attendance_percent
-- FROM student_attendance_summary a
-- JOIN subjects s ON s.subject_id = a.subject_id
-- WHERE a.student_id = 1
-- ORDER BY s.subject_name;

-- D. Faculty/HOD list of students who need attention in a department.
-- SELECT u.user_id, u.full_name, u.registration_number, s.subject_name,
--        d.average_topic_score, d.attendance_percent, d.risk_score,
--        d.risk_level, d.risk_explanation
-- FROM student_subject_dashboard d
-- JOIN users u ON u.user_id = d.student_id
-- JOIN subjects s ON s.subject_id = d.subject_id
-- JOIN courses c ON c.course_id = d.course_id
-- WHERE c.department_id = 1 AND d.needs_attention = TRUE
-- ORDER BY d.risk_score DESC, u.full_name, s.subject_name;

-- E. Faculty review queue for GenAI-generated questions.
-- SELECT q.question_id, q.question_text, q.question_type, q.difficulty,
--        t.topic_name, u.full_name AS generated_by
-- FROM questions q
-- JOIN topics t ON t.topic_id = q.topic_id
-- LEFT JOIN users u ON u.user_id = q.created_by
-- WHERE q.question_source = 'GENAI' AND q.review_status = 'PENDING_REVIEW'
-- ORDER BY q.created_at;

-- F. Open assignments for one student.
-- SELECT a.assignment_id, a.title, a.description, a.due_at, a.max_marks, s.subject_name
-- FROM assignments a
-- JOIN student_enrollments e ON e.section_id = a.section_id
-- JOIN subjects s ON s.subject_id = a.subject_id
-- LEFT JOIN submissions sub
--   ON sub.assignment_id = a.assignment_id AND sub.student_id = e.student_id
-- WHERE e.student_id = 1 AND e.status = 'ACTIVE'
--   AND sub.submission_id IS NULL
-- ORDER BY a.due_at;

-- G. Auto-grade objective answers for one attempt.
-- Store the same canonical option value in questions.correct_answer and student_answers.answer_text.
-- Do not use this for SHORT_ANSWER or DESCRIPTIVE questions; faculty/AI review is required.
-- UPDATE student_answers sa
-- JOIN test_attempts ta ON ta.attempt_id = sa.attempt_id
-- JOIN test_questions tq ON tq.test_id = ta.test_id AND tq.question_id = sa.question_id
-- JOIN questions q ON q.question_id = tq.question_id
-- SET sa.awarded_marks = CASE
--         WHEN LOWER(TRIM(sa.answer_text)) = LOWER(TRIM(q.correct_answer)) THEN tq.marks
--         ELSE 0
--     END,
--     sa.feedback = CASE
--         WHEN LOWER(TRIM(sa.answer_text)) = LOWER(TRIM(q.correct_answer)) THEN 'Correct'
--         ELSE 'Incorrect'
--     END
-- WHERE ta.attempt_id = 1
--   AND q.question_type IN ('MCQ', 'TRUE_FALSE');

-- H. Refresh an attempt score after all descriptive answers have been reviewed.
-- UPDATE test_attempts ta
-- SET ta.score = (
--         SELECT COALESCE(SUM(COALESCE(sa.awarded_marks, 0)), 0)
--         FROM test_questions tq
--         LEFT JOIN student_answers sa
--           ON sa.attempt_id = ta.attempt_id AND sa.question_id = tq.question_id
--         WHERE tq.test_id = ta.test_id
--     ),
--     ta.status = 'EVALUATED',
--     ta.submitted_at = COALESCE(ta.submitted_at, CURRENT_TIMESTAMP)
-- WHERE ta.attempt_id = 1;

-- I. Save or update one answer when the student submits it.
-- INSERT INTO student_answers (attempt_id, question_id, answer_text)
-- VALUES (1, 1, 'Option A')
-- ON DUPLICATE KEY UPDATE
--     answer_text = VALUES(answer_text),
--     answered_at = CURRENT_TIMESTAMP,
--     awarded_marks = NULL,
--     feedback = NULL;

-- J. Create an attendance session and record a student's attendance.
-- INSERT INTO class_sessions (subject_id, section_id, topic_id, session_date, starts_at, marked_by)
-- VALUES (1, 1, 1, CURRENT_DATE, CURRENT_TIME, 1);
-- SET @session_id = LAST_INSERT_ID();
-- INSERT INTO attendance_records (session_id, student_id, status)
-- VALUES (@session_id, 1, 'PRESENT')
-- ON DUPLICATE KEY UPDATE status = VALUES(status), recorded_at = CURRENT_TIMESTAMP;

-- K. Save an at-risk prediction produced by the AI/ML service.
-- INSERT INTO risk_predictions
--     (student_id, subject_id, risk_score, risk_level, model_version, input_features, explanation)
-- VALUES
--     (1, 1, 82.50, 'HIGH', 'demo-v1',
--      JSON_OBJECT('average_score', 38, 'attendance_percent', 55),
--      'Low topic scores and attendance indicate follow-up is recommended.');

-- L. Save GenAI question-paper generation metadata and output.
-- Do not include real student personal data in prompts or stored generation history.
-- INSERT INTO ai_generation_history (user_id, generation_type, input_data, output_data, model_name)
-- VALUES
--     (1, 'QUESTION_PAPER',
--      JSON_OBJECT('subject_id', 1, 'topic_ids', JSON_ARRAY(1, 2), 'difficulty', 'MEDIUM'),
--      JSON_OBJECT('question_ids', JSON_ARRAY(1, 2, 3)),
--      'configured-model-name');