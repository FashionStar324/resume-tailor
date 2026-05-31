"""
Manual test — run with:
    curl -X POST http://localhost:8000/api/resumes/upload \
      -H "X-Session-Id: test-session-001" \
      -F "file=@/path/to/your_resume.pdf"

Expected response shape:
{
  "id": "<uuid>",
  "filename": "your_resume.pdf",
  "parsed_sections": {
    "contact": { "name": "...", ... },
    "summary": "...",
    "experience": [...],
    "education": [...],
    "skills": { ... },
    "projects": [...],
    "certifications": [...]
  }
}
"""
