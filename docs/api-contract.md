# LokSrijan — API Contract

> **Only two endpoints exist today**: `GET /health` and `GET /health/db`.
> Everything under "Reserved endpoint groups" is a **plan, not an
> implementation**. Nothing there responds yet.

Live, always-accurate reference while the backend is running:
**http://localhost:8000/docs** (generated from the code by FastAPI).
When this document and `/docs` disagree, `/docs` is right — fix this file.

---

## 1. Conventions

| Topic | Rule |
| --- | --- |
| Base URL (dev) | `http://localhost:8000` |
| Feature prefix | `/api` — e.g. `/api/challenges` |
| Health prefix | none — `/health` sits at the root so probes survive versioning |
| Format | JSON request and response bodies; UTF-8 |
| Naming | `snake_case` for JSON fields, plural nouns for collections |
| Paths | lowercase, hyphen-free, plural: `/api/challenges/{challenge_id}` |
| Verbs | `GET` read · `POST` create · `PATCH` partial update · `DELETE` remove |
| IDs | server-generated; never supplied by the client on create |
| Timestamps | ISO 8601 UTC, e.g. `2026-08-27T09:15:00Z` |
| Auth | none yet — deliberately deferred |

### Status codes

| Code | Used for |
| --- | --- |
| 200 | successful read or update |
| 201 | resource created |
| 204 | successful delete, no body |
| 400 | malformed request |
| 404 | resource does not exist |
| 409 | conflict, e.g. duplicate submission |
| 422 | validation failed (FastAPI's default shape) |
| 500 | unhandled server error |

### Errors

FastAPI's default shape is used as-is. Do not invent a second error format.

```json
{ "detail": "Challenge 42 not found" }
```

Validation errors (422) return `detail` as an array describing each failure.

### Collections

List endpoints paginate with `?limit=` and `?offset=` and return the total, so
clients can render "showing 20 of 137" without a second request.

```json
{ "items": [], "total": 0, "limit": 20, "offset": 0 }
```

### Explainability requirement

Any endpoint returning an AI-derived score **must** return the reasons for it in
the same response. A bare number is not an acceptable API response.

```json
{
  "score": 0.82,
  "reasons": [
    "Department lists water quality among its focus areas",
    "Located in the same district as the challenge",
    "Has completed 2 similar projects"
  ]
}
```

Likewise, responses that mix AI suggestions with human decisions must keep them
in separate fields, so a client can always tell which is which.

---

## 2. Implemented endpoints

### `GET /health`

API liveness. Does not touch the database, so it stays fast and stays up even
when PostgreSQL is down.

**Response `200`**

```json
{
  "status": "healthy",
  "service": "loksrijan-api"
}
```

### `GET /health/db`

PostgreSQL reachability.

**Always returns `200`** — inspect the `connected` field. This is intentional:
the development status page renders the result instead of handling an error, and
a stopped database is an expected local state rather than a server fault.

**Response `200` — database up**

```json
{
  "connected": true,
  "detail": "PostgreSQL reachable"
}
```

**Response `200` — database down**

```json
{
  "connected": false,
  "detail": "OperationalError: database not reachable"
}
```

The connection attempt is capped at roughly 3 seconds per address so this
endpoint cannot hang.

### `GET /`

Convenience pointer to the docs. Not part of the product API.

```json
{
  "service": "loksrijan-api",
  "environment": "development",
  "docs": "/docs",
  "health": "/health"
}
```

---

## 3. Reserved endpoint groups — NOT IMPLEMENTED

These names are reserved so the team can agree on shape early and so no two
developers invent different paths for the same thing. **None of these respond
today.** Calling any of them returns `404`.

Each is owned by the backend developer responsible for that module. The owner
updates this section **in the same pull request** that implements the endpoint —
see [team-workflow.md](./team-workflow.md).

### `/api/challenges`

Citizen reports, structured problems, clusters, and validation.

| Planned | Purpose |
| --- | --- |
| `POST /api/challenges` | submit a citizen problem report |
| `GET /api/challenges` | list / filter challenges |
| `GET /api/challenges/{id}` | one challenge with evidence and location |
| `GET /api/challenges/{id}/duplicates` | possible duplicate reports, with reasons |
| `POST /api/challenges/{id}/validate` | record a human validation decision |
| `GET /api/clusters` | grouped reports forming a single challenge |

### `/api/matching`

Explainable recommendations between challenges and organisations. Every
response carries its reasons.

| Planned | Purpose |
| --- | --- |
| `GET /api/matching/challenges/{id}/universities` | recommended departments |
| `GET /api/matching/challenges/{id}/ngos` | recommended NGOs |
| `GET /api/matching/challenges/{id}/industry` | recommended industry partners |

### `/api/projects`

Project lifecycle from adoption through pilot.

| Planned | Purpose |
| --- | --- |
| `POST /api/projects` | adopt a challenge as a project |
| `GET /api/projects` | list projects |
| `GET /api/projects/{id}` | project detail and current stage |
| `PATCH /api/projects/{id}` | advance stage, update status |

### `/api/impact`

Baseline, target, actual, and verification.

| Planned | Purpose |
| --- | --- |
| `POST /api/impact/{project_id}/baseline` | record the starting measurement |
| `POST /api/impact/{project_id}/measurements` | record an actual measurement |
| `GET /api/impact/{project_id}` | impact record with verification status |

### `/api/dashboard`

Role-scoped aggregates for dashboards. Read-only.

| Planned | Purpose |
| --- | --- |
| `GET /api/dashboard/government` | validation queue, district rollups |
| `GET /api/dashboard/university` | recommended challenges, active projects |
| `GET /api/dashboard/ngo` | field partnership view |
| `GET /api/dashboard/industry` | sponsorship opportunities |

### Also reserved

`/api/auth` and `/api/users` — authentication and role management, deferred.

---

## 4. Keeping frontend and backend in sync

1. The **backend is the source of truth**. `http://localhost:8000/docs` is
   generated from the code and cannot drift.
2. TypeScript types in `frontend/types/` mirror the Pydantic schemas in
   `backend/app/`. When a schema changes, update the matching type in the
   **same pull request**.
3. Announce any breaking change to a shared endpoint in the team channel before
   merging. A renamed field breaks the other half of the team silently.
4. Frontend developers who need an endpoint that does not exist yet should agree
   its shape here first, then build against a local stub. Do not guess a shape
   and discover the mismatch during integration.
