-- LearnPath AI: read-only queries for the imported OULAD dataset.
-- Public anonymized research data, separate from learnpath_ai.users.
USE learnpath_ai;
SET @batch_id=(SELECT MAX(batch_id) FROM oulad_imports WHERE status='READY');
SET @module='BBB';
SET @presentation='2014J';
SET @start_week=0;
SET @end_week=12;

-- 1. Dataset provenance and verified source counts.
SELECT batch_id,status,source_url,license_name,attribution,archive_sha256,row_counts
FROM oulad_imports WHERE batch_id=@batch_id;

-- 2. Source enrollments versus distinct anonymous learners.
SELECT COUNT(*) AS course_enrollments,COUNT(DISTINCT student_id) AS distinct_learners
FROM oulad_students WHERE batch_id=@batch_id;

-- 3. Weekly line-chart data. Clicks are engagement, not attendance.
SELECT week_index,SUM(clicks) AS clicks,
 COUNT(DISTINCT CASE WHEN clicks>0 THEN student_id END) AS active_learners
FROM oulad_weekly_engagement
WHERE batch_id=@batch_id AND code_module=@module AND code_presentation=@presentation
 AND week_index BETWEEN @start_week AND @end_week
GROUP BY week_index ORDER BY week_index;

-- 4. Heatmap source (learner by week). Missing cells are displayed as no recorded clicks.
SELECT student_id,week_index,clicks,active_days
FROM oulad_weekly_engagement
WHERE batch_id=@batch_id AND code_module=@module AND code_presentation=@presentation
 AND week_index BETWEEN @start_week AND @end_week
ORDER BY student_id,week_index;

-- 5. Assessment-score trends; exclude missing scores and prior banked credits.
SELECT FLOOR(g.submitted_day/7) AS week_index,AVG(g.score) AS mean_score,COUNT(*) AS graded_submissions
FROM oulad_scores g JOIN oulad_assessments a
 ON a.batch_id=g.batch_id AND a.assessment_id=g.assessment_id
WHERE a.batch_id=@batch_id AND a.code_module=@module AND a.code_presentation=@presentation
 AND g.score IS NOT NULL AND g.is_banked=FALSE
 AND g.submitted_day BETWEEN @start_week*7 AND @end_week*7+6
GROUP BY FLOOR(g.submitted_day/7) ORDER BY week_index;

-- 6. Historical outcome bars/donut: full course, not an early risk prediction.
SELECT final_result,COUNT(*) AS enrollment_count FROM oulad_students
WHERE batch_id=@batch_id AND code_module=@module AND code_presentation=@presentation
GROUP BY final_result;

-- 7. Resource interaction bar chart.
SELECT activity_type,SUM(clicks) AS clicks FROM oulad_weekly_activity
WHERE batch_id=@batch_id AND code_module=@module AND code_presentation=@presentation
 AND week_index BETWEEN @start_week AND @end_week
GROUP BY activity_type ORDER BY clicks DESC;
