# University Voice Agent Platform

A multi-tenant university voice-agent platform, built by mirroring the existing
Restaurant Voice Agent architecture. Students call a university's phone number and
ask about admissions, courses, subjects, fees, scholarships, eligibility, deadlines,
and general university information. The agent answers using only that university's
configured data.

It is the university analog of the restaurant platform:

| Restaurant            | University                          |
|-----------------------|-------------------------------------|
| `restaurants.phone`   | `universities.phone` (tenant key)   |
| `menu_items`          | `courses` → `subjects` (hierarchy)  |
| food / table agents   | admissions / course / FAQ agents    |
| `agent_configs`       | `agent_configs` (same shape)        |
| `call_sessions/_messages` | identical call tracking         |

## Layout

```
Universities_agent/
├── backend/
│   ├── api/         FastAPI control plane (CRUD + call tracking)
│   └── my-agent/    LiveKit voice agent (runtime, reads the DB directly)
└── docker-compose.yml
```

## Database (separate from the restaurant DB)

The platform uses its **own** database, `Universities_Voice_Agent`, on the same
Postgres server. It never touches the restaurant database.

1. Create the empty database once:
   ```bash
   docker compose -f Resturant_agent/docker-compose.yml exec postgres \
     psql -U postgres -c "CREATE DATABASE \"Universities_Voice_Agent\";"
   ```
2. Build the schema. Either:
   - **Alembic (recommended, version-controlled, idempotent):**
     ```bash
     cd Universities_agent/backend/api
     cp .env.example .env        # fill in secrets
     alembic upgrade head
     ```
     The API Dockerfile runs `alembic upgrade head` on every boot, so this is automatic in Docker.
   - **or** the one-shot SQL script at the repo root: `university_schema.sql`.

## Backend API

```bash
cd Universities_agent/backend/api
pip install -r requirements.txt
cp .env.example .env            # set DATABASE_URL, secrets, AGENT_INTERNAL_API_KEY
alembic upgrade head
uvicorn app.main:app --reload   # http://localhost:8000/docs (DEBUG=true)
```

### Modules (each: models / schemas / services / routes)
- `auth` — JWT register/login/refresh; self-contained users.
- `roles` — RBAC (admin/owner/manager/operator), operator hard-lock, permission matrix.
- `university` — University profile CRUD + 1:1 `AgentConfig` + `/prompt` generator.
- `admin/universities` — platform-admin cross-tenant University CRUD (onboarding).
- `courses`, `subjects` — course catalog and its subjects/modules.
- `admissions` — 1:1 admission rules (criteria, eligibility, deadlines, documents).
- `scholarships`, `faqs` — supporting data and structured FAQ store.
- `calls` — agent-internal call tracking + JWT call history + WebSocket stream.

Tenancy: every domain row carries `university_id`; every owner-scoped query is
filtered by `current_user.university_id`. Platform admins (role=admin) cross tenants.

## Voice Agent

```bash
cd Universities_agent/backend/my-agent
cp .env.local.example .env.local   # DATABASE_URL (same uni DB), LiveKit, OpenAI, AGENT_INTERNAL_API_KEY
uv sync
uv run python src/agents/main_agent.py dev
```

Call lifecycle:
```
SIP call → LiveKit dispatch (metadata.to_number)
  → _extract_called_number → get_university_context(phone)
     SELECT universities WHERE phone = ?  → university_id
     load courses, agent_config, admission_info (compact summary)
  → AgentSession (OpenAI Realtime + Cartesia TTS + server VAD)
  → Main Router + Admissions / Course / FAQ sub-agents (session.update_agent handoff)
  → retrieval tools query the DB scoped to university_id (info_tools.py)
  → call_tracker posts start/message/end to the API
```

Retrieval is **hybrid-ready**: structured DB tools today (courses, subjects,
admissions, scholarships, FAQs); a pgvector knowledge base is the planned Phase 4
addition for long-form content (see `UNIVERSITY_AGENT_PLAN.md`).

## Frontend (`frontend/`)

TanStack Start (Vite) + React + Tailwind + shadcn/Radix + React Query — the same
stack and shared UI kit as the restaurant frontend. Two role-gated portals.

```bash
cd Universities_agent/frontend
npm install
# .env.local already set: VITE_API_URL=http://localhost:8000
npm run dev      # http://localhost:3000   (npm run build also works — verified)
```

- **Admin portal** (`/admin/*`, role=admin): dashboard, universities table CRUD,
  and a 3-step onboarding stepper (university details → owner account → go live).
- **University portal** (`/app/*`, owner/manager/operator): dashboard, courses,
  subjects, admissions, scholarships, FAQs, voice-agent config, users & roles, settings.
- API layer in `src/lib/api/*` mirrors the backend; auth/role/permission gating via
  `usePermissions` and the `beforeLoad` route guards. Operators are read-only.

Reused verbatim from the restaurant frontend: all `components/ui/*` primitives,
`components/shared/*`, `api-client.ts`, and the Vite/Tailwind config.

## Onboarding flow
1. Platform admin creates a university: `POST /api/v1/admin/universities` (sets name + unique phone).
2. Owner registers against the university name: `POST /api/v1/auth/register`.
3. Owner fills profile, courses, subjects, admissions, scholarships, FAQs, and agent config.
4. A student calls the university's number → routed to that university's agent.
```
