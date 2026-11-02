-- Additive tables for live attendance, scheduled MCQ exams and management history.
CREATE TABLE IF NOT EXISTS attendance_registers (
 session_id BIGINT PRIMARY KEY,
 version INT NOT NULL DEFAULT 1,
 updated_by BIGINT NOT NULL,
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(session_id) REFERENCES class_sessions(session_id),
 FOREIGN KEY(updated_by) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS campus_audit (
 audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
 actor_id BIGINT NOT NULL,
 department_id BIGINT NULL,
 action VARCHAR(40) NOT NULL,
 entity_type VARCHAR(40) NOT NULL,
 entity_id BIGINT NOT NULL,
 reason VARCHAR(500) NOT NULL,
 before_data JSON NULL,
 after_data JSON NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(actor_id) REFERENCES users(user_id),
 KEY ix_campus_audit_department(department_id,audit_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS exam_series (
 request_key VARCHAR(36) PRIMARY KEY,
 fingerprint CHAR(64) NOT NULL,
 created_by BIGINT NOT NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(created_by) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS exam_schedules (
 test_id BIGINT PRIMARY KEY,
 request_key VARCHAR(36) NOT NULL,
 exam_type VARCHAR(12) NOT NULL,
 occurrence_number INT NOT NULL,
 FOREIGN KEY(test_id) REFERENCES tests(test_id),
 FOREIGN KEY(request_key) REFERENCES exam_series(request_key),
 CHECK(exam_type IN ('DAILY','WEEKLY','FINAL'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS exam_answer_drafts (
 attempt_id BIGINT NOT NULL,
 question_id BIGINT NOT NULL,
 answer_text TEXT NOT NULL,
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(attempt_id,question_id),
 FOREIGN KEY(attempt_id) REFERENCES test_attempts(attempt_id),
 FOREIGN KEY(question_id) REFERENCES questions(question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
