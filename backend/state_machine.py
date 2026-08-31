VALID_TRANSITIONS = {
    "SUBMITTED": [
        "UNDER_REVIEW"
    ],

    "UNDER_REVIEW": [
        "VALIDATED",
        "REJECTED"
    ],

    "VALIDATED": [
        "TEAM_FORMED"
    ],

    "TEAM_FORMED": [
        "IN_PROGRESS"
    ],

    "IN_PROGRESS": [
        "SOLUTION_PROPOSED"
    ],

    "SOLUTION_PROPOSED": [
        "IMPLEMENTED"
    ],

    "IMPLEMENTED": [
        "RESOLVED"
    ],

    "REJECTED": [],

    "RESOLVED": []
}


def can_transition(
    current_status: str,
    new_status: str
) -> bool:

    allowed_statuses = VALID_TRANSITIONS.get(
        current_status,
        []
    )

    return new_status in allowed_statuses