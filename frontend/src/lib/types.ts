export interface ContactInfo {
  name: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin?: string;
  github?: string;
}

export interface ExperienceEntry {
  company: string;
  role: string;
  location?: string;
  start_date?: string;
  end_date?: string;
  bullets: string[];
}

export interface EducationEntry {
  institution: string;
  degree?: string;
  field?: string;
  graduation_date?: string;
  gpa?: string;
}

export interface ProjectEntry {
  name: string;
  description?: string;
  bullets: string[];
  url?: string;
  technologies: string[];
}

export interface SkillsSection {
  languages: string[];
  frameworks: string[];
  tools: string[];
  other: string[];
}

export interface ParsedResume {
  contact: ContactInfo;
  summary?: string;
  experience: ExperienceEntry[];
  education: EducationEntry[];
  skills: SkillsSection;
  projects: ProjectEntry[];
  certifications: string[];
}

export interface ResumeUploadResponse {
  id: string;
  filename: string;
  parsed_sections: ParsedResume;
}

export interface ParsedRequirements {
  title?: string;
  company?: string;
  required_skills: string[];
  preferred_skills: string[];
  experience_years?: number;
  key_responsibilities: string[];
  seniority_level?: string;
}

export interface ScoreDetails {
  keyword_match: number;
  experience_alignment: number;
  impact_language: number;
  overall: number;
  strengths: string[];
  missing: string[];
  suggestions: string[];
}

export interface JobScoreResponse {
  job_id: string;
  resume_id: string;
  parsed_requirements: ParsedRequirements;
  score: ScoreDetails;
}

export interface TailoredResumeResponse {
  id: string;
  resume_id: string;
  job_id: string;
  sections: ParsedResume;
  score?: number;
  version: number;
}

export interface SectionEditResponse {
  section_name: string;
  revised_content: unknown;
  edit_id: string;
}

export interface EditHistoryEntry {
  id: string;
  section_name: string;
  user_note?: string;
  original_content: string;
  revised_content: string;
  created_at: string;
}
