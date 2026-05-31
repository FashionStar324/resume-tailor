from pydantic import BaseModel, Field
from typing import Optional
import uuid


class JobScoreRequest(BaseModel):
    resume_id: uuid.UUID
    job_description: str = Field(..., min_length=50)


class ParsedRequirements(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    required_skills: list[str] = []
    preferred_skills: list[str] = []
    experience_years: Optional[int] = None
    key_responsibilities: list[str] = []
    seniority_level: Optional[str] = None


class ScoreDetails(BaseModel):
    keyword_match: float = Field(..., ge=0, le=1)
    experience_alignment: float = Field(..., ge=0, le=1)
    impact_language: float = Field(..., ge=0, le=1)
    overall: float = Field(..., ge=0, le=1)
    strengths: list[str] = []
    missing: list[str] = []
    suggestions: list[str] = []


class JobScoreResponse(BaseModel):
    job_id: uuid.UUID
    resume_id: uuid.UUID
    parsed_requirements: ParsedRequirements
    score: ScoreDetails
