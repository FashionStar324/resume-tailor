from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import resumes, jobs, tailor, health

app = FastAPI(
    title="Resume Tailer API",
    description="AI-powered resume tailoring with section-level memory",
    version="0.1.0",
)

CORS_ORIGINS = list(set(settings.CORS_ORIGINS + ["http://localhost:3000", "http://127.0.0.1:3000"]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(resumes.router, prefix="/api/resumes", tags=["resumes"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["jobs"])
app.include_router(tailor.router, prefix="/api/tailor", tags=["tailor"])
