import json
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.resume import Resume
from app.schemas.resume import ParsedResume
from app.services.openai_client import chat_json, get_embedding

_PARSE_SYSTEM = """You are a resume parser. Extract all information from the resume text and return it as JSON.

Return exactly this structure (omit optional fields if not present, never invent data):
{
  "contact": {
    "name": "string",
    "email": "string or null",
    "phone": "string or null",
    "location": "string or null",
    "linkedin": "string or null",
    "github": "string or null"
  },
  "summary": "string or null",
  "experience": [
    {
      "company": "string",
      "role": "string",
      "location": "string or null",
      "start_date": "string or null",
      "end_date": "string or null (use 'Present' if current)",
      "bullets": ["string"]
    }
  ],
  "education": [
    {
      "institution": "string",
      "degree": "string or null",
      "field": "string or null",
      "graduation_date": "string or null",
      "gpa": "string or null"
    }
  ],
  "skills": {
    "languages": ["string"],
    "frameworks": ["string"],
    "tools": ["string"],
    "other": ["string"]
  },
  "projects": [
    {
      "name": "string",
      "description": "string or null",
      "bullets": ["string"],
      "url": "string or null",
      "technologies": ["string"]
    }
  ],
  "certifications": ["string"]
}

Rules:
- Preserve the candidate's original wording in bullets — do not paraphrase.
- If a skill category is ambiguous, use your best judgement (e.g. Python → languages, React → frameworks, Git → tools).
- Dates should be kept as-is from the resume (e.g. "Jan 2022", "2020–2023").
"""


async def parse_and_store_resume(
    raw_text: str,
    filename: str,
    session_id: str,
    db: AsyncSession,
) -> Resume:
    parsed_dict = await chat_json(_PARSE_SYSTEM, raw_text)

    # Validate against schema (raises ValidationError on bad output)
    parsed = ParsedResume(**parsed_dict)

    resume = Resume(
        id=uuid.uuid4(),
        session_id=session_id,
        filename=filename,
        raw_text=raw_text,
        parsed_sections=parsed.model_dump(),
    )
    db.add(resume)
    await db.commit()
    await db.refresh(resume)
    return resume
