from pydantic import BaseModel
from typing import Optional
import uuid

from app.schemas.resume import ParsedResume
from app.schemas.job import ScoreDetails


class TailorRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID


class TailoredResumeResponse(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    job_id: uuid.UUID
    sections: ParsedResume
    score: Optional[float] = None
    score_details: Optional[ScoreDetails] = None
    version: int

    class Config:
        from_attributes = True


class SectionEditRequest(BaseModel):
    tailored_resume_id: uuid.UUID
    # Format: "summary" | "skills" | "experience.0" | "projects.1" | "education.0"
    section_name: str
    user_note: str


class SectionEditResponse(BaseModel):
    section_name: str
    revised_content: dict | str | list  # matches the type of the edited section
    edit_id: uuid.UUID


class EditHistoryEntry(BaseModel):
    id: uuid.UUID
    section_name: str
    user_note: Optional[str]
    original_content: str
    revised_content: str
    created_at: str

    class Config:
        from_attributes = True
