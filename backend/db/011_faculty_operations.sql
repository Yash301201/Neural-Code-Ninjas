-- Additive faculty operations. Course IDs keep UG/PG records related, not duplicated.
CREATE TABLE IF NOT EXISTS course_programs (
 course_id BIGINT PRIMARY KEY,
 program_level VARCHAR(16) NOT NULL DEFAULT 'UNCLASSIFIED',
 updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(course_id) REFERENCES courses(course_id),
 CHECK(program_level IN ('UG','PG','UNCLASSIFIED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
INSERT IGNORE INTO course_programs(course_id,program_level)
SELECT course_id, CASE
 WHEN LEFT(UPPER(REPLACE(REPLACE(course_name,'.',''),' ','')),5) = 'BTECH' THEN 'UG'
 WHEN LEFT(UPPER(REPLACE(REPLACE(course_name,'.',''),' ','')),5) = 'MTECH'
 OR LEFT(UPPER(REPLACE(REPLACE(course_name,'.',''),' ','')),8) = 'MASTEROF' THEN 'PG'
 ELSE 'UNCLASSIFIED' END FROM courses;
CREATE TABLE IF NOT EXISTS faculty_timetable (
 slot_id BIGINT AUTO_INCREMENT PRIMARY KEY,
 faculty_id BIGINT NOT NULL,
 subject_id BIGINT NOT NULL,
 section_id BIGINT NOT NULL,
 weekday SMALLINT NOT NULL,
 starts_at TIME NOT NULL,
 ends_at TIME NOT NULL,
 room VARCHAR(80) NOT NULL,
 session_type VARCHAR(20) NOT NULL DEFAULT 'LECTURE',
 is_active BOOLEAN NOT NULL DEFAULT TRUE,
 created_by BIGINT NOT NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(faculty_id) REFERENCES users(user_id),
 FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),
 FOREIGN KEY(section_id) REFERENCES sections(section_id),
 FOREIGN KEY(created_by) REFERENCES users(user_id),
 CHECK(weekday BETWEEN 0 AND 6), CHECK(ends_at>starts_at),
 CHECK(session_type IN ('LECTURE','LAB','TUTORIAL')),
 KEY ix_timetable_faculty_day(faculty_id,weekday,is_active),
 KEY ix_timetable_section_day(section_id,weekday,is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
CREATE TABLE IF NOT EXISTS faculty_leave_requests (
 leave_id BIGINT AUTO_INCREMENT PRIMARY KEY,
 requester_id BIGINT NOT NULL,
 start_date DATE NOT NULL,
 end_date DATE NOT NULL,
 leave_type VARCHAR(20) NOT NULL,
 reason VARCHAR(1000) NOT NULL,
 status VARCHAR(16) NOT NULL DEFAULT 'PENDING',
 reviewed_by BIGINT NULL,
 review_note VARCHAR(500) NULL,
 reviewed_at DATETIME NULL,
 created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY(requester_id) REFERENCES users(user_id),
 FOREIGN KEY(reviewed_by) REFERENCES users(user_id),
 CHECK(end_date>=start_date),
 CHECK(status IN ('PENDING','APPROVED','REJECTED','CANCELLED')),
 CHECK(leave_type IN ('CASUAL','SICK','PERSONAL','ACADEMIC')),
 KEY ix_faculty_leave_owner(requester_id,status,start_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
