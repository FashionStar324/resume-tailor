import uuid
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.resume import TailoredResume, SectionEdit, Job
from app.services.openai_client import chat_json

_SECTION_EDIT_SYSTEM = """You are an expert resume editor performing a targeted section revision.

You will receive:
- The FULL resume (for context — do not modify anything outside the target section)
- The JOB REQUIREMENTS the resume is tailored for
- The SPECIFIC SECTION to revise
- A USER NOTE describing what to change

Your task: rewrite ONLY the target section and return it as JSON in this envelope:
  {"section": <revised section value>}

The value type must match the input:
- summary       → string
- skills        → object with keys: languages, frameworks, tools, other (each a list of strings)
- experience.N  → object with keys: company, role, location, start_date, end_date, bullets
- projects.N    → object with keys: name, description, bullets, url, technologies
- education.N   → object with keys: institution, degree, field, graduation_date, gpa

Rules — follow these strictly:
1. NEVER modify any section other than the target.
2. NEVER invent credentials, companies, roles, or dates.
3. PRESERVE company, role, title, location, and all dates exactly.
4. Honor the user's note — it is the primary instruction.
5. Use job keywords and language where they accurately reflect the candidate's work.
6. Improve impact: add metrics, scale, and outcomes where the original is vague,
   but only if reasonably inferable from the existing content.
7. Return only the JSON envelope — no explanation, no markdown.
"""


def _parse_section_key(section_name: str) -> tuple[str, int | None]:
    """Split 'experience.0' → ('experience', 0), 'summary' → ('summary', None)."""
    parts = section_name.split(".", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0], int(parts[1])
    return section_name, None


def _get_current_section(sections: dict, section_name: str):
    key, index = _parse_section_key(section_name)
    if key not in sections:
        raise HTTPException(status_code=400, detail=f"Unknown section: '{key}'.")
    value = sections[key]
    if index is not None:
        if not isinstance(value, list) or index >= len(value):
            raise HTTPException(status_code=400, detail=f"Index {index} out of range for section '{key}'.")
        return value[index]
    return value


def _apply_revised_section(sections: dict, section_name: str, revised) -> dict:
    """Return a new sections dict with only the target section replaced."""
    import copy
    updated = copy.deepcopy(sections)
    key, index = _parse_section_key(section_name)
    if index is not None:
        updated[key][index] = revised
    else:
        updated[key] = revised
    return updated


async def edit_section(
    tailored_resume_id: uuid.UUID,
    section_name: str,
    user_note: str,
    db: AsyncSession,
) -> tuple[SectionEdit, dict]:
    # Load tailored resume
    tr_result = await db.execute(
        select(TailoredResume).where(TailoredResume.id == tailored_resume_id)
    )
    tailored = tr_result.scalar_one_or_none()
    if not tailored:
        raise HTTPException(status_code=404, detail="Tailored resume not found.")

    # Load job for requirements context
    job_result = await db.execute(select(Job).where(Job.id == tailored.job_id))
    job = job_result.scalar_one_or_none()

    current_section = _get_current_section(tailored.sections, section_name)

    user_prompt = f"""FULL RESUME (context only — do not modify):
{json.dumps(tailored.sections, indent=2)}

JOB REQUIREMENTS:
{json.dumps(job.parsed_requirements if job else {}, indent=2)}

TARGET SECTION: {section_name}
CURRENT VALUE:
{json.dumps(current_section, indent=2)}

USER NOTE: {user_note}
"""

    result = await chat_json(_SECTION_EDIT_SYSTEM, user_prompt)

    if "section" not in result:
        raise HTTPException(status_code=502, detail="Model returned unexpected format.")

    revised = result["section"]
    updated_sections = _apply_revised_section(tailored.sections, section_name, revised)

    # Persist edit record
    edit = SectionEdit(
        id=uuid.uuid4(),
        tailored_resume_id=tailored_resume_id,
        section_name=section_name,
        user_note=user_note,
        original_content=json.dumps(current_section),
        revised_content=json.dumps(revised),
    )
    db.add(edit)

    # Update the tailored resume sections in-place
    # Use a new dict assignment so SQLAlchemy detects the change on JSONB
    tailored.sections = updated_sections
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(tailored, "sections")

    await db.commit()
    await db.refresh(edit)

    return edit, revised


async def get_edit_history(
    tailored_resume_id: uuid.UUID,
    db: AsyncSession,
) -> list[SectionEdit]:
    result = await db.execute(
        select(SectionEdit)
        .where(SectionEdit.tailored_resume_id == tailored_resume_id)
        .order_by(SectionEdit.created_at.desc())
    )
    return result.scalars().all()


async def revert_section_edit(
    edit_id: uuid.UUID,
    db: AsyncSession,
) -> tuple[SectionEdit, dict]:
    """Revert a section to its state before the given edit was applied."""
    edit_result = await db.execute(select(SectionEdit).where(SectionEdit.id == edit_id))
    edit = edit_result.scalar_one_or_none()
    if not edit:
        raise HTTPException(status_code=404, detail="Edit not found.")

    tr_result = await db.execute(
        select(TailoredResume).where(TailoredResume.id == edit.tailored_resume_id)
    )
    tailored = tr_result.scalar_one_or_none()

    original = json.loads(edit.original_content)
    updated_sections = _apply_revised_section(tailored.sections, edit.section_name, original)

    tailored.sections = updated_sections
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(tailored, "sections")

    await db.commit()
    return edit, original
