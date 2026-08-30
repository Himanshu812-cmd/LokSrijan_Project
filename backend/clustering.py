import json
import os

from dotenv import load_dotenv
from google import genai

from embedding import embed
from sklearn.metrics.pairwise import cosine_similarity


# ==================================================
# LOAD ENVIRONMENT VARIABLES
# ==================================================

load_dotenv()


# Get Gemini API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from .env file")


# Create Gemini client
client = genai.Client(
    api_key=api_key
)


# ==================================================
# SETTINGS
# ==================================================

SIMILARITY_THRESHOLD = 0.80

# ==================================================
# CHECK IF COMPLAINT BELONGS TO A CLUSTER
# ==================================================

def find_matching_cluster(
    new_vector,
    clusters,
    threshold=SIMILARITY_THRESHOLD
):
    """
    Check whether the new complaint is similar
    to any existing complaint in any cluster.

    Returns:
        cluster_id if a match is found
        None if no match is found
    """

    best_cluster_id = None
    best_similarity = 0.0

    for cluster in clusters:

        for member in cluster["members"]:

            similarity = cosine_similarity(
                [new_vector],
                [member["vector"]]
            )[0][0]

            similarity = float(similarity)

            # Keep the strongest match
            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster_id = cluster["cluster_id"]


    # Only accept if similarity crosses threshold
    if best_similarity >= threshold:

        return best_cluster_id, best_similarity


    return None, best_similarity


# ==================================================
# ADD COMPLAINT TO CLUSTER
# ==================================================

def add_to_cluster(
    cluster,
    fixture,
    vector
):
    """
    Add a citizen complaint to an existing cluster.
    """

    cluster["members"].append({
    "id": fixture["id"],
    "text": fixture["description"],
    "location": fixture.get("location", ""),
    "vector": vector
})


# ==================================================
# CREATE NEW CLUSTER
# ==================================================

def create_cluster(
    clusters,
    fixture,
    vector
):
    """
    Create a completely new cluster.
    """

    cluster_number = len(clusters) + 1

    cluster_id = f"CLUSTER-{cluster_number:03d}"

    new_cluster = {
        "cluster_id": cluster_id,
        "cluster_name": "Generating...",
        "members": [
            {
                "id": fixture["id"],
                "text": fixture["description"],
                "vector": vector
            }
        ]
    }

    clusters.append(new_cluster)

    return new_cluster


# ==================================================
# MAIN CLUSTERING PROCESS
# ==================================================

def build_clusters(fixtures):
    """
    Process all citizen complaints and group
    similar complaints into clusters.
    """

    clusters = []


    for index, fixture in enumerate(fixtures):

        print(
            f"\nProcessing "
            f"{fixture['id']} "
            f"({index + 1}/{len(fixtures)})"
        )

        # ------------------------------------------
        # Create embedding
        # ------------------------------------------

        vector = embed(
            fixture["description"]
        )


        # ------------------------------------------
        # Check existing clusters
        # ------------------------------------------

        cluster_id, similarity = find_matching_cluster(
            vector,
            clusters
        )


        # ------------------------------------------
        # If matching cluster exists
        # ------------------------------------------

        if cluster_id is not None:

            print(
                f"  → Joining {cluster_id}"
            )

            print(
                f"  → Similarity: "
                f"{similarity:.3f}"
            )


            # Find the cluster
            for cluster in clusters:

                if cluster["cluster_id"] == cluster_id:

                    add_to_cluster(
                        cluster,
                        fixture,
                        vector
                    )

                    break


        # ------------------------------------------
        # Otherwise create new cluster
        # ------------------------------------------

        else:

            new_cluster = create_cluster(
                clusters,
                fixture,
                vector
            )

            print(
                f"  → Created "
                f"{new_cluster['cluster_id']}"
            )


    return clusters


# ==================================================
# GENERATE NAMES FOR CLUSTERS
# ==================================================

def name_clusters(clusters):
    """
    Generate names for all clusters using ONE Gemini API call.
    """

    if not clusters:
        return clusters

    # Prepare all cluster information
    cluster_text = ""

    for cluster in clusters:

        cluster_text += f"\n{cluster['cluster_id']}:\n"

        for member in cluster["members"]:
            cluster_text += f"- {member['text']}\n"


    prompt = f"""
You are organizing citizen complaints into problem groups.

Below are several clusters of complaints.

{cluster_text}

For EACH cluster, generate a short, clear name
describing the common problem.

Rules:
- Maximum 6 words per name
- Keep the cluster IDs exactly as provided
- Return ONLY valid JSON
- Do not add markdown
- Do not add explanations

Required format:

{{
  "CLUSTER-001": "Short Problem Name",
  "CLUSTER-002": "Short Problem Name"
}}
"""


    print("\nGenerating names for all clusters...")


    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        text = response.text.strip()


        # Remove markdown fences if Gemini adds them
        if text.startswith("```"):

            text = text.replace("```json", "")
            text = text.replace("```", "")

            text = text.strip()


        names = json.loads(text)


        # Assign names to clusters
        for cluster in clusters:

            cluster_id = cluster["cluster_id"]

            cluster["cluster_name"] = names.get(
                cluster_id,
                "Unnamed Problem"
            )


    except Exception as e:

        print("\nCould not generate cluster names.")
        print("Reason:", e)

        # Give clusters a fallback name
        for cluster in clusters:

            cluster["cluster_name"] = (
                f"Problem Group {cluster['cluster_id']}"
            )


    return clusters


# ==================================================
# DISPLAY RESULTS
# ==================================================

def display_clusters(clusters):

    print("\n")
    print("=" * 70)
    print("FINAL PROBLEM CLUSTERS")
    print("=" * 70)


    for cluster in clusters:

        print(
            f"\n{cluster['cluster_id']}"
        )

        print(
            f"Problem: "
            f"{cluster['cluster_name']}"
        )

        print(
            f"Number of reports: "
            f"{len(cluster['members'])}"
        )

        print("Citizen reports:")


        for member in cluster["members"]:

            print(
                f"  • {member['id']}: "
                f"{member['text']}"
            )


        print("-" * 70)


# ==================================================
# SAVE RESULTS
# ==================================================

def save_clusters(clusters):

    # Remove vectors before saving because
    # they make the JSON unnecessarily large.

    clean_clusters = []

    for cluster in clusters:

        clean_cluster = {
            "cluster_id": cluster["cluster_id"],
            "cluster_name": cluster["cluster_name"],
            "member_ids": [
                member["id"]
                for member in cluster["members"]
            ]
        }

        clean_clusters.append(
            clean_cluster
        )


    with open(
        "clusters.json",
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            clean_clusters,
            file,
            indent=2,
            ensure_ascii=False
        )


    print(
        "\nClusters saved to clusters.json"
    )


# ==================================================
# RUN PROGRAM
# ==================================================

if __name__ == "__main__":

    # ----------------------------------------------
    # Load fixtures
    # ----------------------------------------------

    with open(
        "fixtures.json",
        "r",
        encoding="utf-8"
    ) as file:

        fixtures = json.load(file)


    print("=" * 70)
    print("STARTING CLUSTERING")
    print("=" * 70)


    # ----------------------------------------------
    # Build clusters
    # ----------------------------------------------

    clusters = build_clusters(
        fixtures
    )


    # ----------------------------------------------
    # Generate names
    # ----------------------------------------------

    clusters = name_clusters(
        clusters
    )


    # ----------------------------------------------
    # Display results
    # ----------------------------------------------

    display_clusters(
        clusters
    )


    # ----------------------------------------------
    # Save results
    # ----------------------------------------------

    save_clusters(
        clusters
    )