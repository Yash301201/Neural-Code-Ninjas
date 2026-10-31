# Brief-to-backend coverage

| Requirement | Implementation |
| --- | --- |
| Four roles and secure login | /auth/login, /auth/me, administrator-managed accounts, Argon2 + JWT |
| Organization/course management | departments, courses, sections, subjects, topics catalog APIs |
| Student/faculty mapping | /enrollments, /faculty-assignments |
| Reviewable question bank | /questions with edit/review and published-question freeze |
| Online tests and objective evaluation | /tests, attempt start, submit, automatic scores |
| Descriptive evaluation | /answers/{id}/grade, /ai/answers/{id}/feedback |
| Progress by topic | /students/{id}/performance |
| Assignment submission/deadlines | assignment and submission endpoints |
| Attendance tied to progress | /attendance and performance metrics |
| Early risk identification | /students/{id}/risk; explicitly a heuristic baseline |
| Personalized study plans | /study-plans and item status; rule-based prioritization |
| GenAI question generation | /ai/questions, persisted pending-review bank entries |
| English/Telugu explanations | /ai/doubts with selected language |
| Faculty/HOD/admin dashboards | /dashboard and department learning gaps |
| Academic calendar | academic_events catalog |
| Synthetic demonstration data | db/002_sample_data.sql |
| Schema, API documentation, architecture | db/, Swagger, docs/openapi.json, README Mermaid diagram |

The user's requested phase is the database and backend. The brief's React UI, presentation and repository publishing are outside that phase. Live LLM functionality requires configured provider credentials. No predictive accuracy is claimed for the heuristic baseline.
