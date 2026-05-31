"""
Manual test — stream a tailored resume:

    curl -X POST http://localhost:8000/api/tailor/stream \
      -H "Content-Type: application/json" \
      -H "X-Session-Id: test-session-001" \
      -N \
      -d '{"resume_id": "<uuid>", "job_id": "<uuid>"}'

The -N flag disables curl buffering so you see SSE events in real time.

Event sequence:
  data: {"type": "token", "content": "{"}
  data: {"type": "token", "content": "\\n  \\"contact\\""}
  ...
  data: {"type": "sections", "sections": { ...full ParsedResume JSON... }}
  data: {"type": "saved", "tailored_resume_id": "<uuid>"}

Fetch the saved result later:
    curl http://localhost:8000/api/tailor/<tailored_resume_id>
"""
