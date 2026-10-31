# Groq LLM + MySQL RAG assistant

AI Knowledge Assistant is available in all four role sidebars. MySQL stores 905 public retrieval chunks and owner-scoped conversation history. Configure LLM_API_KEY in backend/.env and restart for Groq generation; evidence retrieval works without it. See backend/docs/rag-integration.md for setup, database migration and verification.

# New: Kaggle OULAD analytics

OULAD is now imported into separate MySQL analytics tables. Sign in and open **Dataset Analytics** in the sidebar for heatmaps, line/area graphs, bar charts, outcome summaries and learner drill-downs. See `backend/docs/oulad-integration.md` for source attribution, import counts and validation. Emails and passwords are unchanged; fictional student/faculty display names are localized.

---

# LearnPath AI - ZIP frontend integration

The uploaded learnpath-ai.zip React design is integrated in `frontend-react/`. Its login illustration, blue/violet styling, responsive role layouts, sidebar, buttons, confirmation dialog and toasts are retained. Active pages use FastAPI and MySQL instead of the ZIP's in-memory preview state. The original ZIP and previous frontend in `frontend/` are preserved. The original preview page sources remain for reference but are not imported into the production entry point; active pages are in `src/pages/LivePages.tsx`.

## Run from your current backend terminal

```powershell
cd "C:\Users\DELL\OneDrive\Yash\OneDrive\Desktop\LearnPathAI\backend"
powershell -ExecutionPolicy Bypass -File .\start-project.ps1
```

The same command works from the parent LearnPathAI folder. Open **http://127.0.0.1:8001/app/**. Select Student / Faculty / HOD / Admin, then enter the matching credentials from `backend/.local/portal-logins.txt`. A separate copy was delivered in `LearnPathAI-role-credentials.txt`. The four portal accounts now use user-requested simple local passwords; see backend/.local/portal-logins.txt. Reapply them with python -m scripts.set_local_demo_passwords from backend/. Existing demo and personal administrator credentials are unchanged.

| Role | Email | Mapping |
| --- | --- | --- |
| Admin | admin@learnpath.dev | Institution administration |
| HOD | hod@learnpath.dev | Existing department |
| Faculty | faculty@learnpath.dev | Existing department subjects and sections |
| Student | student@learnpath.dev | Existing course/section |

New users start with their own records. The newly created Portal Student completed one synthetic practice attempt during verification (6 marks) and has a generated study plan. Original sample students retain their previous work. No passwords are stored in the React bundle. The generated local credentials file is private reference material; MySQL stores Argon2id hashes in users.password_hash.

## Connected workflows

- Login validates actual credentials. Role navigation is based on `/auth/me`; choosing a role does not grant that role. Protected routes redirect mismatched users to their own workspace.
- Dashboard scores, enrollment counts, attendance, history and charts use stored academic records. Unassessed users show `Awaiting data`; missing scores remain blank rather than fabricated.
- Faculty manages topics and question banks, creates tests from approved questions, publishes/closes papers, and reviews objective/descriptive results. Generated questions require review.
- Students take server-timed assessments, save answers in their browser tab, submit to FastAPI, and receive persisted objective scores. Faculty assigns final marks to descriptive answers.
- Assignments support creation, student text submissions, faculty grading and feedback. Deadlines and mark bounds are enforced by the backend.
- Attendance records one class session for the selected section; the same records feed analytics.
- Study plans are generated from topic history; checkboxes persist progress to MySQL. Risk and prioritization are documented heuristics, not a trained predictive model.
- HOD dashboards and directories are department-scoped. Student data is restricted to the authenticated student; faculty sees assigned sections.
- Admin manages users, account status, passwords, departments, courses, subjects, topics, sections, enrollment and teaching mappings, and calendar events. After creating a student/faculty account, use Academic mapping to give it its academic scope.
- Academic reports export real values to CSV. Profile and settings show actual backend identity and connection state.
- GenAI explanations, draft questions and suggested grading feedback use server-side provider credentials. Configure LLM_API_KEY, LLM_BASE_URL and LLM_MODEL in backend/.env. Missing credentials produce an error rather than a pretend response.
- Public self-registration and email password-recovery claims from the preview were removed from active behavior. Administrators create accounts and reset passwords; no email service is configured.

## Source and architecture

```text
LearnPathAI/
  start-project.ps1
  frontend-react/
    src/pages/Login.tsx       # Real login with role validation
    src/pages/LivePages.tsx   # Connected workflow screens
    src/context/AppContext.tsx
    src/components/          # ZIP design components
    src/layouts/             # Four ZIP role layouts
    package.json / package-lock.json
    dist/                    # Built React app served by FastAPI
  frontend/                  # Previous frontend, preserved
  backend/
    start-project.ps1        # Wrapper; works from your backend terminal
    app/portal.py            # Scoped snapshot and admin password reset
    app/main.py              # Existing API + /api aliases + React SPA routes
    scripts/create_portal_accounts.py
    .local/portal-logins.txt  # Private generated credentials
    db/                      # Existing project schema and SQL queries
```

Browser → React → authenticated `/api/...` → FastAPI permissions/services → SQLAlchemy/PyMySQL → MySQL `learnpath_ai`. FastAPI serves the React build from `/app/`, including deep-link refreshes. The previous UI is available at `/legacy`.

## Development and rebuild

Normal startup uses the existing build; no separate React server is required. After changing React source:

```powershell
powershell -ExecutionPolicy Bypass -File .\start-project.ps1 -Rebuild
```

Or run `npm run build` in `frontend-react/`. For Vite development run `npm run dev` there while FastAPI is running on 8001, then use http://127.0.0.1:3000/app/. Vite proxies `/api` to FastAPI. On a new computer run `npm ci` before building and follow the backend MySQL/Python setup. Do not copy an active MySQL data directory. Docker source context was updated to build React and package both apps, but Docker execution was not tested.

If backend Python files change, stop the old server with Ctrl+C and restart it. If port 8001 is occupied by an older instance, stop that project's terminal before starting the new version. Another local port can be selected with `-Port 8002`; Vite's development proxy remains configured for 8001 unless you update it.

## Verification

- Production TypeScript check and Vite build passed.
- **10 MySQL integration tests passed**, including the existing workflows and new scoped React portal / API-alias checks. The TestClient transport emits one deprecation warning; assertions pass.
- All four generated accounts authenticated successfully, and each fetched an authorized portal workspace. Student snapshots contain no staff answer bank, password hashes or other students' private histories.
- Browser verified rejection of a wrong admin password, real admin sign-in and database-backed user management.
- Browser signed in with the generated Student account, completed the practice test, received 6 marks with EVALUATED status, and generated a persisted personalized plan.
- The root and backend-folder startup entry points launch the same app. React assets and nested app routes are served through FastAPI.
- Live LLM requests, email recovery, Docker runtime and full college-scale load testing are not verified.

References: https://vite.dev/guide/backend-integration and https://fastapi.tiangolo.com/tutorial/static-files/.

Final browser checks also verified the generated Faculty, HOD and Admin credentials, the student route guard against an admin URL, the faculty question bank and attendance history, and the desktop responsive layout.
