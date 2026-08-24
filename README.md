# Koreum OS — Enterprise Agentic AI Operating Platform

**Phase 1: Foundation** — a fully runnable scaffold with FastAPI backend, React frontend, PostgreSQL + pgvector, Redis, JWT auth, RBAC, multi-tenancy, and audit logging.

## Quick start

### Prerequisites
- Docker + Docker Compose
- Python 3.12+
- Node 20+

### 1. Environment

```bash
cp .env.example .env
# edit .env — set JWT_SECRET and GEMINI_API_KEY (Gemini is used in Phase 2)
```

### 2. Run with Docker Compose (everything)

```bash
docker compose -f infrastructure/docker-compose.yml up --build
```

- Backend: http://localhost:8000/docs (OpenAPI)
- Frontend: http://localhost:5173

### 3. Or run locally (recommended for development)

**Start data services:**
```bash
docker compose -f infrastructure/docker-compose.yml up -d postgres redis
```

**Backend:**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env   # or symlink
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

### 4. Login

Open http://localhost:5173 and sign in with the seeded admin:

- **Email:** `admin@koreum.local`
- **Password:** `Admin123!`

## Project structure

```
koreum-os/
├── backend/          FastAPI modular monolith (app/, alembic/, tests/)
├── frontend/         Vite + React + TypeScript + Tailwind
├── infrastructure/   docker-compose.yml
├── docs/             Koreum_OS_Phase1_Plan.md
├── scripts/          dev.sh helper
├── .env.example
└── README.md
```

## Architecture

Three pillars (spec §3):
- **Koreum Vault** — Knowledge Intelligence (Phase 2)
- **Koreum Fabric** — Multi-Agent Orchestration (Phase 4)
- **Koreum Guard** — Security, Governance, Compliance (Phase 6)

Phase 1 delivers the foundation all pillars share: auth, users, tenants, RBAC, audit, and a dashboard.

See `docs/Koreum_OS_Phase1_Plan.md` for the full architecture overview, Mermaid diagrams, DB entity model, and phase roadmap.

## Testing

```bash
cd backend
pytest -v
```

## API documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Tech stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12, FastAPI, Pydantic v2, SQLAlchemy 2 (async), Alembic |
| Database | PostgreSQL 16 + pgvector |
| Cache | Redis 7 |
| Frontend | Vite, React 18, TypeScript, Tailwind CSS |
| Auth | JWT (access + refresh), bcrypt |
| LLM (Phase 2) | Gemini (default), via `LLMProvider` abstraction |

## Roadmap

- ✅ Phase 1 — Foundation (this release)
- ⬜ Phase 2 — Koreum Vault (document ingestion, RAG, vector search)
- ⬜ Phase 3 — Knowledge Graph
- ⬜ Phase 4 — Koreum Fabric (agents, tools, orchestration)
- ⬜ Phase 5 — Workflow Engine
- ⬜ Phase 6 — Koreum Guard (policy, AI governance)
- ⬜ Phase 7 — Enterprise Integrations
- ⬜ Phase 8 — Production Hardening

## License

Proprietary — All rights reserved.
