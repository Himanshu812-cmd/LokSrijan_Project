# project_store.py
# BE-4: Execution & Impact Engine
#
# This file is your entire domain: Projects, Milestones, Impact, Analytics.
# No LLM calls anywhere — it's CRUD + deterministic math.

from collections import Counter

# ----------------------------------------------------------------------
# In-memory store. In a real DB this would be a table; for the hackathon
# it's just a list of dicts. B1 does the same thing for Challenges.
# ----------------------------------------------------------------------
projects: list[dict] = []


# ----------------------------------------------------------------------
# 1. PROJECT CRUD
# ----------------------------------------------------------------------
def create_project(challenge_id: str, university: str, team: list[str]) -> dict:
    """
    Called when B3 reports an accepted university match for a challenge.
    Until B3 is ready, call this yourself with fixtures.fake_matches.
    """
    project = {
        "id": f"PRJ-{len(projects) + 1:03d}",
        "challenge_id": challenge_id,
        "university": university,
        "team": team,
        # Status lifecycle: PROPOSED -> ACTIVE -> PILOT -> COMPLETED -> DROPPED
        "status": "PROPOSED",
        "milestones": [],
        "impact": None,
    }
    projects.append(project)
    return project


def get_project(project_id: str) -> dict | None:
    return next((p for p in projects if p["id"] == project_id), None)


def update_status(project_id: str, new_status: str) -> dict | None:
    valid = {"PROPOSED", "ACTIVE", "PILOT", "COMPLETED", "DROPPED"}
    if new_status not in valid:
        raise ValueError(f"Invalid status '{new_status}'. Must be one of {valid}")
    p = get_project(project_id)
    if p:
        p["status"] = new_status
    return p


# ----------------------------------------------------------------------
# 2. MILESTONE CRUD
# ----------------------------------------------------------------------
def add_milestone(project_id: str, title: str, due_date: str) -> dict | None:
    p = get_project(project_id)
    if not p:
        return None
    milestone = {
        "id": f"M-{len(p['milestones']) + 1}",
        "title": title,
        "due_date": due_date,
        # Status lifecycle: PENDING -> IN_PROGRESS -> DONE -> DELAYED
        "status": "PENDING",
    }
    p["milestones"].append(milestone)
    return milestone


def update_milestone_status(project_id: str, milestone_id: str, status: str) -> dict | None:
    valid = {"PENDING", "IN_PROGRESS", "DONE", "DELAYED"}
    if status not in valid:
        raise ValueError(f"Invalid status '{status}'. Must be one of {valid}")
    p = get_project(project_id)
    if not p:
        return None
    for m in p["milestones"]:
        if m["id"] == milestone_id:
            m["status"] = status
    return p


# ----------------------------------------------------------------------
# 3. IMPACT CALCULATION
# ----------------------------------------------------------------------
def calculate_impact(baseline: float, target: float, actual: float) -> dict:
    """
    baseline = value before the project started (e.g. 100 households without clean water)
    target   = the goal the team is aiming for (e.g. 20 households)
    actual   = current measured value (e.g. 40 households)

    pct_improvement measures how much of the "bad" baseline has been reduced.
    target_met checks if actual has crossed the target, handling both
    "lower is better" (e.g. dropout %) and "higher is better" (e.g. literacy %) cases.
    """
    if baseline == 0:
        pct_improvement = 0.0
    else:
        pct_improvement = ((baseline - actual) / baseline) * 100

    if target < baseline:
        # Goal is to bring the number DOWN (e.g. dropout rate, disease cases)
        target_met = actual <= target
    else:
        # Goal is to bring the number UP (e.g. literacy rate, yield)
        target_met = actual >= target

    return {
        "baseline": baseline,
        "target": target,
        "actual": actual,
        "pct_improvement": round(pct_improvement, 2),
        "target_met": target_met,
    }


def set_project_impact(project_id: str, baseline: float, target: float, actual: float) -> dict | None:
    p = get_project(project_id)
    if not p:
        return None
    p["impact"] = calculate_impact(baseline, target, actual)
    return p


# ----------------------------------------------------------------------
# 4. ANALYTICS
# ----------------------------------------------------------------------
def project_counts_by_status() -> dict:
    return dict(Counter(p["status"] for p in projects))


def project_counts_by_university() -> dict:
    return dict(Counter(p["university"] for p in projects))


def avg_impact() -> float:
    impacts = [p["impact"]["pct_improvement"] for p in projects if p["impact"]]
    return round(sum(impacts) / len(impacts), 2) if impacts else 0.0


def project_counts_by_domain(fake_challenges: list[dict]) -> dict:
    """
    Domain isn't stored on the project itself — it lives on B1's Challenge.
    This joins on challenge_id. Swap `fake_challenges` for B1's real store later;
    nothing else in this file changes.
    """
    domain_by_challenge = {c["id"]: c["domain"] for c in fake_challenges}
    domains = [domain_by_challenge.get(p["challenge_id"], "Unknown") for p in projects]
    return dict(Counter(domains))
