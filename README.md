# Resume Tailer

AI-powered resume tailoring with section-level memory.

---

## Why I built this

In 2023 I built a resume tailoring system professionally. The architecture at the time was the obvious one: take the full resume, take the job description, send both to the model, get a rewritten resume back.

It worked. But it had a flaw that only became clear after watching real users interact with it.

When someone wanted to tweak a single bullet — say, reframe one role description to better emphasize leadership — we had to resend the entire document. The model had no memory of the previous tailoring session. Every edit was a cold start. Users would adjust one thing and find that unrelated sections had quietly shifted. Trust eroded.

There was a second, subtler problem. A bullet point under **"Staff Engineer at Stripe"** means something categorically different from the same bullet under **"Summer Intern at a Startup."** Full-document resends collapse that hierarchy. The model optimizes globally instead of understanding where in the document it is and what the surrounding context implies about the candidate.

This is a rebuild of that system — same domain, better architecture — using what I learned from shipping the original.

---

## What I did differently

The tailored resume is stored as **structured JSON**, not a blob of text:

```json
{
  "contact": { "name": "...", "email": "...", ... },
  "summary": "...",
  "experience": [
    { "company": "Stripe", "role": "Staff Engineer", "bullets": [...] },
    { "company": "Startup", "role": "Intern", "bullets": [...] }
  ],
  "skills": { "languages": [...], "frameworks": [...], "tools": [...] },
  "projects": [...],
  "education": [...]
}
```

When a user edits a section, only that section is sent to the model — but the **full resume JSON is included as read-only context**. The model knows it is rewriting the Stripe role, not the intern role. It knows what comes before and after. It cannot accidentally drift other sections because the prompt only asks for one section back.

Each edit is stored as a diff: original content, user note, revised content. Any section can be reverted to any prior state. The document builds incrementally rather than being regenerated wholesale on every change.

---

## Architecture

```
frontend/   Next.js 15 (App Router), TypeScript, Tailwind CSS
backend/    FastAPI, Python 3.12, SQLAlchemy async, Alembic
database/   PostgreSQL 16 + pgvector
ai/         OpenAI GPT-4o (parse, score, tailor, edit)
cache/      Redis (rate limiting)
pdf/        WeasyPrint (server-side PDF generation)
```

### Why pgvector over Pinecone

At this scale, running a separate vector database is operational overhead with no practical benefit. pgvector inside Postgres means one service, one connection pool, and transactional consistency between the resume text and its embedding. The similarity search runs in the same query as everything else.

### Why structured JSON over raw text

Raw text storage makes section-level diffing, partial edits, version history, and PDF generation from a template all significantly harder. The JSON schema is the load-bearing piece of the architecture — everything else is built on top of it.

### Why FastAPI over Node for the backend

The AI calls are I/O-bound and async throughout. Python gives first-class access to `pdfplumber`, `python-docx`, and the OpenAI SDK. There is no FFI overhead and no impedance mismatch between the model output and the application data structures.

---

## Data model

```
resumes          — raw text, parsed JSON sections, embedding
jobs             — raw description, parsed requirements, embedding
tailored_resumes — sections JSON, score, score breakdown, version
section_edits    — section name, user note, original, revised (per-edit history)
```

The `section_edits` table is what enables revert. Every edit writes a row. Reverting applies the stored `original_content` back to `tailored_resumes.sections` and patches the section in place.

---

## Scoring

Match score is structured across three dimensions:

| Dimension | Weight | What it measures |
|---|---|---|
| `keyword_match` | 40% | Required skills present in resume |
| `experience_alignment` | 35% | Seniority, domain, years of experience |
| `impact_language` | 25% | Metrics, scale, outcomes in bullets |

The `missing` array from the score drives what the tailoring step focuses on — it is the bridge between diagnosis and fix.

---

## API

| Method | Path | Description |
|---|---|---|
| `POST` | `/api/resumes/upload` | Upload PDF or DOCX, returns parsed sections |
| `GET` | `/api/resumes/{id}` | Fetch a parsed resume |
| `POST` | `/api/jobs/score` | Score a resume against a job description |
| `POST` | `/api/tailor/stream` | Tailor a resume, SSE stream |
| `GET` | `/api/tailor/{id}` | Fetch a tailored resume |
| `GET` | `/api/tailor/{id}/pdf` | Download as ATS-optimized PDF |
| `POST` | `/api/tailor/edit` | Revise one section with a note |
| `GET` | `/api/tailor/{id}/history` | Full edit log, newest first |
| `POST` | `/api/tailor/edit/{edit_id}/revert` | Restore a section to before a specific edit |

---

## Local setup

**Prerequisites:** Docker, Python 3.12, Node 20

```bash
# 1. Start Postgres + Redis
docker compose up -d

# 2. Backend
cd backend
cp .env.example .env                   # fill in OPENAI_API_KEY

# On Debian/Ubuntu, install the venv package first if needed:
# sudo apt install python3.12-venv -y
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload          # runs on http://localhost:8000

# 3. Frontend (new terminal)
cd frontend
cp .env.local.example .env.local
npm install
npm run dev                            # runs on http://localhost:3000
```

Open [http://localhost:3000](http://localhost:3000).

> **Note:** Keep the `.venv` active whenever running backend commands. You will see `(.venv)` in your prompt when it is active.

---

## Usage

1. **Upload** a resume (PDF or DOCX)
2. **Paste** a job description and click **Analyze Match**
3. Review the structured score — keyword gaps, strengths, suggestions
4. Click **Tailor My Resume** — streams the rewrite in real time
5. In the editor, hover any section and click **Edit**
6. Type a plain-English instruction: *"Emphasize the Kubernetes migration I led"*
7. Only that section is revised — everything else stays
8. Use **Edit History** to revert any section to a previous state
9. **Download PDF** — clean, ATS-optimized, named after the candidate

---

## Tradeoffs

**PDF fidelity vs. ATS optimization.** The output PDF uses a fixed template, not a replica of the uploaded design. ATS systems parse structured text; decorative layouts often confuse them. The template is a deliberate choice, not a limitation.

**No fine-tuning.** Prompt engineering with GPT-4o is sufficient at this scale. Fine-tuning would require labeled data and retraining cycles that do not make sense for a personal tool.

**Session-based auth.** No account system in v1. Resumes are scoped to a session ID stored in a cookie. This ships faster and covers the core use case. Auth is a v2 concern.

**One GPT-4o call for full tailoring, one call per section edit.** Section edits are small and fast. The full tailoring call is larger but streams — the user sees output within a second or two. Splitting tailoring into per-section calls would be more granular but slower and more expensive for the first pass.

**Embeddings stored but not yet used for search.** The schema includes a `vector(1536)` column on both `resumes` and `jobs` for future similarity search — e.g. surfacing the most relevant past resume for a new job description. In v1, scoring and tailoring go entirely through GPT-4o structured output, so embeddings are not computed on insert. This is a deliberate deferral, not an oversight.

**Null bytes stripped from PDF text.** Some PDFs embed null bytes (`\x00`) in extracted text — common in phone numbers formatted with certain font encodings. PostgreSQL rejects null bytes in `TEXT` columns, so they are stripped at extraction time. The parsed content is unaffected.

---

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.12 |
| Database | PostgreSQL 16 + pgvector |
| AI | OpenAI GPT-4o |
| PDF parse | pdfplumber, python-docx |
| PDF export | WeasyPrint |
| Cache | Redis |
| Infra | Docker Compose |

---

## Troubleshooting

**`python3 -m venv` fails with `ensurepip` error**
```bash
sudo apt install python3.12-venv -y
```

**`alembic upgrade head` fails with connection refused**
Docker isn't running yet. Run `docker compose up -d` first and wait a few seconds for Postgres to be ready.

**CORS error in the browser**
The backend must be running at `http://localhost:8000` before the frontend can make requests. Check that `uvicorn` started successfully and `http://localhost:8000/health` returns `{"status": "ok"}`.

**PDF upload fails with 422**
The PDF may be image-based (scanned). `pdfplumber` can only extract text from PDFs with actual text layers. Use a text-based PDF or a DOCX instead.
