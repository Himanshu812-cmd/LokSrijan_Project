# LokSrijan — Architecture

> Status: **development foundation**. Routing, shared layout, API client, and a
> verified frontend-to-backend connection exist. No product features are
> implemented yet.

---

## 1. Monorepo architecture

One repository, two applications, run side by side in development.

```
Loksrijan/
├── frontend/            Next.js application (port 3000)
├── backend/             FastAPI application (port 8000)
├── docs/                architecture, API contract, team workflow
├── docker-compose.yml   local PostgreSQL (port 5432)
├── .gitignore
├── .env.example         reference for every environment variable
└── README.md
```

**Why a monorepo:** six developers, one clone, one issue tracker, and a single
place where the API contract is agreed. Frontend and backend are deployed
separately later; nothing here prevents that.

The two applications communicate **only over HTTP/JSON**. There is no shared
code between them. The contract is documented in
[api-contract.md](./api-contract.md) and mirrored in TypeScript types under
`frontend/types/`.

```
Browser
  │  fetch (JSON)
  ▼
Next.js (localhost:3000)          FastAPI (localhost:8000)
  └── lib/api.ts ───────────────────► /health, /api/*
                                        │  SQLAlchemy
                                        ▼
                                     PostgreSQL (localhost:5432)
```

Note that the health call is made **from the browser**, not from the Next.js
server. That is why CORS is configured on the backend.

---

## 2. Frontend architecture

**Stack:** Next.js 16.3.3 (App Router), React 19.2, TypeScript 5 (strict),
Tailwind CSS v4, shadcn/ui.

```
frontend/
├── app/                    routes (App Router)
│   ├── layout.tsx          root layout — fonts, metadata, SiteHeader
│   ├── page.tsx            landing placeholder
│   ├── citizen/            mobile-first citizen interface
│   ├── government/         desktop-first dashboard
│   ├── university/
│   ├── ngo/
│   ├── industry/
│   └── dev/                temporary connectivity check
├── components/
│   ├── ui/                 shadcn/ui primitives (generated — do not hand-edit)
│   ├── shared/             cross-app components (SiteHeader, PageShell)
│   └── dashboard/          reusable dashboard building blocks
├── lib/
│   ├── api.ts              the only place that calls fetch
│   ├── navigation.ts       canonical role routes
│   └── utils.ts            cn() class merge helper (shadcn)
├── types/                  API response types mirroring backend schemas
└── public/
```

### Conventions

- **Every route renders exactly one `PageShell`.** It owns page width, spacing,
  and the single `h1`, so heading order stays valid for screen readers.
- **All network calls go through `lib/api.ts`.** No component calls `fetch`
  directly. This keeps the base URL, headers, and error handling in one place.
- **`ApiError`** carries `status` and `url`; `status === 0` means the API was
  unreachable rather than a failed request.
- **Server Components by default.** Add `"use client"` only when a component
  needs state, effects, or event handlers.
- **Design tokens come from shadcn/ui** (`bg-background`, `text-foreground`,
  `text-muted-foreground`, `border-border`). Do not introduce a parallel colour
  palette. Base colour is `neutral`; a LokSrijan brand accent is added later.
- Responsive: mobile-first for citizen-facing pages, desktop-first for
  dashboards. Avoid heavy gradients and animation.

### One Next.js 16 detail worth knowing

**Typecheck needs generated types.** `LayoutProps` / `PageProps` are generated
into `.next/types` by `next dev`, `next build`, or `next typegen`. A bare
`tsc --noEmit` fails with *"Cannot find name 'LayoutProps'"*. Always use
`npm run typecheck`, which runs `next typegen && tsc --noEmit`.

Also note `next lint` was removed in Next 16 — use `npm run lint` (plain
ESLint), and `next build` no longer lints for you.

---

## 3. Backend architecture

**Stack:** FastAPI 0.141, Python 3.11, SQLAlchemy 2.0 (synchronous),
psycopg 3, Pydantic 2 / pydantic-settings.

A **modular monolith**: one deployable application, internally organised by
feature. Not microservices.

```
backend/
├── app/
│   ├── main.py             app creation, CORS, router mounting
│   ├── core/
│   │   ├── config.py       env-driven settings (pydantic-settings)
│   │   └── database.py     engine, SessionLocal, Base, get_db
│   ├── api/
│   │   ├── health.py       GET /health, GET /health/db
│   │   └── router.py       aggregator for everything under /api
│   ├── models/             SQLAlchemy ORM models — one file per entity
│   ├── schemas/            Pydantic request/response models
│   ├── services/           business logic — one file per concern
│   └── modules/            feature routers — all empty placeholders
│       ├── auth/  users/  challenges/  ai/
│       └── matching/  projects/  impact/  analytics/
├── requirements.txt        pinned dependencies
└── .env.example
```

### Layer layout

The backend is organised in **layers**, not as self-contained vertical slices.
There is exactly one place for each kind of code:

| Layer | Contains | Example |
| --- | --- | --- |
| `models/` | SQLAlchemy ORM models, one file per entity | `models/challenge.py` |
| `schemas/` | Pydantic request/response models | `schemas/challenge.py` |
| `services/` | business logic | `services/matching_service.py` |
| `modules/<name>/routes.py` | FastAPI router for that feature | `modules/challenges/routes.py` |
| `api/router.py` | registers every module router under `/api` | one line per module |

**Why models are central rather than per-module:** the core entities reference
each other heavily — a Challenge has a Location, an Organization, Evidence, and
belongs to a ChallengeCluster. Splitting them across feature modules produces
circular imports immediately, and Alembic autogenerate needs a single import
point to see the whole schema.

This split also maps cleanly onto parallel work: one developer can own
`models/`, another `modules/challenges/routes.py`, another
`services/ai_service.py`, and another `services/matching_service.py`, with
almost no overlapping files.

Rules that keep the monolith from rotting:

- Routers contain no business logic — they validate input and call a service.
- A service receives its database session as an argument; it never opens its own.
- Cross-feature access goes through the other feature's **service**, never
  directly into its tables.
- Health endpoints live at the application root (`/health`), not under `/api`,
  so infrastructure probes survive API versioning.

`app/modules/organizations/` (universities, NGOs, industry partners) and
`app/modules/notifications/` are **not created yet** — they are added when
first needed, to keep the current tree honest about what exists.

---

## 4. Database direction

PostgreSQL 16, running in Docker for local development
(`docker-compose.yml`). SQLAlchemy is used synchronously — simpler to reason
about for a small team and fast enough for this MVP.

**Current state: connection configuration only.** There are no tables, no ORM
models, and no migration tool yet.

Next step (a separate task) is the core schema, roughly:

```
users, roles
challenges                a validated, structured problem
challenge_evidence        photos and attachments
challenge_locations       district / block / village / coordinates
challenge_categories
challenge_clusters        many reports grouped into one challenge
validations               who approved what, and when
ai_assessments            model output + reasoning, kept auditable
```

Principles:

- Every table has `id`, `created_at`, `updated_at`.
- Foreign keys are explicit; enums are used for fixed vocabularies.
- **AI output is stored alongside its reasoning**, never as a bare score.
- **Human decisions are recorded separately from AI suggestions**, so it is
  always clear who decided what.
- Demo data is flagged in the database, never mixed silently with real data.

Deliberately deferred, with reasons:

| Deferred | Why | Added when |
| --- | --- | --- |
| **Alembic** | nothing to migrate until models exist | with the first ORM models |
| **PostGIS** | plain lat/lon columns cover the demo | real geospatial queries are needed |
| **pgvector** | clustering can start with simpler similarity | embedding search is proven necessary |
| **Redis** | no background jobs yet | AI calls need queueing |

`engine` is created with `connect_args={"connect_timeout": 3}` so the API fails
fast instead of hanging when PostgreSQL is down, and with `pool_pre_ping=True`
to recycle dropped connections.

---

## 5. AI integration direction

**Nothing is implemented.** No provider is configured, no API key is required,
and no AI library is installed. `AI_PROVIDER` and `AI_API_KEY` exist in the env
templates as reserved names only.

The plan is a single provider-agnostic interface in `app/modules/ai/`:

```python
class AIService(Protocol):
    def extract_problem(self, raw_text: str) -> ProblemExtraction: ...
    def classify_problem(self, problem: ProblemExtraction) -> Classification: ...
    def find_duplicates(self, problem: ProblemExtraction) -> list[DuplicateMatch]: ...
    def generate_summary(self, challenge_id: int) -> str: ...
```

- The provider is selected by configuration, never hardcoded.
- A `MockAIService` returning fixed, clearly-labelled output lets the whole
  pipeline and the demo run with no API key and no cost.
- Abstract at the level above — one interface, swappable implementations. Do not
  build a plugin framework.

Non-negotiable:

- **AI recommendations must be explainable.** Every score ships with the reasons
  behind it. A number with no explanation is not acceptable output.
- **AI suggests; humans validate.** No AI output changes an important record
  without a person approving it.

---

## 6. Current MVP scope

Implemented:

- Monorepo under git, with secrets and build artefacts ignored
- Next.js frontend that builds, typechecks, and lints clean
- FastAPI backend with `GET /health` and `GET /health/db`
- Environment-driven configuration on both sides, no hardcoded values
- CORS allowing the Next.js dev server
- PostgreSQL compose file (validated; requires Docker Desktop running)
- Verified browser → frontend → backend connectivity

Not implemented — in rough priority order:

1. Citizen problem submission
2. AI problem structuring
3. Duplicate detection
4. Challenge clustering
5. Human validation
6. University matching
7. NGO matching
8. Project lifecycle
9. Impact tracking
10. Government analytics dashboard

Authentication is deliberately deferred; it is not on the critical path to
proving the core loop.

