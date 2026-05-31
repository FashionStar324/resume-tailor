import json
import uuid
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import AsyncGenerator

from app.db.session import get_db
from app.models.resume import TailoredResume
from app.schemas.tailor import (
    TailorRequest,
    TailoredResumeResponse,
    SectionEditRequest,
    SectionEditResponse,
    EditHistoryEntry,
)
from app.schemas.resume import ParsedResume
from app.schemas.job import ScoreDetails
from app.services.tailor_service import (
    stream_tailored_resume,
    save_tailored_resume,
    get_resume_and_job,
)
from app.services.section_edit_service import (
    edit_section,
    get_edit_history,
    revert_section_edit,
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


@router.post("/edit", response_model=SectionEditResponse)
async def edit_resume_section(
    body: SectionEditRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Revise a single section of a tailored resume.

    section_name format:
      "summary"       — the summary string
      "skills"        — the full skills object
      "experience.0"  — first experience entry
      "projects.1"    — second project entry
      "education.0"   — first education entry
    """
    edit, revised = await edit_section(
        tailored_resume_id=body.tailored_resume_id,
        section_name=body.section_name,
        user_note=body.user_note,
        db=db,
    )
    return SectionEditResponse(
        section_name=edit.section_name,
        revised_content=revised,
        edit_id=edit.id,
    )


@router.get("/{tailored_resume_id}/history", response_model=list[EditHistoryEntry])
async def get_section_edit_history(
    tailored_resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    edits = await get_edit_history(tailored_resume_id, db)
    return [
        EditHistoryEntry(
            id=e.id,
            section_name=e.section_name,
            user_note=e.user_note,
            original_content=e.original_content,
            revised_content=e.revised_content,
            created_at=e.created_at.isoformat(),
        )
        for e in edits
    ]


@router.post("/edit/{edit_id}/revert", response_model=SectionEditResponse)
async def revert_edit(
    edit_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    edit, original = await revert_section_edit(edit_id, db)
    return SectionEditResponse(
        section_name=edit.section_name,
        revised_content=original,
        edit_id=edit.id,
    )
