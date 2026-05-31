import uuid
import json
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.resume import Resume, Job, TailoredResume
from app.schemas.resume import ParsedResume
from app.services.openai_client import client

_TAILOR_SYSTEM = """You are an expert resume writer. Rewrite the resume to better match the job requirements.
Return the full tailored resume as JSON using exactly the same structure as the input resume.

Rules — follow these strictly:
1. NEVER invent experience, skills, or credentials that are not in the original resume.
2. PRESERVE all companies, roles, titles, dates, and institutions exactly as they appear.
3. REFRAME bullets to highlight skills relevant to the job — use the job's language and keywords
   where they accurately describe what the candidate did.
4. ADD missing required skills to the skills section only if they genuinely appear anywhere in
   the resume (e.g. mentioned in a project but not in skills).
5. IMPROVE impact language: add metrics, scale, and outcomes where the original is vague,
   but only if you can reasonably infer them from context.
6. REWRITE the summary (or create one if absent) to directly address the job's key requirements.
7. Return valid JSON. Do not include markdown fences or explanation — only the JSON object.

The output must follow the exact same JSON schema as the input resume."""


async def stream_tailored_resume(
    resume: Resume,
    job: Job,
) -> AsyncGenerator[str, None]:
    user_prompt = f"""INPUT RESUME:
{json.dumps(resume.parsed_sections, indent=2)}

JOB REQUIREMENTS:
{json.dumps(job.parsed_requirements, indent=2)}

JOB DESCRIPTION (full text for context):
{job.raw_description[:3000]}
"""
    stream = await client.chat.completions.create(
        model="gpt-4o",
        temperature=0.3,
        stream=True,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": _TAILOR_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
    )

    accumulated = ""
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            accumulated += delta
            yield f"data: {json.dumps({'type': 'token', 'content': delta})}\n\n"

    # Validate and return the complete tailored resume
    try:
        parsed = ParsedResume(**json.loads(accumulated))
        yield f"data: {json.dumps({'type': 'sections', 'sections': parsed.model_dump()})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


async def save_tailored_resume(
    resume_id: uuid.UUID,
    job_id: uuid.UUID,
    sections: dict,
    score: float | None,
    score_details: dict | None,
    db: AsyncSession,
) -> TailoredResume:
    tailored = TailoredResume(
        id=uuid.uuid4(),
        resume_id=resume_id,
        job_id=job_id,
        sections=sections,
        score=score,
        score_details=score_details,
        version=1,
    )
    db.add(tailored)
    await db.commit()
    await db.refresh(tailored)
    return tailored


async def get_resume_and_job(
    resume_id: uuid.UUID,
    job_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[Resume, Job]:
    resume_result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = resume_result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    return resume, job
