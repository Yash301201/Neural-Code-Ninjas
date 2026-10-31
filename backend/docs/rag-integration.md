# LearnPathAI: Groq LLM, RAG and MySQL

The integration is implemented. Live Groq generation requires your own API key; no key was present during verification. Retrieval and MySQL conversation persistence are working now.

## Enable Groq

Create a key at https://console.groq.com/keys and edit the existing backend/.env privately. Preserve DATABASE_URL, JWT_SECRET and every other existing setting. Set these three entries (do not duplicate them):

```dotenv
LLM_API_KEY=your_actual_groq_key
LLM_BASE_URL=https://api.groq.com/openai/v1
LLM_MODEL=llama-3.3-70b-versatile
```

Do not put the provider key in frontend code, MySQL, credential JSON, or chat. The backend reads it at process startup. Stop the running backend with Ctrl+C in its terminal, then run:

```powershell
cd "C:\Users\DELL\OneDrive\Yash\OneDrive\Desktop\LearnPathAI\backend"
powershell -ExecutionPolicy Bypass -File .\start-project.ps1
```

If the launcher says the application is already running, stop that existing backend process first so the new environment settings are loaded. Do not launch a second server on port 8001.

Sign in with your existing account and choose **AI Knowledge Assistant** in the sidebar. Admin URL: http://127.0.0.1:8001/app/admin/rag-assistant. Student, faculty and HOD have corresponding sidebar entries. Provider status should change from “Groq key needed” to “Groq configured.” This checks presence of the key, not validity; send a question to verify the provider itself.

## MySQL changes already applied

The additive migration backend/db/007_rag_assistant.sql creates:

| Table | Persistent data |
|---|---|
| rag_chunks | Source text, title, source URL, cohort, checksum; 905 indexed chunks |
| rag_conversations | Conversation title and owner user_id foreign key |
| rag_messages | Question, answer, source citation snapshots, mode, model, timestamp |

Existing users, passwords and JWT secret were not changed. Questions and answers are normal application data stored as text, not password hashes. Do not enter confidential information into assistant questions.

New installations include this SQL in init_db and Docker initialization. Docker init scripts run only on fresh volumes; existing databases require the setup command. This command was already run against your local database and safely rerun with 0 changed chunks:

```powershell
cd "C:\Users\DELL\OneDrive\Yash\OneDrive\Desktop\LearnPathAI\backend"
.\.venv\Scripts\python.exe -m scripts.setup_rag
```

After importing a new OULAD batch, refresh the knowledge index with this command or the admin **Refresh public knowledge index** button. This rebuilds managed source chunks without deleting conversation history. Previous answers retain their original evidence snapshots and may become outdated.

## How it works

1. An authenticated question reaches FastAPI /api/rag/ask.
2. Relevant chunks are retrieved from MySQL and ranked with BM25 lexical retrieval. This is a real retrieval pipeline; it does not use embeddings or a vector database.
3. Optional cohort filtering limits research evidence to the selected cohort plus general guidance.
4. The backend sends only the question and selected public/curated evidence to Groq's chat-completions endpoint. Account tables, grades, credential files and secrets are never retrieved for model context.
5. Groq is instructed to answer from evidence with [S1] style citations. Citation labels must refer to retrieved sources or the answer is rejected in favor of source excerpts. Labels being valid does not prove every claim is supported, so inspect the sources.
6. The answer and evidence snapshots persist in MySQL under the signed-in owner. Other users, including admins, cannot read that conversation through the API.

Evidence-only mode skips Groq. Missing keys, provider failures and invalid citations show explicitly labeled retrieved excerpts, never a fabricated model answer. Unmatched queries return an insufficient-evidence response. Each question is independent; conversation history is saved for review, not sent as model context.

The 905 chunks cover historical OULAD provenance, per-cohort enrollments/outcomes, per-week clicks/active learners, and curated guidance on study planning, RAG and project authentication. They do not contain private academic records, exam answers, student-level demographics or uploaded arbitrary documents. The original UK research provenance is retained. VLE engagement is not classroom attendance. This assistant does not execute SQL, modify academic records or make student decisions.

## Evaluator demonstration

Select BBB / 2014J and ask: “What happened in BBB 2014J week 0 engagement?” Expand evidence citations, then reopen the saved conversation from the sidebar or reload the page. Use backend/db/008_rag_reporting_queries.sql in MySQL Workbench to inspect persisted records and the index. SQL files are versioned schema/query definitions; MySQL holds the actual live rows.

## Verification

- Frontend TypeScript and Vite production build passed.
- 16 MySQL-backed backend tests passed in an isolated database ending _test; one existing Starlette/httpx deprecation warning.
- Retrieval relevance, invalid citation rejection, missing-key fallback, MySQL history persistence, conversation owner isolation, auth, role restriction on reindex and input validation checked.
- Browser sign-in, sidebar navigation, retrieval answer and saved-history entry verified against the running app.
- Live Groq generation remains unverified until your API key is configured. Mocked provider responses test the integration contract, not the external model.

Official Groq documentation: https://console.groq.com/docs/quickstart and https://console.groq.com/docs/models.
