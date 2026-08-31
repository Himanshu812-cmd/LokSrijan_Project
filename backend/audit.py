from datetime import datetime,timezone

from data.store import audit_logs


def create_audit_log(
    challenge_id: int,
    user_id: int,
    action: str,
    old_value: str | None = None,
    new_value: str | None = None
):

    audit_entry = {
        "id": len(audit_logs) + 1,
        "challenge_id": challenge_id,
        "user_id": user_id,
        "action": action,
        "old_value": old_value,
        "new_value": new_value,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    audit_logs.append(audit_entry)

    return audit_entry
def get_challenge_audit_logs(challenge_id: int):
    return [
        log
        for log in audit_logs
        if log["challenge_id"] == challenge_id
    ]