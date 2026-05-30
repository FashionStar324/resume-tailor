"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-05-30

"""
from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "resumes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", sa.String(64), nullable=False, index=True),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("parsed_sections", JSONB, nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", sa.String(64), nullable=False, index=True),
        sa.Column("raw_description", sa.Text, nullable=False),
        sa.Column("parsed_requirements", JSONB, nullable=True),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "tailored_resumes",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("resume_id", UUID(as_uuid=True), sa.ForeignKey("resumes.id"), nullable=False),
        sa.Column("job_id", UUID(as_uuid=True), sa.ForeignKey("jobs.id"), nullable=False),
        sa.Column("sections", JSONB, nullable=False),
        sa.Column("score", sa.Float, nullable=True),
        sa.Column("score_details", JSONB, nullable=True),
        sa.Column("version", sa.Integer, default=1, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "section_edits",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tailored_resume_id",
            UUID(as_uuid=True),
            sa.ForeignKey("tailored_resumes.id"),
            nullable=False,
        ),
        sa.Column("section_name", sa.String(64), nullable=False),
        sa.Column("user_note", sa.Text, nullable=True),
        sa.Column("original_content", sa.Text, nullable=False),
        sa.Column("revised_content", sa.Text, nullable=False),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now(), nullable=False),
    )

    op.create_index("ix_tailored_resumes_resume_id", "tailored_resumes", ["resume_id"])
    op.create_index("ix_tailored_resumes_job_id", "tailored_resumes", ["job_id"])
    op.create_index("ix_section_edits_tailored_resume_id", "section_edits", ["tailored_resume_id"])


def downgrade() -> None:
    op.drop_table("section_edits")
    op.drop_table("tailored_resumes")
    op.drop_table("jobs")
    op.drop_table("resumes")
    op.execute("DROP EXTENSION IF EXISTS vector")
