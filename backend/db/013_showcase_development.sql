CREATE TABLE IF NOT EXISTS staff_evidence (
 evidence_id BIGINT AUTO_INCREMENT PRIMARY KEY,
 owner_id BIGINT NOT NULL,
 category VARCHAR(20) NOT NULL,
 title VARCHAR(160) NOT NULL,
 details TEXT NOT NULL,
 reference_url VARCHAR(512) NULL,
 skill_level SMALLINT NULL,
 status VARCHAR(16) NOT NULL DEFAULT 'SUBMITTED',
 review_note VARCHAR(500) NULL,
 reviewed_by BIGINT NULL,
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(owner_id) REFERENCES users(user_id),
 FOREIGN KEY(reviewed_by) REFERENCES users(user_id),
 CHECK(category IN ('SKILL','RESUME','RESEARCH','COLLABORATION','TRAINING')),
 CHECK(status IN ('SUBMITTED','VERIFIED','RETURNED','ARCHIVED')),
 CHECK(skill_level IS NULL OR skill_level BETWEEN 1 AND 5),
 KEY ix_staff_evidence_owner(owner_id,status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS staff_feedback (
 feedback_id BIGINT AUTO_INCREMENT PRIMARY KEY,
 author_id BIGINT NOT NULL,
 faculty_id BIGINT NOT NULL,
 context_key VARCHAR(80) NOT NULL,
 subject_id BIGINT NULL,
 section_id BIGINT NULL,
 clarity SMALLINT NOT NULL,
 interaction SMALLINT NOT NULL,
 comments VARCHAR(1000) NOT NULL,
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(author_id) REFERENCES users(user_id),
 FOREIGN KEY(faculty_id) REFERENCES users(user_id),
 FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),
 FOREIGN KEY(section_id) REFERENCES sections(section_id),
 UNIQUE KEY uq_staff_feedback(author_id,faculty_id,context_key),
 CHECK(clarity BETWEEN 1 AND 5), CHECK(interaction BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS course_dataset_links (
 course_id BIGINT PRIMARY KEY,
 batch_id INT NOT NULL,
 code_module VARCHAR(8) NOT NULL,
 code_presentation VARCHAR(12) NOT NULL,
 linked_by BIGINT NOT NULL,
 FOREIGN KEY(course_id) REFERENCES courses(course_id),
 FOREIGN KEY(linked_by) REFERENCES users(user_id),
 CONSTRAINT fk_showcase_dataset_cohort FOREIGN KEY(batch_id,code_module,code_presentation)
 REFERENCES oulad_courses(batch_id,code_module,code_presentation)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS demo_showcase_runs (
 run_key VARCHAR(60) PRIMARY KEY,
 created_by BIGINT NOT NULL,
 summary JSON NOT NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(created_by) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
