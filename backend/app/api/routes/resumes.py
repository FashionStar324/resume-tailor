import uuid
from fastapi import APIRouter, Depends, File, UploadFile, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeUploadResponse, ParsedResume
from app.services.parser import extract_text
from app.services.resume_service import parse_and_store_resume

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB


def _get_session_id(x_session_id: str = Header(default=None)) -> str:
    if x_session_id:
        return x_session_id
    return str(uuid.uuid4())


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    session_id: str = Depends(_get_session_id),
    db: AsyncSession = Depends(get_db),
):
    if file.size and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail="File too large. Maximum size is 5 MB.")

    raw_text = await extract_text(file)
    resume = await parse_and_store_resume(raw_text, file.filename or "resume", session_id, db)

    return ResumeUploadResponse(
        id=resume.id,
        filename=resume.filename,
        parsed_sections=ParsedResume(**resume.parsed_sections),
    )


@router.get("/{resume_id}", response_model=ResumeUploadResponse)
async def get_resume(
    resume_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    return ResumeUploadResponse(
        id=resume.id,
        filename=resume.filename,
        parsed_sections=ParsedResume(**resume.parsed_sections),
    )
