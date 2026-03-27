# Aigentics Backend

Multi-tenant FastAPI backend scaffold for an enterprise AI workforce SaaS platform. The product model is "hire, train, supervise, and manage digital workers", not a workflow canvas.

## Stack

- Python 3.12
- FastAPI
- Pydantic v2
- PydanticAI
- SQLAlchemy 2
- Alembic
- MySQL
- Redis
- Qdrant
- Socket.IO
- S3-compatible object storage

## Project Structure

```text
app/
  api/            REST routes and request dependencies
  agents/         PydanticAI runtime scaffolding and structured outputs
  approvals/      Policy engine and approval helpers
  audit/          Audit package hooks and audit service
  core/           Settings, enums, security
  db/             Engine, session, base metadata
  integrations/   MCP and OpenAPI normalization scaffolding
  jobs/           Redis-backed worker and scheduler primitives
  knowledge/      Storage, embedding, ingestion, retrieval, Qdrant
  models/         SQLAlchemy multi-tenant domain models
  realtime/       Socket.IO setup and publisher
  schemas/        Pydantic request/response models
  services/       Tenant-safe service layer
  tools/          Internal tool registry
scripts/
  seed_defaults.py
tests/
alembic/
```

## Architecture Notes

- Tenant isolation is enforced through `tenant_id` on workspace-scoped models and `X-Workspace-ID` membership resolution in the API dependency layer.
- Agents are split into global templates and tenant-hired instances.
- Knowledge ingestion is explicit: source metadata, documents, chunks, embeddings, and vector upserts are separated into dedicated services.
- Integrations and tools are normalized into internal definitions so agents never improvise raw external API calls.
- High-risk or sensitive actions pass through the policy engine and approval workflow.
- Realtime updates are delivered via Socket.IO rooms for workspaces and conversations.
- Redis coordinates background jobs using small, explicit queue envelopes instead of a monolithic task framework.

## Current Scaffold Coverage

- Auth with JWT access and refresh tokens
- Multi-tenant users and memberships
- Agent catalog and tenant agents
- Knowledge source records
- Integration templates and tenant integrations
- Tool definition and permission models
- Conversations and messages
- Approval queue
- Dashboard analytics summary
- Notifications and manager insights
- PydanticAI runtime scaffolding for workforce agents and the Agent Manager
- OpenAPI importer scaffold for custom tool generation
- Redis worker and scheduler scaffold
- Socket.IO ASGI integration

## External Adapters

These boundaries are present but still require vendor wiring:

- `app/knowledge/embeddings.py`
  Gemini embedding provider adapter is intentionally isolated because Google SDK details change over time.
- Native integration execution adapters
  Tool execution boundaries are modeled, but provider-specific Gmail/Slack/CRM implementations are not filled in yet.
- Browser automation fallback
  The integration type exists, but no browser executor is implemented in this scaffold.

## Local Setup

1. Create and activate a Python 3.12 virtual environment.
2. Install dependencies:

```bash
pip install -e .[dev]
```

3. Copy environment variables:

```bash
cp .env.example .env
```

4. Start infrastructure locally, either with your own services or Docker Compose:

```bash
docker compose up -d mysql redis qdrant minio
```

5. Run migrations:

```bash
alembic upgrade head
```

6. Seed the default catalog:

```bash
python scripts/seed_defaults.py
```

7. Start the API:

```bash
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```

## Recommended Next Build Steps

1. Replace the Gemini embedding adapter scaffold with the exact Google GenAI SDK implementation you want to standardize on.
2. Add provider-specific tool executors for Gmail, Slack, CRM, ATS, calendar, and WhatsApp.
3. Expand the conversation engine with agent-run orchestration, streaming tokens, and human handoff state transitions.
4. Add invitation email delivery, password reset, and OAuth flows.
5. Replace the broad initial Alembic migration scaffold with explicit hand-authored follow-up revisions as the schema stabilizes.
