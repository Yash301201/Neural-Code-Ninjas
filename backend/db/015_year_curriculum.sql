-- Additive academic-year classification and curriculum coverage.
CREATE TABLE IF NOT EXISTS section_study_years (
 section_id BIGINT PRIMARY KEY,
 study_year SMALLINT NOT NULL,
 FOREIGN KEY(section_id) REFERENCES sections(section_id),
 CHECK(study_year BETWEEN 1 AND 8)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS subject_curriculum (
 subject_id BIGINT PRIMARY KEY,
 study_year SMALLINT NOT NULL,
 semester SMALLINT NOT NULL,
 FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),
 CHECK(study_year BETWEEN 1 AND 8),
 CHECK(semester BETWEEN 1 AND 16)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS teaching_topic_progress (
 faculty_assignment_id BIGINT NOT NULL,
 topic_id BIGINT NOT NULL,
 status VARCHAR(16) NOT NULL DEFAULT 'PLANNED',
 updated_by BIGINT NOT NULL,
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 PRIMARY KEY(faculty_assignment_id,topic_id),
 FOREIGN KEY(faculty_assignment_id) REFERENCES faculty_subject_assignments(faculty_assignment_id),
 FOREIGN KEY(topic_id) REFERENCES topics(topic_id),
 FOREIGN KEY(updated_by) REFERENCES users(user_id),
 CHECK(status IN ('PLANNED','IN_PROGRESS','COMPLETED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
