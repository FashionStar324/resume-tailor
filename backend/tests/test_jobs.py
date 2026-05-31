"""
Manual test — run after uploading a resume to get a resume_id:

    curl -X POST http://localhost:8000/api/jobs/score \
      -H "Content-Type: application/json" \
      -H "X-Session-Id: test-session-001" \
      -d '{
        "resume_id": "<uuid-from-step-3>",
        "job_description": "We are looking for a senior software engineer..."
      }'

Expected response shape:
{
  "job_id": "<uuid>",
  "resume_id": "<uuid>",
  "parsed_requirements": {
    "title": "Senior Software Engineer",
    "company": "...",
    "required_skills": ["Python", "AWS", ...],
    "preferred_skills": ["Kubernetes", ...],
    "experience_years": 5,
    "key_responsibilities": [...],
    "seniority_level": "senior"
  },
  "score": {
    "keyword_match": 0.72,
    "experience_alignment": 0.80,
    "impact_language": 0.65,
    "overall": 0.73,
    "strengths": ["Strong Python background", ...],
    "missing": ["Kubernetes", "Go"],
    "suggestions": ["Add metrics to your AWS bullet points", ...]
  }
}
"""
