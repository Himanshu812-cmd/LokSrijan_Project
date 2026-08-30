# api.py
# BE-4: Execution & Impact Engine — HTTP layer
# This is the ONLY new thing added at this stage: everything it calls
# already worked and was tested in project_store.py / test_be4.py.

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fixtures import fake_challenges
import project_store as store

app = FastAPI(title="BE-4: Execution & Impact Engine")


# ---------- request bodies ----------
class CreateProjectRequest(BaseModel):
    challenge_id: str
    university: str
    team: list[str]


class StatusUpdateRequest(BaseModel):
    status: str


class MilestoneRequest(BaseModel):
    title: str
    due_date: str


class ImpactRequest(BaseModel):
    baseline: float
    target: float
    actual: float


# ---------- project endpoints ----------
@app.post("/projects")
def create_project(req: CreateProjectRequest):
    return store.create_project(req.challenge_id, req.university, req.team)


@app.get("/projects/{project_id}")
def get_project(project_id: str):
    p = store.get_project(project_id)
    if not p:
        raise HTTPException(404, "Project not found")
    return p


@app.patch("/projects/{project_id}/status")
def update_status(project_id: str, req: StatusUpdateRequest):
    try:
        p = store.update_status(project_id, req.status)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not p:
        raise HTTPException(404, "Project not found")
    return p


# ---------- milestone endpoints ----------
@app.post("/projects/{project_id}/milestones")
def add_milestone(project_id: str, req: MilestoneRequest):
    m = store.add_milestone(project_id, req.title, req.due_date)
    if not m:
        raise HTTPException(404, "Project not found")
    return m


@app.patch("/projects/{project_id}/milestones/{milestone_id}")
def update_milestone(project_id: str, milestone_id: str, req: StatusUpdateRequest):
    try:
        p = store.update_milestone_status(project_id, milestone_id, req.status)
    except ValueError as e:
        raise HTTPException(400, str(e))
    if not p:
        raise HTTPException(404, "Project not found")
    return p


# ---------- impact endpoint ----------
@app.post("/projects/{project_id}/impact")
def set_impact(project_id: str, req: ImpactRequest):
    p = store.set_project_impact(project_id, req.baseline, req.target, req.actual)
    if not p:
        raise HTTPException(404, "Project not found")
    return p["impact"]


# ---------- analytics endpoints ----------
@app.get("/analytics/status")
def analytics_status():
    return store.project_counts_by_status()


@app.get("/analytics/university")
def analytics_university():
    return store.project_counts_by_university()


@app.get("/analytics/domain")
def analytics_domain():
    # Swap fake_challenges for B1's real challenge store once it exists —
    # no other code in this file needs to change.
    return store.project_counts_by_domain(fake_challenges)


@app.get("/analytics/impact")
def analytics_impact():
    return {"avg_impact_pct": store.avg_impact()}
