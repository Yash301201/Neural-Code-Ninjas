# LearnPath AI backend

FastAPI application backed by MySQL, serving the React portal, academic APIs, research analytics, and optional Groq-assisted learning tools.

Start with the [project README](../README.md) for full installation and the [architecture guide](docs/architecture.md) for folder ownership and data flows.

## Modules

| File | Responsibility |
|---|---|
| `app/main.py` | Application lifecycle, academic endpoints, API aliases, static frontend delivery |
| `app/portal.py` | Scoped portal snapshots and administrative portal operations |
| `app/security.py` | Argon2id password checks, JWTs, role and academic scope enforcement |
| `app/schemas.py` | Request validation models |
| `app/db.py` | SQLAlchemy engine, request sessions and persistence helpers |
| `app/analytics.py` | Academic reports, study priorities and heuristic risk indicators |
| `app/dataset_analytics.py` | Public OULAD cohort queries and research metrics |
| `app/ai.py` | Structured question generation, explanations and feedback suggestions |
| `app/rag.py` | MySQL-backed BM25 retrieval, Groq synthesis, citations and saved history |
| `app/config.py` | Server-side environment configuration |

## Manual startup

From this `backend/` directory, with MySQL running and the React build available:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set `DATABASE_URL` and replace `JWT_SECRET` in `.env`. Preserve an existing configuration when updating. Create the schema explicitly, then create an administrator interactively:

```powershell
.\.venv\Scripts\python.exe -m scripts.init_db --create-database
.\.venv\Scripts\python.exe -m scripts.create_admin
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Omit `--create-database` if the database already exists. The running API does not silently create its schema. Use a dedicated database account; schema setup needs the corresponding DDL permissions.

The existing Windows showcase can instead use `start-project.ps1` from this directory or the repository root. That launcher depends on its preconfigured local MySQL installation and `.local/mysql-data`; it is not a fresh-clone provisioning script.

## Database operations

| Operation | Command from `backend/` |
|---|---|
| Apply schema definitions | `.\.venv\Scripts\python.exe -m scripts.init_db` |
| Load fictional examples once into a fresh schema | `.\.venv\Scripts\python.exe -m scripts.init_db --sample-data` |
| Download public research archive | `.\.venv\Scripts\python.exe -m scripts.download_oulad` |
| Import OULAD and reconcile aggregates | `.\.venv\Scripts\python.exe -m scripts.import_oulad` |
| Apply RAG schema and refresh its public index | `.\.venv\Scripts\python.exe -m scripts.setup_rag` |

`db/001`, `003`, `005`, and `007` define schema. `db/002` is optional sample data. `db/004`, `006`, and `008` are reporting query packs. SQL DDL implicitly commits; back up existing databases before schema updates. These scripts do not provide automatic migration-history tracking.

## Authentication and AI

`POST /auth/login` or `/api/auth/login` accepts email and password and returns an expiring bearer JWT. The API checks active account status, role, and academic scope. MySQL stores Argon2id password hashes; JWTs do not store passwords. Account creation and password reset are administrative workflows.

Groq generation uses `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` from `.env`. Restart the API after changing them. Structured GenAI tasks require a provider key; the RAG assistant can return clearly labeled retrieved evidence without generation. No private academic records are indexed into the public RAG corpus. See [RAG setup](docs/rag-integration.md).

## Validation

Set `TEST_DATABASE_URL` to a disposable MySQL database ending in `_test`, then run:

```powershell
.\.venv\Scripts\python.exe -m pytest tests -q
```

Tests recreate their target schema. Never use the application database. The recorded run passed 16 tests with an existing Starlette/httpx deprecation warning; live Groq generation and Docker runtime remain unverified.

## Container configuration

`Dockerfile` builds React and packages the Python server. `compose.yaml` supplies MySQL 8.4 and the API, bound to localhost port 8000. Configure `MYSQL_PASSWORD`, `MYSQL_ROOT_PASSWORD`, and `JWT_SECRET` in `.env` before running `docker compose up --build -d` from this directory. MySQL initialization scripts run only on a fresh volume; existing volumes need explicit schema updates. Do not remove volumes containing data you need.

## Documentation

- [Architecture](docs/architecture.md)
- [OULAD integration](docs/oulad-integration.md)
- [RAG integration](docs/rag-integration.md)
- [Credential storage](docs/credential-storage.md)
- [Frontend integration notes](docs/react-integration.md)
