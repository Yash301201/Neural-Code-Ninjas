-- OULAD public research dataset. These tables never reference application users.
-- Attribution: Kuzilek, Hlosta and Zdrahal (2015), CC BY 4.0.
-- Source: https://www.kaggle.com/datasets/rocki37/open-university-learning-analytics-dataset
USE learnpath_ai;
CREATE TABLE IF NOT EXISTS oulad_imports (
 batch_id INT AUTO_INCREMENT PRIMARY KEY,
 archive_sha256 CHAR(64) NOT NULL,
 status VARCHAR(16) NOT NULL,
 source_url VARCHAR(512) NOT NULL,
 license_name VARCHAR(64) NOT NULL DEFAULT 'CC BY 4.0',
 attribution VARCHAR(512) NOT NULL,
 imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 completed_at DATETIME NULL,
 row_counts JSON NULL,
 error_message VARCHAR(1024) NULL,
 KEY idx_oulad_import_ready(status,batch_id),
 KEY idx_oulad_import_hash(archive_sha256)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_courses (
 batch_id INT NOT NULL, code_module VARCHAR(8) NOT NULL,
 code_presentation VARCHAR(12) NOT NULL, length_days INT NOT NULL,
 PRIMARY KEY(batch_id,code_module,code_presentation),
 FOREIGN KEY(batch_id) REFERENCES oulad_imports(batch_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_students (
 batch_id INT NOT NULL, code_module VARCHAR(8) NOT NULL,
 code_presentation VARCHAR(12) NOT NULL, student_id INT NOT NULL,
 previous_attempts INT NOT NULL, studied_credits INT NOT NULL,
 final_result VARCHAR(24) NOT NULL,
 PRIMARY KEY(batch_id,code_module,code_presentation,student_id),
 FOREIGN KEY(batch_id,code_module,code_presentation)
 REFERENCES oulad_courses(batch_id,code_module,code_presentation),
 KEY idx_oulad_student_lookup(batch_id,student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_registrations (
 batch_id INT NOT NULL, code_module VARCHAR(8) NOT NULL,
 code_presentation VARCHAR(12) NOT NULL, student_id INT NOT NULL,
 registration_day INT NULL, unregistration_day INT NULL,
 PRIMARY KEY(batch_id,code_module,code_presentation,student_id),
 FOREIGN KEY(batch_id,code_module,code_presentation,student_id)
 REFERENCES oulad_students(batch_id,code_module,code_presentation,student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_assessments (
 batch_id INT NOT NULL, assessment_id INT NOT NULL,
 code_module VARCHAR(8) NOT NULL, code_presentation VARCHAR(12) NOT NULL,
 assessment_type VARCHAR(16) NOT NULL, due_day INT NULL,
 weight DECIMAL(8,3) NOT NULL,
 PRIMARY KEY(batch_id,assessment_id),
 FOREIGN KEY(batch_id,code_module,code_presentation)
 REFERENCES oulad_courses(batch_id,code_module,code_presentation),
 KEY idx_oulad_assessment_scope(batch_id,code_module,code_presentation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_scores (
 batch_id INT NOT NULL, assessment_id INT NOT NULL, student_id INT NOT NULL,
 submitted_day INT NULL, is_banked BOOLEAN NOT NULL, score DECIMAL(7,3) NULL,
 PRIMARY KEY(batch_id,assessment_id,student_id),
 FOREIGN KEY(batch_id,assessment_id) REFERENCES oulad_assessments(batch_id,assessment_id),
 CONSTRAINT chk_oulad_score CHECK(score IS NULL OR score BETWEEN 0 AND 100),
 KEY idx_oulad_score_student(batch_id,student_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_vle_sites (
 batch_id INT NOT NULL, code_module VARCHAR(8) NOT NULL,
 code_presentation VARCHAR(12) NOT NULL, site_id INT NOT NULL,
 activity_type VARCHAR(64) NOT NULL, week_from INT NULL, week_to INT NULL,
 PRIMARY KEY(batch_id,code_module,code_presentation,site_id),
 FOREIGN KEY(batch_id,code_module,code_presentation)
 REFERENCES oulad_courses(batch_id,code_module,code_presentation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_weekly_engagement (
 batch_id INT NOT NULL, code_module VARCHAR(8) NOT NULL,
 code_presentation VARCHAR(12) NOT NULL, student_id INT NOT NULL,
 week_index INT NOT NULL, clicks BIGINT NOT NULL, log_records INT NOT NULL,
 active_days SMALLINT NOT NULL,
 PRIMARY KEY(batch_id,code_module,code_presentation,student_id,week_index),
 FOREIGN KEY(batch_id,code_module,code_presentation,student_id)
 REFERENCES oulad_students(batch_id,code_module,code_presentation,student_id),
 KEY idx_oulad_week_scope(batch_id,code_module,code_presentation,week_index),
 CONSTRAINT chk_oulad_week_clicks CHECK(clicks>=0),
 CONSTRAINT chk_oulad_active_days CHECK(active_days BETWEEN 1 AND 7)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS oulad_weekly_activity (
 batch_id INT NOT NULL, code_module VARCHAR(8) NOT NULL,
 code_presentation VARCHAR(12) NOT NULL, week_index INT NOT NULL,
 activity_type VARCHAR(64) NOT NULL, clicks BIGINT NOT NULL, log_records INT NOT NULL,
 PRIMARY KEY(batch_id,code_module,code_presentation,week_index,activity_type),
 FOREIGN KEY(batch_id,code_module,code_presentation)
 REFERENCES oulad_courses(batch_id,code_module,code_presentation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
