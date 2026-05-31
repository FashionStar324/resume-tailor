import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.resume import Job, Resume
from app.schemas.job import ParsedRequirements, ScoreDetails
from app.services.openai_client import chat_json, get_embedding

_PARSE_JOB_SYSTEM = """You are a job description parser. Extract structured requirements and return JSON.

Return exactly this structure:
{
  "title": "string or null",
  "company": "string or null",
  "required_skills": ["string"],
  "preferred_skills": ["string"],
  "experience_years": integer or null,
  "key_responsibilities": ["string"],
  "seniority_level": "intern | junior | mid | senior | staff | principal | manager or null"
}

Rules:
- required_skills: explicitly required or must-have skills
- preferred_skills: nice-to-have or bonus skills
- Keep skill names concise (e.g. "Python", "React", "Kubernetes")
- key_responsibilities: 3–6 core responsibilities as short phrases
"""

_SCORE_SYSTEM = """You are a resume-to-job fit evaluator. Given a parsed resume and parsed job requirements,
return a structured match score as JSON.

Return exactly this structure:
{
  "keyword_match": float between 0 and 1,
  "experience_alignment": float between 0 and 1,
  "impact_language": float between 0 and 1,
  "overall": float between 0 and 1,
  "strengths": ["string — up to 5 specific things the resume does well for this job"],
  "missing": ["string — required skills or experience gaps, be specific"],
  "suggestions": ["string — up to 3 concrete actions to improve the match"]
}

Scoring rubric:
- keyword_match: what fraction of required_skills appear in the resume
- experience_alignment: how well the candidate's seniority, domain, and years of experience match
- impact_language: how well bullets use metrics, scale, and outcomes (not just responsibilities)
- overall: weighted average (keyword_match * 0.4 + experience_alignment * 0.35 + impact_language * 0.25)

Be honest — a 0.9 should be rare and mean the resume is nearly perfect for the role.
"""


async def parse_job_description(raw_description: str) -> ParsedRequirements:
    result = await chat_json(_PARSE_JOB_SYSTEM, raw_description)
    return ParsedRequirements(**result)


async def score_resume_against_job(
    resume: Resume,
    parsed_requirements: ParsedRequirements,
) -> ScoreDetails:
    user_prompt = f"""RESUME:
{json.dumps(resume.parsed_sections, indent=2)}

JOB REQUIREMENTS:
{json.dumps(parsed_requirements.model_dump(), indent=2)}
"""
    result = await chat_json(_SCORE_SYSTEM, user_prompt)
    return ScoreDetails(**result)


async def create_job_and_score(
    raw_description: str,
    resume_id: uuid.UUID,
    session_id: str,
    db: AsyncSession,
) -> tuple[Job, Resume, ParsedRequirements, ScoreDetails]:
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Resume not found.")

    parsed_requirements = await parse_job_description(raw_description)
    score = await score_resume_against_job(resume, parsed_requirements)

    job = Job(
        id=uuid.uuid4(),
        session_id=session_id,
        raw_description=raw_description,
        parsed_requirements=parsed_requirements.model_dump(),
    )
    db.add(job)
    await db.commit()
    await db.refresh(job)

    return job, resume, parsed_requirements, score
