# BE-4 — Execution & Impact Engine — How It Works

## The 4 files
| File | What it is |
|---|---|
| `fixtures.py` | Fake data pretending to be B1's challenges and B3's matches, so you can build/test alone |
| `project_store.py` | All your real logic: project CRUD, milestones, impact math, analytics — **no LLM calls** |
| `test_be4.py` | Runs the whole flow end-to-end with fixtures — run this first |
| `api.py` | Wraps the logic above in HTTP endpoints (FastAPI) |

## How to run it
```bash
pip install fastapi uvicorn
python3 test_be4.py              # see the logic work in plain terminal output
uvicorn api:app --reload         # start the real API at http://localhost:8000/docs
```

## The mental model (say this if asked "walk me through BE-4")
1. **A project is created** the moment B3 finds a university match for a challenge. It starts life as `PROPOSED`.
2. **It moves through a status lifecycle**: PROPOSED → ACTIVE → PILOT → COMPLETED (or DROPPED). You update this manually via `PATCH /projects/{id}/status`.
3. **Milestones** are just checkpoints inside a project (survey done, prototype built, etc.), each with their own status: PENDING → IN_PROGRESS → DONE → DELAYED.
4. **Impact** is a single formula, not AI: `((baseline - actual) / baseline) * 100`. It answers "how much of the original problem has shrunk." It handles both "lower is better" (disease cases) and "higher is better" (literacy rate) by checking whether the target sits below or above the baseline.
5. **Analytics** is just counting — `Counter()` over your in-memory list, grouped by status, university, domain, or averaged impact. Domain isn't stored on the project itself; it's joined in from the challenge (B1's data) using `challenge_id`.

## Why no database, no AI here
- No AI: BE-4 has no unstructured input to interpret — every field is a number or an enum a human/UI sets directly. That's B2's job (extraction/classification), not yours.
- No real DB: a Python list of dicts is enough for a hackathon demo; swapping in Postgres later means only touching `project_store.py`'s internals, not the API or the math.

## If a judge asks "what happens when a project fails to improve anything?"
`target_met` will be `False` and `pct_improvement` can even go negative (if `actual` is worse than `baseline`) — the formula doesn't hide bad outcomes, which is intentional for an honest government dashboard.

## Integration point with teammates
- **B3 → you**: their "accepted match" should call `create_project(challenge_id, university, team)`.
- **B1 → you**: your `/analytics/domain` currently reads `fixtures.fake_challenges`; once B1's real challenge store exists, swap that one argument for their real list.
