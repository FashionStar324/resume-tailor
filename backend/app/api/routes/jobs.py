import uuid
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.job import JobScoreRequest, JobScoreResponse
from app.services.job_service import create_job_and_score

router = APIRouter()


def _get_session_id(x_session_id: str = Header(default=None)) -> str:
    if x_session_id:
        return x_session_id
    return str(uuid.uuid4())


@router.post("/score", response_model=JobScoreResponse)
async def score_job(
    body: JobScoreRequest,
    session_id: str = Depends(_get_session_id),
    db: AsyncSession = Depends(get_db),
):
    job, resume, parsed_requirements, score = await create_job_and_score(
        raw_description=body.job_description,
        resume_id=body.resume_id,
        session_id=session_id,
        db=db,
    )

    return JobScoreResponse(
        job_id=job.id,
        resume_id=resume.id,
        parsed_requirements=parsed_requirements,
        score=score,
    )
