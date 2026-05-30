# Resume Tailer

AI-powered resume tailoring with section-level memory.

## Why I built this

In 2023 I built a resume tailoring system professionally. The approach at the time was simple: take the full resume, take the job description, send both to the model, get a rewritten resume back. It worked, but it had a fundamental flaw.

When a user wanted to tweak a single bullet point — say, a role description under one specific job — we had to resend the entire document. The model had no memory of the previous tailoring session. Every edit was a cold start. Users got frustrated because small changes caused unintended rewrites elsewhere in the document.

The other problem: a bullet point under "Staff Engineer at Stripe" means something categorically different from the same bullet under "Summer Intern at a Startup." Full-document resends lose that hierarchy. The model optimizes the document globally instead of understanding the positional context of each section.

## What I did differently

This version is built around **section-level memory**. The tailored resume is stored as a structured JSON document — not a blob of text. When a user wants to revise one section, only that section is sent to the model, but the full resume JSON is included as context. The model knows where it is in the document, what came before, and what the job requires.

Each edit is stored as a diff — original content, user note, revised content. You can revert any section to a previous state. The document builds up incrementally, section by section, rather than being regenerated wholesale each time.

## Architecture

```
frontend/          Next.js 15, TypeScript, Tailwind, shadcn/ui
backend/           FastAPI, SQLAlchemy async, Alembic
                   PostgreSQL + pgvector (single DB, no separate vector store)
                   OpenAI GPT-4o for parsing, scoring, and tailoring
```

**Why pgvector over Pinecone:** At the scale of a personal tool, running a separate vector database is operational overhead with no benefit. pgvector inside Postgres means one fewer service to run, one fewer connection to manage, and transactional consistency between the resume text and its embedding.

**Why FastAPI over Node for the backend:** The AI calls are I/O-bound and async throughout. Python gives direct access to pdfplumber and python-docx without FFI overhead. The OpenAI SDK is first-class in Python.

**Why structured section JSON instead of raw text:** Enables section-level diffing, partial edits, version history, and clean PDF generation from a template. Raw text storage makes all of these harder.

## Tradeoffs I made

- **PDF fidelity vs. ATS optimization:** The output PDF uses a clean fixed template, not a replica of the uploaded design. This is intentional — ATS systems parse structured text, not decorative layouts.
- **No fine-tuning:** Prompt engineering with GPT-4o is sufficient at this scale. Fine-tuning would require labeled data and retraining cycles that don't make sense for a personal tool.
- **Session-based auth for v1:** No account system in the initial version. Resumes are scoped to a session ID stored in a cookie. Auth is a v2 concern.

## Local setup

```bash
# Start Postgres + Redis
docker compose up -d

# Backend
cd backend
cp .env.example .env   # add your OPENAI_API_KEY
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Features

- Upload a resume (PDF or DOCX)
- Paste a job description and get a structured match score
- Tailor the full resume to the job in one click
- Edit any section with a plain-English note — only that section is revised
- Download the final result as a clean ATS-optimized PDF
- Full edit history with per-section revert

## Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL 16 + pgvector |
| AI | OpenAI GPT-4o |
| PDF parse | pdfplumber, python-docx |
| PDF export | WeasyPrint |
| Cache | Redis |
| Infra | Docker Compose |
