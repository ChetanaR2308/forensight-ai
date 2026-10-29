# ForenSight AI

A secure, human-assisted digital-forensics research prototype for investigating cases with CCTV, images, PDFs, witness statements, and other evidence sources.

> Critical: This tool is decision-support software only. AI output is never proof of identity, guilt, or innocence. Human investigators remain responsible for all conclusions.

## Project goal

ForenSight AI helps investigators:
- upload CCTV footage, images, documents, and witness statements
- preserve evidence integrity with SHA-256 hashing
- extract metadata, events, timestamps, entities, and observations
- correlate evidence across sources and time
- identify conflicts, uncertainty, and evidence gaps
- answer case-specific investigation questions with source citations
- generate explainable investigation reports

## Branch and working target

This repository branch is:
- `spoorthi/complete-forensight-platform`

Do not modify or merge `main`.

## What is implemented in this branch

The project includes a working MVP structure:
- FastAPI backend with auth, case management, evidence upload, and investigation endpoints
- JWT auth and demo role-based access for investigator, analyst, and admin roles
- local filesystem storage with secure path handling and SHA-256 verification
- deterministic evidence processing with metadata extraction and text parsing
- timeline generation from observations and human-readable report generation
- React + Vite + TypeScript UI for login, dashboard, and case workflows
- backend tests for auth, case access, and evidence upload validation

## Important limitations

This is a research prototype, not a production forensic system:
- MongoDB, Neo4j, embeddings, and LLM integrations are optional, not required for the default local demo.
- OpenCV and OCR are used when installed; the project remains deterministic and transparent when absent.
- No external service is treated as a proof source.
- Synthetic demo evidence is used for development and testing.

## Local setup (Windows)

### 1) Clone and switch branch

```powershell
git clone https://github.com/ChetanaR2308/forensight-ai.git
cd forensight-ai
git checkout spoorthi/complete-forensight-platform
```

### 2) Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -e .[test]
Copy-Item .env.example .env
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3) Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev -- --host 0.0.0.0 --port 5173
```

### 4) Optional Docker stack

```powershell
docker compose up --build
```

## Environment variables

### Backend (`backend/.env`)

```dotenv
ENVIRONMENT=development
JWT_SECRET=change-me-local-dev-only
ACCESS_TOKEN_EXPIRE_MINUTES=60
MAX_UPLOAD_SIZE_MB=25
UPLOADS_DIR=backend/uploads
CORS_ORIGINS=http://localhost:5173
USE_MONGO=false
MONGO_URI=mongodb://mongodb:27017
MONGO_DB_NAME=forensight
ENABLE_LLM=false
DEMO_ADMIN_PASSWORD=admin123
DEMO_INVESTIGATOR_PASSWORD=investigator123
DEMO_ANALYST_PASSWORD=analyst123
NEO4J_URI=
NEO4J_USER=neo4j
NEO4J_PASSWORD=neo4j123
VECTOR_BACKEND=memory
LLM_PROVIDER=demo
LLM_MODEL=demo-grounded-model
LLM_API_KEY=
```

### Frontend (`frontend/.env`)

```dotenv
VITE_API_BASE_URL=http://localhost:8000
```

## Demo users

Local demo users are seeded automatically at startup:
- `admin / admin123`
- `investigator / investigator123`
- `analyst / analyst123`

## API overview

- `GET /health`
- `POST /auth/token`
- `GET /cases`
- `POST /cases`
- `GET /cases/{case_id}`
- `PATCH /cases/{case_id}`
- `DELETE /cases/{case_id}`
- `GET /cases/{case_id}/evidence`
- `POST /cases/{case_id}/evidence`
- `GET /cases/{case_id}/evidence/{evidence_id}`
- `GET /cases/{case_id}/evidence/{evidence_id}/download`
- `GET /cases/{case_id}/evidence/{evidence_id}/integrity`
- `GET /cases/{case_id}/evidence/timeline`
- `POST /cases/{case_id}/investigation/query`
- `GET /cases/{case_id}/investigation/report`
- `GET /cases/{case_id}/graph/export`

## Test and validation commands

```powershell
cd backend
pytest

cd ../frontend
npm test
npm run build
```

## Recommended workflow

1. Start the backend.
2. Start the frontend.
3. Sign in using a demo user.
4. Create a synthetic case.
5. Upload text, image, or document evidence.
6. Check the timeline and investigation query response.
7. Review the report and evidence gaps.
8. Treat all AI output as evidence-backed decision support only.

## Security and evidence handling

- Raw evidence files are stored locally under `backend/uploads`.
- Each file is hashed with SHA-256 during upload.
- Integrity verification recomputes the hash and compares it with the recorded value.
- Source evidence and uncertainty are preserved in every structured observation.
- The platform never declares guilt or invents evidence.

## Completion status

This repository branch is a working research prototype rather than a production forensic platform.

Implemented features in the codebase:
- secure demo auth and role-based access
- case creation and access control
- file upload and SHA-256 integrity checks
- deterministic extraction of metadata and evidence observations
- timeline generation and structured report creation
- UI screens for login, dashboard, and case workflows

Optional or external dependencies that remain non-default:
- MongoDB for persistent production storage
- Neo4j graph database for graph-native persistence
- vector database / embeddings for advanced semantic retrieval
- open OCR and media-analysis model pipelines
- LLM providers for optional grounded generative assistance

These services are intentionally left optional and clearly documented where they are not yet active in the demo.
