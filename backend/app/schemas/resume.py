from pydantic import BaseModel
from typing import Optional
import uuid


class ContactInfo(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None


class ExperienceEntry(BaseModel):
    company: str
    role: str
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    bullets: list[str] = []


class EducationEntry(BaseModel):
    institution: str
    degree: Optional[str] = None
    field: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None


class ProjectEntry(BaseModel):
    name: str
    description: Optional[str] = None
    bullets: list[str] = []
    url: Optional[str] = None
    technologies: list[str] = []


class SkillsSection(BaseModel):
    languages: list[str] = []
    frameworks: list[str] = []
    tools: list[str] = []
    other: list[str] = []


class ParsedResume(BaseModel):
    contact: ContactInfo
    summary: Optional[str] = None
    experience: list[ExperienceEntry] = []
    education: list[EducationEntry] = []
    skills: SkillsSection = SkillsSection()
    projects: list[ProjectEntry] = []
    certifications: list[str] = []


class ResumeUploadResponse(BaseModel):
    id: uuid.UUID
    filename: str
    parsed_sections: ParsedResume

    class Config:
        from_attributes = True
