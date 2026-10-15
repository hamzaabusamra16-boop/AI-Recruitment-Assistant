

import json
import sys
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from schemas import (
    CandidateDecisionRequest,
    CandidateScreeningRequest,
    JobDescriptionRequest,
    RankingRequest,
)
from services import (
    load_candidate_decisions,
    load_ranked_candidates,
    rank_saved_candidates,
    save_candidate_decision,
)
from AI.AI import screen_candidate

app = FastAPI(
    title="AI Recruitment Screening Assistant",
    description="API for AI-powered CV screening and candidate ranking",
    version="1.0.0",
)

RESULTS_FILE = BASE_DIR / ".env_" / "ranked_candidates.json"
DECISIONS_FILE = BASE_DIR / ".env_" / "candidate_decisions.json"
jobs_db: dict[str, dict] = {}
@app.get("/")
def home():
    return {
        "message": "AI Recruitment Screening API is running"
    }

@app.post("/jobs", status_code=201)
def create_job(job: JobDescriptionRequest):
    job_id = str(uuid4())

    new_job = {
        "id": job_id,
        "title": job.title,
        "description": job.description,
        "status": "created",
    }

    jobs_db[job_id] = new_job

    return new_job
BASE_DIR = Path(__file__).resolve().parent.parent
RESULTS_FILE = BASE_DIR / ".env_" / "ranked_candidates.json"
DECISIONS_FILE = BASE_DIR / ".env_" / "candidate_decisions.json"
@app.get("/jobs")
def get_jobs():
    return list(jobs_db.values())

@app.post("/screen")
def screen_cv(request: CandidateScreeningRequest):
    result = screen_candidate(
        cv_text=request.cv_text,
        job_description=request.job_description,
    )

    return result
@app.get("/candidates")
def get_candidates():
    return load_ranked_candidates()

@app.post("/candidates/rank")
def rank_candidates_endpoint(request: RankingRequest):
    result = rank_saved_candidates(top_n=request.top_n)

    return {
        "total_candidates": len(result["candidates"]),
        "qualified_candidates": sum(
            item["ranking"]["all_must_have_satisfied"]
            for item in result["candidates"]
        ),
        "shortlist": result["shortlist"],
    }


@app.put("/candidates/{candidate_index}/decision")
def update_candidate_decision(
    candidate_index: int,
    request: CandidateDecisionRequest,
):
    candidates = load_ranked_candidates()

    if candidate_index < 0 or candidate_index >= len(candidates):
        raise HTTPException(
            status_code=404,
            detail="Candidate not found",
        )

    candidate = candidates[candidate_index]

    candidate_info = candidate.get("candidate", {})

    candidate_id = (
        candidate.get("message_id")
        or candidate.get("id")
        or candidate_info.get("email")
    )

    if not candidate_id:
        raise HTTPException(
            status_code=400,
            detail="Candidate has no stable ID or email",
        )

    saved_decision = save_candidate_decision(
        candidate_id=str(candidate_id),
        decision=request.decision,
        notes=request.notes,
    )

    return {
        "candidate_id": candidate_id,
        **saved_decision,
    }
@app.get("/candidate-decisions")
def get_candidate_decisions():
    return load_candidate_decisions()

@app.get("/candidates-with-decisions")
def get_candidates_with_decisions():
    if not RESULTS_FILE.exists():
        raise HTTPException(
            status_code=404,
            detail="No candidate results file found",
        )

    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    candidates = data["candidates"] if isinstance(data, dict) else data

    decisions = {}

    if DECISIONS_FILE.exists():
        with open(DECISIONS_FILE, "r", encoding="utf-8") as file:
            decisions = json.load(file)

    result = []

    for index, candidate in enumerate(candidates):
        candidate_info = candidate.get("candidate", {})

        candidate_id = (
            candidate.get("message_id")
            or candidate.get("id")
            or candidate_info.get("email")
        )
        result.append({
            "candidate_index": index,
            "candidate": candidate,
            "hr_decision": decisions.get(candidate_id),
        })

    return result
