from extraction import extract
from universities import universities


# Ask citizen for the problem
problem = input("\nEnter your problem: ")


# Send problem to AI
data = extract(problem)


# Check if AI extraction failed
if "error" in data:
    print("\nAI extraction failed:")
    print(data["message"])
    exit()


# Get required capabilities automatically from AI
required_capabilities = data.get(
    "required_capabilities", []
)


print("\n================================")
print("        PROBLEM ANALYSIS")
print("================================")

print("\nProblem:")
print(data.get("problem", problem))

print("\nDomain:")
print(data.get("domain", "Unknown"))

print("\nRequired Capabilities:")
print(", ".join(required_capabilities))


# Matching
results = []

for university in universities:

    university_skills = [
        skill.lower().strip()
        for skill in university.get("skills", [])
    ]

    matched = []

    for capability in required_capabilities:

        capability = capability.lower().strip()

        # Check whether capability matches
        # any university skill
        for skill in university_skills:

            if (
                capability in skill
                or skill in capability
            ):
                matched.append(capability)
                break


    # Remove duplicates
    matched = list(set(matched))


    # Calculate score
    if len(required_capabilities) > 0:

        score = (
            len(matched)
            / len(required_capabilities)
        ) * 100

    else:
        score = 0


    results.append({
        "name": university["name"],
        "score": round(score, 2),
        "matched": matched
    })


# Highest score first
results.sort(
    key=lambda x: x["score"],
    reverse=True
)


# Show results
print("\n================================")
print("        BEST MATCHES")
print("================================")


# Show only universities with a match
found = False

for number, result in enumerate(results, start=1):

    if result["score"] > 0:

        found = True

        print(
            f"\n{number}. {result['name']}"
        )

        print(
            f"   Match Score: {result['score']}%"
        )

        print(
            "   Matching Capabilities:",
            ", ".join(result["matched"])
        )


if not found:

    print(
        "\nNo suitable university found."
    )