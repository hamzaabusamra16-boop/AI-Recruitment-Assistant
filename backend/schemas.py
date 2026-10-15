from pydantic import BaseModel, Field
from typing import Literal

class JobDescriptionRequest(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: str = Field(min_length=20)

class CandidateScreeningRequest(BaseModel):
    cv_text: str = Field(min_length=50)
    job_description: str = Field(min_length=20)
class CandidateDecisionRequest(BaseModel):
    decision: Literal["Shortlist", "Review Later", "Reject"]
    notes: str = Field(default="", max_length=1000)

class RankingRequest(BaseModel):
    top_n: int = Field(default=20, ge=1, le=100)
