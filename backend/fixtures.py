# fixtures.py
# These fake B1's challenge output and B3's match output.
# You use these to build and test BE-4 completely on your own.

fake_challenges = [
    {"id": "CH-001", "domain": "Water", "priority_score": 82},
    {"id": "CH-002", "domain": "Education", "priority_score": 65},
    {"id": "CH-003", "domain": "Healthcare", "priority_score": 74},
]

fake_matches = [
    {"challenge_id": "CH-001", "university": "IIT Dhanbad", "team": ["Dr. Rao", "S. Kumar", "A. Singh"]},
    {"challenge_id": "CH-002", "university": "BIT Mesra", "team": ["Dr. Verma", "P. Das"]},
    {"challenge_id": "CH-003", "university": "NIT Jamshedpur", "team": ["Dr. Iyer", "R. Sharma"]},
]
