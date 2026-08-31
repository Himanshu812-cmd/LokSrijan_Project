from fastapi import APIRouter, Depends, HTTPException

from schemas.challenge import (
    ChallengeCreate,
    ChallengeUpdate,
    ChallengeResponse,
    ChallengeStatusUpdate
)
from schemas.evidence import EvidenceCreate, EvidenceResponse
from services.evidence import add_evidence, get_challenge_evidence

from dependencies.auth import get_current_user

from data.store import challenges

from services.audit import (
    create_audit_log,
    get_challenge_audit_logs
)

from services.state_machine import can_transition
router = APIRouter(
    prefix="/challenges",
    tags=["Challenges"]
)
@router.post(
    "/",
    response_model=ChallengeResponse
)
def create_challenge(
    challenge_data: ChallengeCreate,
    current_user=Depends(get_current_user)
):

    global next_challenge_id

    challenge = {
        "id": next_challenge_id,

        "title": challenge_data.title,

        "description": challenge_data.description,

        "category": challenge_data.category,

        "location": challenge_data.location,

        "severity": challenge_data.severity,

        "status": "SUBMITTED",

        "created_by": current_user["id"]
    }

    challenges[next_challenge_id] = challenge

    create_audit_log(
        challenge_id=next_challenge_id,
        user_id=current_user["id"],
        action="CREATE_CHALLENGE"
    )

    next_challenge_id += 1

    return challenge
@router.get(
    "/",
    response_model=list[ChallengeResponse]
)
def get_challenges():

    return list(challenges.values())
@router.get(
    "/{challenge_id}",
    response_model=ChallengeResponse
)
def get_challenge(
    challenge_id: int
):

    challenge = challenges.get(challenge_id)

    if challenge is None:

        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    return challenge
@router.put(
    "/{challenge_id}",
    response_model=ChallengeResponse
)
def update_challenge(
    challenge_id: int,
    challenge_data: ChallengeUpdate,
    current_user=Depends(get_current_user)
):

    challenge = challenges.get(challenge_id)

    if challenge is None:

        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    old_data = challenge.copy()

    update_data = challenge_data.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():

        if value is not None:

            challenge[key] = value

    create_audit_log(
        challenge_id=challenge_id,
        user_id=current_user["id"],
        action="UPDATE_CHALLENGE"
    )

    return challenge
@router.delete(
    "/{challenge_id}"
)
def delete_challenge(
    challenge_id: int,
    current_user=Depends(get_current_user)
):

    challenge = challenges.get(challenge_id)

    if challenge is None:

        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    del challenges[challenge_id]

    create_audit_log(
        challenge_id=challenge_id,
        user_id=current_user["id"],
        action="DELETE_CHALLENGE"
    )

    return {
        "message": "Challenge deleted successfully"
    }
@router.patch(
    "/{challenge_id}/status",
    response_model=ChallengeResponse
)
def update_challenge_status(
    challenge_id: int,
    status_data: ChallengeStatusUpdate,
    current_user=Depends(get_current_user)
):

    challenge = challenges.get(challenge_id)

    if challenge is None:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    current_status = challenge["status"]
    new_status = status_data.new_status

    if not can_transition(
        current_status,
        new_status
    ):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition: {current_status} -> {new_status}"
        )

    challenge["status"] = new_status

    create_audit_log(
        challenge_id=challenge_id,
        user_id=current_user["id"],
        action="STATUS_CHANGE",
        old_value=current_status,
        new_value=new_status
    )

    return challenge
@router.post(
    "/{challenge_id}/evidence",
    response_model=EvidenceResponse
)
def create_evidence(
    challenge_id: int,
    evidence_data: EvidenceCreate,
    current_user=Depends(get_current_user)
):
    if challenge_id not in challenges:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    evidence_entry = add_evidence(
        challenge_id=challenge_id,
        evidence_type=evidence_data.evidence_type,
        description=evidence_data.description,
        url=evidence_data.url,
        submitted_by=current_user["id"]
    )

    create_audit_log(
        challenge_id=challenge_id,
        user_id=current_user["id"],
        action="EVIDENCE_ADDED",
        new_value=str(evidence_entry["id"])
    )

    return evidence_entry
@router.get(
    "/{challenge_id}/evidence",
    response_model=list[EvidenceResponse]
)
def get_evidence(
    challenge_id: int,
    current_user=Depends(get_current_user)
):
    if challenge_id not in challenges:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    return get_challenge_evidence(challenge_id)
@router.get("/{challenge_id}/audit")
def get_audit_logs(
    challenge_id: int,
    current_user=Depends(get_current_user)
):
    if challenge_id not in challenges:
        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    return get_challenge_audit_logs(challenge_id)