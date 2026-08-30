from fastapi import FastAPI
from pydantic import BaseModel

from extraction import extract
from cluster_manager import (
    initialize_clusters,
    process_new_complaint,
    get_similar_by_id,
    get_cluster,
    get_all_clusters,
    get_all_reports
)


# ==================================================
# FASTAPI APPLICATION
# ==================================================

app = FastAPI(
    title="LokSrijan Backend API",
    description="AI-powered societal problem analysis API",
    version="1.0"
)


# ==================================================
# INITIALIZE CLUSTERS
# ==================================================

initialize_clusters()


# ==================================================
# REQUEST MODEL
# ==================================================

class ProblemRequest(BaseModel):

    description: str
    location: str


# ==================================================
# HOME
# ==================================================

@app.get("/")
def home():

    return {
        "message": "LokSrijan Backend API is running"
    }


# ==================================================
# ANALYZE PROBLEM
# ==================================================

@app.post("/api/analyze")
def analyze_problem(request: ProblemRequest):

    # ----------------------------------------------
    # STEP 1: Extract information from description
    # ----------------------------------------------

    analysis = extract(
        request.description
    )

    # ----------------------------------------------
    # STEP 2: Process complaint
    # ----------------------------------------------

    result = process_new_complaint(

    title=analysis.get(
        "problem",
        "New Citizen Problem"
    ),

    description=request.description,

    location=request.location
)

    # ----------------------------------------------
    # STEP 3: Return response
    # ----------------------------------------------

    return {

        "success": True,

        "report_id":
            result["report_id"],

        "description":
            request.description,

        "location":
            request.location,

        "analysis":
            analysis,

        "similar_reports":
            result["similar_reports"],

        "cluster": {

            "cluster_id":
                result["cluster_id"],

            "cluster_name":
                result["cluster_name"],

            "member_count":
                result["member_count"]
        },

        "action":
            result["action"]
    }

# ==================================================
# GET SIMILAR REPORTS
# ==================================================

@app.get("/api/similar/{report_id}")
def get_similar_reports(report_id: str):

    results = get_similar_by_id(
        report_id
    )

    if results is None:

        return {
            "success": False,
            "message": "Report not found"
        }


    return {
        "success": True,
        "report_id": report_id,
        "similar_reports": results
    }


# ==================================================
# GET CLUSTER INFORMATION
# ==================================================

@app.get("/api/cluster/{cluster_id}")
def get_cluster_information(cluster_id: str):

    result = get_cluster(
        cluster_id
    )

    if result is None:

        return {
            "success": False,
            "message": "Cluster not found"
        }


    return {
        "success": True,
        "cluster": result
    }

# ==================================================
# GET ALL CLUSTERS
# ==================================================

@app.get("/api/clusters")
def get_all_problem_clusters():

    results = get_all_clusters()

    return {
        "success": True,
        "total_clusters": len(results),
        "clusters": results
    }

# ==================================================
# GET ALL REPORTS
# ==================================================

@app.get("/api/problems")
def get_all_problem_reports():

    reports = get_all_reports()

    return {
        "success": True,
        "total_reports": len(reports),
        "reports": reports
    }