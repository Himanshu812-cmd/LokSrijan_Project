from data.store import evidence, next_evidence_id
def add_evidence(
    challenge_id: int,
    evidence_type: str,
    description: str,
    url: str,
    submitted_by: int
):
    global next_evidence_id
    evidence_entry = {
        "id": next_evidence_id,
        "challenge_id": challenge_id,
        "evidence_type": evidence_type,
        "description": description,
        "url": url,
        "submitted_by": submitted_by
    }
    evidence[next_evidence_id] = evidence_entry
    next_evidence_id += 1
    return evidence_entry
def get_challenge_evidence(challenge_id: int):
    return [
        item
        for item in evidence.values()
        if item["challenge_id"] == challenge_id
    ]