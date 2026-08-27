# LokSrijan — Team Workflow

Six developers, one repository. The goal of this document is simple: **nobody
should ever be blocked by, or silently overwrite, someone else's work.**

---

## 1. Branches

```
main                    always working — never commit directly
├── frontend/<thing>    frontend work
├── backend/<thing>     backend work
└── feature/<thing>     anything spanning both
```

Use short, descriptive names: `frontend/citizen-form`,
`backend/challenge-model`, `feature/duplicate-detection`.

**`main` must always start and build.** If you break `main`, fixing it is your
immediate priority.

### Create a branch

```bash
git checkout main
git pull origin main
git checkout -b backend/challenge-model
```

Always branch from a freshly pulled `main`. Branching from a stale `main`
creates merge conflicts that were entirely avoidable.

### Get the latest changes into your branch

```bash
git checkout main
git pull origin main
git checkout backend/challenge-model
git merge main
```

Do this **at least once a day**. A branch that has not seen `main` for three
days is a merge conflict waiting to happen.

We use `merge`, not `rebase`. Rebasing shared branches during a hackathon costs
more time than the tidy history is worth.

### Commit

Small, working commits with a clear subject line:

```bash
git add backend/app/modules/challenges/models.py
git commit -m "feat(challenges): add Challenge and ChallengeEvidence models"
```

Prefixes: `feat`, `fix`, `refactor`, `docs`, `chore`, `test`.

**Never use `git add .` from the repository root.** It is how unrelated files
and stray local edits end up in someone else's review. Stage the files you
actually changed.

### Open a pull request

```bash
git push -u origin backend/challenge-model
```

Then open a PR into `main`. Keep PRs small enough that a teammate can review
them in ten minutes. One reviewer is enough. State clearly in the description
whether the change affects the API contract.

---

## 2. File ownership — how we avoid editing the same files

Each area has a primary owner. **If you need to change a file outside your area,
say so in the team channel first.** This is the single most effective way to
avoid conflicts.

| Dev | Role | Primary area |
| --- | --- | --- |
| **F1** | Citizen experience | `frontend/app/` (landing + citizen flow), `frontend/components/shared/` |
| **F2** | Dashboard frontend | `frontend/app/{government,university,ngo,industry}/`, `frontend/components/dashboard/` |
| **B1** | Database + core models | `backend/app/models/`, migrations |
| **B2** | Challenge APIs | `backend/app/modules/challenges/`, `backend/app/schemas/challenge.py` |
| **B3** | AI problem intelligence | `backend/app/services/ai_service.py` |
| **B4** | Matching engine | `backend/app/services/matching_service.py` |

The backend split is by **layer**, not by feature, precisely so that four
developers can work at once without touching the same files. B1 owns the tables,
B2 owns the HTTP surface, B3 and B4 own one service file each. See
[architecture.md](./architecture.md#layer-layout).

B1 is on the critical path: B2, B3, and B4 all need the `Challenge` model to
exist. B1 should push the core models early and incomplete rather than late and
polished.

### Shared files — coordinate before editing

These are the files most likely to cause a painful conflict. Announce your
change first, keep it minimal, and merge it quickly.

| File | Why it is contended |
| --- | --- |
| `backend/app/api/router.py` | every module registers its router here |
| `backend/requirements.txt` | any new dependency |
| `frontend/package.json` | any new dependency |
| `frontend/lib/api.ts` | every new endpoint adds a method |
| `frontend/types/api.ts` | shared response types |
| `frontend/app/layout.tsx` | global layout |
| `docs/api-contract.md` | the agreed contract |
| `docker-compose.yml`, `.env.example` | project-wide |

### Practical habits that prevent conflicts

- Create **new files** rather than expanding existing ones where reasonable. Two
  new files never conflict; one shared file edited twice always does.
- Add your router registration line to `router.py` as a **single line** and push
  it early, before the module is finished.
- Keep formatting consistent so diffs stay small. Do not reformat a file you did
  not otherwise change — a whitespace-only diff hides the real change and
  guarantees a conflict.
- Never commit `.env`, `node_modules/`, `.venv/`, or `.next/`. They are
  git-ignored; if you find yourself force-adding one, stop and ask.

---

## 3. How frontend and backend coordinate an API change

The contract is the interface between two halves of the team. Treat a change to
it as a change to a shared dependency.

**When the backend adds or changes an endpoint:**

1. Agree the shape in `docs/api-contract.md` **before** writing the code, if the
   frontend will consume it. A five-minute conversation beats a two-hour
   integration debug.
2. Implement it. FastAPI regenerates `http://localhost:8000/docs` automatically.
3. In the **same pull request**, update:
   - `docs/api-contract.md` — move the endpoint from "reserved" to "implemented"
   - `frontend/types/api.ts` — the matching TypeScript type
   - `frontend/lib/api.ts` — a method for the new endpoint
4. Post in the team channel: endpoint, method, request shape, response shape.

**When the frontend needs an endpoint that does not exist yet:**

1. Write the proposed request and response into `docs/api-contract.md`.
2. Get the owning backend developer to confirm the shape.
3. Build against a local stub while they implement it. Do **not** invent a shape
   privately and hope it matches.

**Rules that are not negotiable:**

- The **backend is the source of truth** for response shapes. `/docs` cannot
  drift from the code; this repository's Markdown can.
- Renaming a field is a breaking change. Announce it before merging.
- Never change a shared response shape in a PR whose description does not
  mention it.

---

## 4. Daily rhythm

**Start of day**

```bash
git checkout main && git pull origin main
docker compose up -d          # PostgreSQL
```

Then start your app — see [../README.md](../README.md) for the exact commands.

**Before you push**

| Side | Command |
| --- | --- |
| Frontend | `npm run typecheck` and `npm run lint` |
| Backend | confirm the app imports and `GET /health` still responds |

Push nothing that fails typecheck. Twelve seconds of checking saves a teammate
an hour.

**End of day**

Push your branch even if the work is unfinished. Work that exists only on one
laptop is work the team can lose.

---

## 5. Definition of done

A change is done when:

- it works locally and does not break `GET /health` or `npm run build`
- no secret, `.env` file, or build artefact is committed
- shared docs and types are updated in the same PR
- a teammate has reviewed it
- for any AI-derived output: the reasoning is returned alongside the result, and
  a human still makes the final decision

---

## 6. Project rules

These are constraints, not preferences. The full list is in
[../README.md](../README.md#project-rules). The ones that bite most often during
day-to-day work:

- Never build a fake integration with a government system.
- Never claim production deployment or an official partnership.
- Clearly label demo data as demo data.
- AI suggests; humans validate.
- Keep secrets out of the repository — use `.env.example`.
- Do not change unrelated files.
