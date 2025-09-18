# ASM Subdomain Discovery (MVP)

Passive-first, safe-by-default subdomain discovery with optional active bruteforce and DNS resolution (opt-in via token). Backend: FastAPI + SQLAlchemy + Alembic, Worker: Redis + RQ, Storage: Postgres (SQLite in dev), Frontend: React (Vite). Modular connectors for CT logs, Chaos, SecurityTrails, Wayback (CommonCrawl placeholder). Includes tests and Docker Compose for local runs.

## Features

- Inputs: `domain`, optional `scope` (include/exclude regex), toggles for `bruteforce` and `resolution` (active features gated by token).
- Passive sources:
  - crt.sh (HTTP JSON, parsing)
  - ProjectDiscovery Chaos (API key optional; mock fallback)
  - SecurityTrails (API key optional; mock fallback)
  - Wayback Machine (CDX API)
  - CommonCrawl placeholder for future expansion
- Optional active bruteforce (local wordlist) and DNS resolution (A/AAAA/CNAME), rate-limited and opt-in.
- Orchestration: Redis + RQ worker; parallel connectors; per-connector timeouts and rate limits.
- Normalization & Deduplication: lower-case, strip wildcards and trailing dots, merge sources.
- Storage schema: assets, asset_sources, scans, scan_jobs, owners.
- API:
  - POST `/api/v1/scan`
  - GET `/api/v1/scan/{scan_id}`
  - GET `/api/v1/assets?domain=example.com&live=true`
  - GET `/api/v1/assets/{id}`
  - GET `/api/v1/assets/export.csv?domain=example.com`
  - GET `/api/v1/assets/graph.json?domain=example.com`
- Frontend: Simple SPA to start a scan, watch status, view results, export CSV.
- Tests: unit for normalizer and resolver (mocked), integration test with fake connector data.
- Bonus: saves raw connector outputs to `backend/app/storage/raw` for auditability.

## Security & Ethics

- Passive discovery by default.
- Active features (bruteforce + resolution) require `ACTIVE_SCAN_TOKEN` and must be explicitly enabled per-scan.
- Logs and rate limits for connectors to avoid abuse.
- Never commit real API keys.

## Quickstart with Docker

Requirements: Docker + Docker Compose

1. Copy `.env.example` to `.env` and customize as needed.
2. Start services:
   ```bash
   docker compose up --build
   ```
3. Apply DB migrations:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
4. Open the UI: http://localhost:5173
5. API docs: http://localhost:8000/docs

## Environment Variables

See `.env.example`. Key vars:
- `DATABASE_URL` (default Postgres in Compose; SQLite for local non-Compose dev)
- `REDIS_URL`
- `ACTIVE_SCAN_TOKEN` (required to enable active `bruteforce`/`resolution`)
- `CHAOS_API_KEY` (optional)
- `SECURITYTRAILS_API_KEY` (optional)
- `WORDLIST_PATH` (path to wordlist for bruteforce)
- Rate limit knobs like `CONNECTOR_TIMEOUT_SECONDS`, `RESOLVER_MAX_CONCURRENCY`

## Example Usage

- Start a passive-only scan:
  ```bash
  curl -s -X POST http://localhost:8000/api/v1/scan \
    -H 'Content-Type: application/json' \
    -d '{"domain":"test.example","bruteforce":false,"resolution":false,"notify":false}'
  ```
  Response:
  ```json
  { "job_id": "rq:...", "scan_id": "..." }
  ```

- Poll status:
  ```bash
  curl -s http://localhost:8000/api/v1/scan/<scan_id> | jq
  ```

- Enable active bruteforce/resolution (requires token):
  ```bash
  curl -s -X POST http://localhost:8000/api/v1/scan \
    -H 'Content-Type: application/json' \
    -d '{"domain":"test.example","bruteforce":true,"resolution":true,"active_token":"'$ACTIVE_SCAN_TOKEN'"}'
  ```

- List assets:
  ```bash
  curl -s "http://localhost:8000/api/v1/assets?domain=test.example&live=false" | jq
  ```

Expected asset sample (acceptance criteria shape):
```json
{
  "subdomain": "sub.test.example",
  "normalized": "sub.test.example",
  "resolved": true,
  "ips": ["1.2.3.4"],
  "sources": ["crtsh","chaos"],
  "first_seen": "2025-09-18T02:00:00Z"
}
```

## Development (Local without Docker)

- Create virtualenv, install deps:
  ```bash
  python -m venv .venv && source .venv/bin/activate
  pip install -r backend/requirements.txt
  export DATABASE_URL=sqlite:///./asm.db
  export REDIS_URL=redis://localhost:6379/0
  alembic -c backend/alembic.ini upgrade head
  uvicorn backend.app.main:app --reload
  rq worker -u $REDIS_URL asm-queue
  ```

## Tests

Run all tests:
```bash
pytest
```

## Design Notes

- Connectors implement a simple async interface with per-connector rate limiting and timeouts.
- Deduplication merges sources and retains proofs per source.
- Resolution is isolated and opt-in to prevent unintentional active scanning.
- Storage uses JSON for portability (Postgres JSONB when available).
- Orchestrator is async inside the worker to execute connectors concurrently.

## Roadmap

- Add CommonCrawl real implementation, Shodan/Censys connectors.
- Add notifications, authn/authz, and multi-tenant owner relationships.
- Add pagination and richer filtering in API/UI.