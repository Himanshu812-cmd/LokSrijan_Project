from fastapi import APIRouter, Depends, HTTPException

from data.store import challenges

from schemas.action import StatusUpdate

from dependencies.auth import get_current_user

from services.validation import validate_status_change

from services.audit import create_audit_log


router = APIRouter(
    prefix="/challenges",
    tags=["Challenge Actions"]
)
@router.patch(
    "/{challenge_id}/status"
)
def update_status(
    challenge_id: int,
    status_data: StatusUpdate,
    current_user=Depends(get_current_user)
):

    challenge = challenges.get(challenge_id)

    if challenge is None:

        raise HTTPException(
            status_code=404,
            detail="Challenge not found"
        )

    old_status = challenge["status"]

    new_status = status_data.new_status

    validate_status_change(
        old_status,
        new_status
    )

    challenge["status"] = new_status

    create_audit_log(
        challenge_id=challenge_id,
        user_id=current_user["id"],
        action="STATUS_CHANGE",
        old_value=old_status,
        new_value=new_status
    )

    return {
        "message": "Status updated successfully",
        "challenge_id": challenge_id,
        "old_status": old_status,
        "new_status": new_status
    }