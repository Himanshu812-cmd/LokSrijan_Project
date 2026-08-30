import json

from clustering import (
    build_clusters,
    name_clusters,
    find_matching_cluster,
    add_to_cluster
)

from embedding import embed


# ==================================================
# GLOBAL CLUSTER STORE
# ==================================================

clusters = []


# ==================================================
# REPORT ID COUNTER
# ==================================================

next_report_number = 1


# ==================================================
# INITIALIZE CLUSTERS
# ==================================================

def initialize_clusters():
    """
    Load fixtures, build clusters, and prepare
    the next available citizen report ID.
    """

    global clusters
    global next_report_number

    print("\n")
    print("=" * 70)
    print("INITIALIZING PROBLEM CLUSTERS")
    print("=" * 70)

    # ----------------------------------------------
    # Load fixtures
    # ----------------------------------------------

    with open(
        "fixtures.json",
        "r",
        encoding="utf-8"
    ) as file:

        fixtures = json.load(file)

    # ----------------------------------------------
    # Build initial clusters
    # ----------------------------------------------

    clusters = build_clusters(fixtures)

    # ----------------------------------------------
    # Generate cluster names
    # ----------------------------------------------

    clusters = name_clusters(clusters)

    # ----------------------------------------------
    # Find highest existing CIT number
    # ----------------------------------------------

    highest_number = 0

    for fixture in fixtures:

        report_id = fixture["id"]

        if report_id.startswith("CIT-"):

            try:
                number = int(
                    report_id.replace("CIT-", "")
                )

                highest_number = max(
                    highest_number,
                    number
                )

            except ValueError:
                pass

    next_report_number = highest_number + 1

    # ----------------------------------------------
    # Display clusters
    # ----------------------------------------------

    print("\n")
    print("=" * 70)
    print("CLUSTERS INITIALIZED")
    print("=" * 70)

    for cluster in clusters:

        print(
            f"{cluster['cluster_id']} - "
            f"{cluster['cluster_name']} - "
            f"{len(cluster['members'])} reports"
        )

    print(
        f"\nNext citizen report ID: "
        f"CIT-{next_report_number:03d}"
    )


# ==================================================
# GENERATE NEW REPORT ID
# ==================================================

def generate_report_id():

    global next_report_number

    report_id = (
        f"CIT-{next_report_number:03d}"
    )

    next_report_number += 1

    return report_id


# ==================================================
# FIND SIMILAR REPORTS
# ==================================================

def find_similar_reports(
    new_vector,
    threshold=0.80
):
    """
    Find existing reports similar to a new complaint.
    """

    from sklearn.metrics.pairwise import cosine_similarity

    matches = []

    for cluster in clusters:

        for member in cluster["members"]:

            similarity = cosine_similarity(
                [new_vector],
                [member["vector"]]
            )[0][0]

            similarity = float(similarity)

            if similarity >= threshold:

                matches.append({
                    "id": member["id"],
                    "similarity_score": round(
                        similarity,
                        3
                    ),
                    "cluster_id":
                        cluster["cluster_id"],
                    "cluster_name":
                        cluster["cluster_name"]
                })

    # Highest similarity first

    matches.sort(
        key=lambda x: x["similarity_score"],
        reverse=True
    )

    return matches


# ==================================================
# PROCESS NEW COMPLAINT
# ==================================================

def process_new_complaint(
    title,
    description,
    location,
    threshold=0.80
):
    """
    Process a new citizen complaint.

    Generates a new ID, creates its embedding,
    checks for similarity, and either joins an
    existing cluster or creates a new cluster.
    """

    # ----------------------------------------------
    # Generate new ID
    # ----------------------------------------------

    complaint_id = generate_report_id()

    # ----------------------------------------------
    # Create embedding
    # ----------------------------------------------

    vector = embed(description)

    # ----------------------------------------------
    # Find similar reports
    # ----------------------------------------------

    similar_reports = find_similar_reports(
        vector,
        threshold
    )

    # ----------------------------------------------
    # Find matching cluster
    # ----------------------------------------------

    cluster_id, similarity = find_matching_cluster(
        vector,
        clusters,
        threshold
    )

    # ==================================================
    # EXISTING CLUSTER
    # ==================================================

    if cluster_id is not None:

        matched_cluster = None

        for cluster in clusters:

            if cluster["cluster_id"] == cluster_id:

                matched_cluster = cluster
                break

        complaint = {
            "id": complaint_id,
            "title": title,
            "description": description,
            "location": location
        }

        # Add new report to existing cluster

        add_to_cluster(
            matched_cluster,
            complaint,
            vector
        )

        return {
            "report_id": complaint_id,

            "action":
                "joined_existing_cluster",

            "cluster_id":
                matched_cluster["cluster_id"],

            "cluster_name":
                matched_cluster["cluster_name"],

            "similarity_score":
                round(similarity, 3),

            "similar_reports":
                similar_reports,

            "member_count":
                len(matched_cluster["members"])
        }

    # ==================================================
    # CREATE NEW CLUSTER
    # ==================================================

    else:

        cluster_number = len(clusters) + 1

        new_cluster_id = (
            f"CLUSTER-{cluster_number:03d}"
        )

        new_cluster = {

            "cluster_id":
                new_cluster_id,

            "cluster_name":
                title,

            "members": [

                {
                    "id":
                        complaint_id,

                    "text":
                        description,

                    "Location":
                        location,

                    "vector":
                        vector
                }

            ]
        }

        clusters.append(
            new_cluster
        )

        return {

            "report_id":
                complaint_id,

            "action":
                "created_new_cluster",

            "cluster_id":
                new_cluster_id,

            "cluster_name":
                title,

            "similar_reports":
                similar_reports,

            "member_count":
                1
        }


# ==================================================
# GET CLUSTER
# ==================================================

def get_cluster(cluster_id):

    for cluster in clusters:

        if cluster["cluster_id"] == cluster_id:

            return {

                "cluster_id":
                    cluster["cluster_id"],

                "cluster_name":
                    cluster["cluster_name"],

                "member_ids": [

                    member["id"]

                    for member
                    in cluster["members"]

                ],

                "member_count":
                    len(cluster["members"])
            }

    return None


# ==================================================
# GET SIMILAR REPORTS BY ID
# ==================================================

def get_similar_by_id(
    report_id,
    threshold=0.80
):
    """
    Find reports similar to an existing report.
    """

    target_member = None

    # ----------------------------------------------
    # Find report
    # ----------------------------------------------

    for cluster in clusters:

        for member in cluster["members"]:

            if member["id"] == report_id:

                target_member = member
                break

        if target_member:
            break

    # ----------------------------------------------
    # Report not found
    # ----------------------------------------------

    if target_member is None:

        return None

    # ----------------------------------------------
    # Find similar reports
    # ----------------------------------------------

    similar_reports = find_similar_reports(
        target_member["vector"],
        threshold
    )

    # ----------------------------------------------
    # Remove itself
    # ----------------------------------------------

    similar_reports = [

        report

        for report
        in similar_reports

        if report["id"] != report_id

    ]

    return similar_reports

# ==================================================
# GET ALL CLUSTERS
# ==================================================

def get_all_clusters():
    """
    Return all currently available problem clusters.
    """

    results = []

    for cluster in clusters:

        results.append({
            "cluster_id": cluster["cluster_id"],
            "cluster_name": cluster["cluster_name"],
            "member_count": len(cluster["members"]),
            "member_ids": [
                member["id"]
                for member in cluster["members"]
            ]
        })

    return results

# ==================================================
# GET ALL REPORTS
# ==================================================

def get_all_reports():
    """
    Return all citizen reports currently stored
    inside the clusters.
    """

    reports = []

    for cluster in clusters:

        for member in cluster["members"]:

            reports.append({
                "id": member["id"],
                "description": member["text"],
                "location": member.get("location", ""),
                "cluster_id": cluster["cluster_id"],
                "cluster_name": cluster["cluster_name"]
            })

    return reports