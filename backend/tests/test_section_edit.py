"""
Manual tests for section-level editing.

1. Edit the summary:
    curl -X POST http://localhost:8000/api/tailor/edit \
      -H "Content-Type: application/json" \
      -d '{
        "tailored_resume_id": "<uuid>",
        "section_name": "summary",
        "user_note": "Make it more focused on backend engineering and distributed systems."
      }'

2. Edit a specific experience entry (index 0 = most recent job):
    curl -X POST http://localhost:8000/api/tailor/edit \
      -H "Content-Type: application/json" \
      -d '{
        "tailored_resume_id": "<uuid>",
        "section_name": "experience.0",
        "user_note": "Emphasize leadership and mention the Kubernetes migration I led."
      }'

3. Edit skills:
    curl -X POST http://localhost:8000/api/tailor/edit \
      -H "Content-Type: application/json" \
      -d '{
        "tailored_resume_id": "<uuid>",
        "section_name": "skills",
        "user_note": "Move Rust to languages and add Terraform to tools."
      }'

4. View full edit history (newest first):
    curl http://localhost:8000/api/tailor/<tailored_resume_id>/history

5. Revert a specific edit:
    curl -X POST http://localhost:8000/api/tailor/edit/<edit_id>/revert

Response shape for edit/revert:
{
  "section_name": "experience.0",
  "revised_content": { "company": "...", "role": "...", "bullets": [...] },
  "edit_id": "<uuid>"
}
"""
