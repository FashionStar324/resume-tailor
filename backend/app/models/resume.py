import uuid
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, ForeignKey, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector

from app.db.session import Base


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    raw_text: Mapped[str] = mapped_column(Text)
    parsed_sections: Mapped[dict] = mapped_column(JSONB, nullable=True)
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tailored_resumes: Mapped[list["TailoredResume"]] = relationship(back_populates="resume")


class Job(Base):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id: Mapped[str] = mapped_column(String(64), index=True)
    raw_description: Mapped[str] = mapped_column(Text)
    parsed_requirements: Mapped[dict] = mapped_column(JSONB, nullable=True)
    embedding: Mapped[list] = mapped_column(Vector(1536), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tailored_resumes: Mapped[list["TailoredResume"]] = relationship(back_populates="job")


class TailoredResume(Base):
    __tablename__ = "tailored_resumes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resumes.id"))
    job_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("jobs.id"))
    sections: Mapped[dict] = mapped_column(JSONB)
    score: Mapped[float] = mapped_column(Float, nullable=True)
    score_details: Mapped[dict] = mapped_column(JSONB, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    resume: Mapped["Resume"] = relationship(back_populates="tailored_resumes")
    job: Mapped["Job"] = relationship(back_populates="tailored_resumes")
    section_edits: Mapped[list["SectionEdit"]] = relationship(back_populates="tailored_resume")


class SectionEdit(Base):
    __tablename__ = "section_edits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tailored_resume_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("tailored_resumes.id"))
    section_name: Mapped[str] = mapped_column(String(64))
    user_note: Mapped[str] = mapped_column(Text, nullable=True)
    original_content: Mapped[str] = mapped_column(Text)
    revised_content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    tailored_resume: Mapped["TailoredResume"] = relationship(back_populates="section_edits")
