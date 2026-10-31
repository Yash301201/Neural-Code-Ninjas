# Verification performed

Verified 2026-10-31 on Windows with Python 3.12, MySQL Community Server 8.0.46, SQLAlchemy 2.0.55 and the packages recorded in requirements.lock.txt.

- Installed the dependencies into the project's .venv.
- Created a separate MySQL data directory under .local/mysql-data, bound to 127.0.0.1:3307; no existing MySQL service/database was modified.
- Applied the full schema, calendar extension and synthetic seed SQL successfully to learnpath_ai: 22 tables, three reporting views, six initial user records including a generated local administrator.
- Verified the generated administrator can log in and retrieve its own profile; password hash is omitted from responses.
- Generated docs/openapi.json from the initialized application: 54 operations.
- Ran seven MySQL integration tests using the project virtualenv and a separate learnpath_ai_test database. Result: **7 passed**. Tests cover login/role checks, answer-key redaction, section isolation, objective grading, duplicate submissions, frozen published questions, descriptive review and mark bounds, invalid questions, duration expiry, assignment deadlines and grades, attendance, performance, risk, plans, dashboards, AI review gating, malformed provider output and disabled accounts.
- Executed start-local.ps1 and verified real HTTP health, docs and OpenAPI endpoints.

The installed Starlette version emits one deprecation warning about TestClient's httpx transport; assertions pass. A real LLM call was not made because no provider key was supplied; generated-question integration uses a mocked provider and missing-key handling is tested. Docker configuration is supplied but was not executed (Docker is unavailable). The local risk and prioritization features are heuristics, not a trained ML model. Load/performance testing at the brief's full college scale has not been performed. No frontend is included in this backend phase.
