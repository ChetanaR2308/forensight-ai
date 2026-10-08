# ForenSight AI (Research MVP)

> **Disclaimer (critical):** This project is human-in-the-loop research software, **not** an autonomous forensic decision maker. AI-assisted outputs are never proof of identity, guilt, or innocence.

ForenSight AI is a full-stack MVP for forensic investigation decision support. The implementation is intentionally deterministic-first, explainable, and runnable locally.

## Implemented MVP scope (honest)

- FastAPI backend with JWT auth and RBAC roles: `investigator`, `analyst`, `admin`
- Case CRUD with ownership/collaborator access checks
- Evidence upload with multipart handling, local object-storage-style filesystem writes, SHA-256 streaming hash, metadata, and audit logging
- Evidence integrity verification endpoint that recomputes SHA-256
- Typed models for cases, evidence, observations, events, findings, citations, uncertainty/conflict status, and audit records
- Deterministic processing pipeline:
  - Optional OpenCV metadata extraction when available
  - OCR adapter interface with deterministic fallback
  - Structured observation persistence with provenance
- Deterministic timeline/correlation service
- Investigation query endpoint returning grounded citations and **Insufficient evidence** when unsupported
- Structured report endpoint with findings, conflicts, evidence gaps, uncertainty, and next actions
- Replaceable integration interfaces with in-memory MVP adapters for graph/vector/langgraph orchestration
- React + TypeScript + Vite + Tailwind UI with authentication, protected routes, dashboard, cases, evidence, timeline, assistant view, and report view
- Backend + frontend tests and CI workflow

## Planned (not implemented) research integrations

- Production-grade MongoDB persistence layer
- Optional LLM providers (disabled by default)
- Live vector DB and Neo4j graph query integrations
- Rich relationship graph visual analytics

## Monorepo structure

- `backend/` FastAPI service
  - `app/routers` API modules
  - `app/services` domain logic and adapters
  - `app/models` typed domain/schemas
  - `app/repositories` repository abstraction and local fallback
  - `app/tests` pytest coverage
- `frontend/` React + TypeScript app
  - dashboard, cases, case detail, upload/timeline/assistant/report views
- `.github/workflows/ci.yml` backend/frontend checks
- `docker-compose.yml` local stack (MongoDB required for service container, Neo4j optional profile)

## Local setup

### Prereqs
- Python 3.11+
- Node.js 20+
- Docker (optional but recommended)

### Backend
```bash
cd backend
pip install -e .[test]
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

### Full stack with Docker Compose
```bash
docker compose up --build
```

Neo4j is optional and only started with:
```bash
docker compose --profile optional up neo4j
```

## Demo users (local development only)
Seeded at startup (in-memory/local-safe defaults):
- `admin / admin123`
- `investigator / investigator123`
- `analyst / analyst123`

Change these in `backend/.env` for your local environment.

## Environment variables

### Backend (`backend/.env`)
- `JWT_SECRET` (required outside local demo)
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `MAX_UPLOAD_SIZE_MB`
- `UPLOADS_DIR`
- `CORS_ORIGINS`
- `USE_MONGO` (`false` by default in MVP)
- `MONGO_URI`, `MONGO_DB_NAME`
- `ENABLE_LLM` (`false` by default)

### Frontend (`frontend/.env`)
- `VITE_API_BASE_URL` (default `http://localhost:8000`)

## Security and data-handling assumptions

- Raw evidence files are written to local filesystem object-style storage (`backend/uploads`) and are **not** stored in MongoDB.
- Uploads enforce max file size and safe filename/path handling.
- Evidence SHA-256 is computed while streaming upload and re-verifiable.
- Preserve provenance for every observation/finding: evidence ID, source, timestamp, processing stage, confidence, and uncertainty/conflict status.
- Avoid committing uploads, secrets, model weights, or generated artifacts.

## API overview

- `GET /health`
- `POST /auth/token`
- `GET|POST /cases`
- `GET|PATCH|DELETE /cases/{case_id}`
- `GET|POST /cases/{case_id}/evidence`
- `GET /cases/{case_id}/evidence/{evidence_id}/integrity`
- `GET /cases/{case_id}/evidence/timeline`
- `POST /cases/{case_id}/investigation/query`
- `GET /cases/{case_id}/investigation/report`
- `GET /cases/{case_id}/graph/export`

## Testing

```bash
make backend-test
make frontend-test
make frontend-build
```

## Ethics and reliability policy

- Never invent facts from missing data.
- If evidence is missing, ambiguous, or unsupported, return **Insufficient evidence** or **Inconclusive**.
- Assistant responses must include uncertainty labels and citations where available.
- Human investigators remain responsible for all conclusions.

## Incremental roadmap

1. Replace in-memory repository with full Mongo persistence implementation.
2. Add optional pluggable LLM provider with strict grounded mode.
3. Add Neo4j and vector DB adapters with retry/backoff and observability.
4. Expand ingestion and validation for additional media formats.
5. Add stronger audit export, signed integrity manifests, and role-scoped policy controls.
