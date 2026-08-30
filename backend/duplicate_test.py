import json

from embedding import embed, find_similar


# --------------------------------------------------
# STEP 1: Load fixtures
# --------------------------------------------------

with open("fixtures.json", "r", encoding="utf-8") as file:
    fixtures = json.load(file)


# --------------------------------------------------
# STEP 2: Create in-memory vector store
# --------------------------------------------------

stored_vectors = []


# --------------------------------------------------
# STEP 3: Generate embeddings for fixtures
# --------------------------------------------------

print("\nGenerating embeddings for fixtures...\n")


for fixture in fixtures:

    print("Embedding:", fixture["id"])

    vector = embed(
        fixture["description"]
    )

    stored_vectors.append({
        "id": fixture["id"],
        "text": fixture["description"],
        "vector": vector,
        "cluster_id": None
    })


print("\nAll fixture embeddings created.")


# --------------------------------------------------
# STEP 4: Create a new citizen complaint
# --------------------------------------------------

new_text = (
    "There is a leaking water pipe "
    "near the Main Market."
)


print("\n" + "=" * 70)

print("NEW CITIZEN COMPLAINT:")
print(new_text)

print("=" * 70)


# --------------------------------------------------
# STEP 5: Create embedding for new complaint
# --------------------------------------------------

new_vector = embed(new_text)


# --------------------------------------------------
# STEP 6: Find similar complaints
# --------------------------------------------------

matches = find_similar(
    new_vector,
    stored_vectors,
    threshold=0.80
)


# --------------------------------------------------
# STEP 7: Display possible duplicates
# --------------------------------------------------

print("\nPOSSIBLE DUPLICATES:\n")


if not matches:

    print("No similar complaints found.")


else:

    for match in matches:

        print(
            f"{match['id']} "
            f"→ similarity: "
            f"{match['similarity']:.3f}"
        )

        print(
            f"   {match['text']}"
        )

        print()


print("=" * 70)