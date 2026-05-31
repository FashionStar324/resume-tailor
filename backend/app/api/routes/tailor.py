import json
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator

from app.db.session import get_db
from app.models.resume import TailoredResume
from app.schemas.tailor import TailorRequest, TailoredResumeResponse, SectionEditRequest
from app.schemas.resume import ParsedResume
from app.schemas.job import ScoreDetails
from app.services.tailor_service import (
    stream_tailored_resume,
    save_tailored_resume,
    get_resume_and_job,
)

router = APIRouter()


def _get_session_id(x_session_id: str = Header(default=None)) -> str:
    return x_session_id or str(uuid.uuid4())


@router.post("/stream")
async def tailor_stream(
    body: TailorRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Stream the tailored resume section by section via SSE.

    Event types:
      {"type": "token",    "content": "..."}           — raw token for live rendering
      {"type": "sections", "sections": {...}}           — full validated ParsedResume JSON
      {"type": "saved",    "tailored_resume_id": "..."}— DB record created
      {"type": "error",    "message": "..."}            — something went wrong
    """
    resume, job = await get_resume_and_job(body.resume_id, body.job_id, db)

    async def event_stream() -> AsyncGenerator[str, None]:
        final_sections = None

        async for event in stream_tailored_resume(resume, job):
            yield event

            # Capture sections payload so we can save after streaming
            try:
                data = json.loads(event.removeprefix("data: ").strip())
                if data.get("type") == "sections":
                    final_sections = data["sections"]
            except Exception:
                pass

        if final_sections:
            tailored = await save_tailored_resume(
                resume_id=resume.id,
                job_id=job.id,
                sections=final_sections,
                score=job.parsed_requirements.get("overall") if job.parsed_requirements else None,
                score_details=None,
                db=db,
            )
            yield f"data: {json.dumps({'type': 'saved', 'tailored_resume_id': str(tailored.id)})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/{tailored_resume_id}", response_model=TailoredResumeResponse)
async def get_tailored_resume(
    tailored_resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(TailoredResume).where(TailoredResume.id == tailored_resume_id)
    )
    tailored = result.scalar_one_or_none()
    if not tailored:
        raise HTTPException(status_code=404, detail="Tailored resume not found.")

    return TailoredResumeResponse(
        id=tailored.id,
        resume_id=tailored.resume_id,
        job_id=tailored.job_id,
        sections=ParsedResume(**tailored.sections),
        score=tailored.score,
        score_details=ScoreDetails(**tailored.score_details) if tailored.score_details else None,
        version=tailored.version,
    )
