-- Read-only reports for the year-wise academic workspace.
USE learnpath_ai;

-- Curriculum minimums per degree: 24 (UG4), 18 (UG3), 15 (PG2).
SELECT c.course_name,p.program_level,c.duration_years,COUNT(sc.subject_id) AS curriculum_subjects,
CASE WHEN p.program_level='UG' AND c.duration_years=4 THEN 24
 WHEN p.program_level='UG' AND c.duration_years=3 THEN 18
 WHEN p.program_level='PG' AND c.duration_years=2 THEN 15 ELSE NULL END AS minimum_subjects
FROM courses c JOIN course_programs p ON p.course_id=c.course_id
LEFT JOIN subjects s ON s.course_id=c.course_id
LEFT JOIN subject_curriculum sc ON sc.subject_id=s.subject_id
GROUP BY c.course_id,c.course_name,p.program_level,c.duration_years ORDER BY c.course_id;

-- Student counts per program, study year and section.
SELECT p.program_level,c.course_name,sy.study_year,sec.section_name,sec.academic_year,
COUNT(DISTINCT e.student_id) AS students
FROM sections sec JOIN courses c ON c.course_id=sec.course_id
LEFT JOIN course_programs p ON p.course_id=c.course_id
LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id
LEFT JOIN student_enrollments e ON e.section_id=sec.section_id AND e.status='ACTIVE'
GROUP BY sec.section_id,p.program_level,c.course_name,sy.study_year,sec.section_name,sec.academic_year
ORDER BY c.course_id,sy.study_year,sec.section_name;

-- Individual students with UG/PG, degree, current enrolled year and section.
SELECT u.user_id,u.full_name,u.email,p.program_level,c.course_name,sy.study_year,
sec.section_name,sec.academic_year
FROM users u JOIN student_enrollments e ON e.student_id=u.user_id AND e.status='ACTIVE'
JOIN sections sec ON sec.section_id=e.section_id JOIN courses c ON c.course_id=sec.course_id
LEFT JOIN course_programs p ON p.course_id=c.course_id
LEFT JOIN section_study_years sy ON sy.section_id=sec.section_id
WHERE u.role='STUDENT' ORDER BY c.course_id,sy.study_year,sec.section_name,u.full_name;

-- Subjects and their semester/year.
SELECT c.course_name,p.program_level,sc.study_year,sc.semester,s.subject_name,s.subject_code
FROM subject_curriculum sc JOIN subjects s ON s.subject_id=sc.subject_id
JOIN courses c ON c.course_id=s.course_id JOIN course_programs p ON p.course_id=c.course_id
ORDER BY c.course_id,sc.study_year,sc.semester,s.subject_name;

-- Faculty allocations with planned/completed topics.
SELECT u.full_name AS faculty,c.course_name,p.program_level,sc.study_year,sc.semester,
sec.section_name,sec.academic_year,s.subject_name,t.topic_name,
COALESCE(progress.status,'PLANNED') AS topic_status
FROM faculty_subject_assignments f JOIN users u ON u.user_id=f.faculty_id
JOIN subjects s ON s.subject_id=f.subject_id JOIN subject_curriculum sc ON sc.subject_id=s.subject_id
JOIN courses c ON c.course_id=s.course_id JOIN course_programs p ON p.course_id=c.course_id
JOIN sections sec ON sec.section_id=f.section_id LEFT JOIN topics t ON t.subject_id=s.subject_id
LEFT JOIN teaching_topic_progress progress ON progress.faculty_assignment_id=f.faculty_assignment_id AND progress.topic_id=t.topic_id
ORDER BY u.user_id,c.course_id,sc.study_year,s.subject_id,sec.section_id,t.topic_id;
