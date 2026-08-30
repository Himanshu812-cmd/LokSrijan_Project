import json
from extraction import extract


# Load all fixtures
with open("fixtures.json", "r", encoding="utf-8") as file:
    fixtures = json.load(file)


# Test every fixture
for fixture in fixtures:

    print("\n" + "=" * 70)

    print("ID:", fixture["id"])
    print("TITLE:", fixture["title"])
    print("DESCRIPTION:", fixture["description"])

    result = extract(fixture["description"])

    print("\nAI OUTPUT:")
    print(json.dumps(result, indent=2))

    print("=" * 70)