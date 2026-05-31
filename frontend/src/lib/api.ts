import type {
  ResumeUploadResponse,
  JobScoreResponse,
  TailoredResumeResponse,
  SectionEditResponse,
  EditHistoryEntry,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function request<T>(
  path: string,
  init: RequestInit,
  sessionId: string
): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "X-Session-Id": sessionId,
      ...init.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed: ${res.status}`);
  }
  return res.json();
}

export async function uploadResume(
  file: File,
  sessionId: string
): Promise<ResumeUploadResponse> {
  const form = new FormData();
  form.append("file", file);
  return request("/api/resumes/upload", { method: "POST", body: form }, sessionId);
}

export async function scoreJob(
  resumeId: string,
  jobDescription: string,
  sessionId: string
): Promise<JobScoreResponse> {
  return request(
    "/api/jobs/score",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_id: resumeId, job_description: jobDescription }),
    },
    sessionId
  );
}

export async function getTailoredResume(
  tailoredResumeId: string,
  sessionId: string
): Promise<TailoredResumeResponse> {
  return request(`/api/tailor/${tailoredResumeId}`, { method: "GET" }, sessionId);
}

export async function editSection(
  tailoredResumeId: string,
  sectionName: string,
  userNote: string,
  sessionId: string
): Promise<SectionEditResponse> {
  return request(
    "/api/tailor/edit",
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tailored_resume_id: tailoredResumeId,
        section_name: sectionName,
        user_note: userNote,
      }),
    },
    sessionId
  );
}

export async function getEditHistory(
  tailoredResumeId: string,
  sessionId: string
): Promise<EditHistoryEntry[]> {
  return request(`/api/tailor/${tailoredResumeId}/history`, { method: "GET" }, sessionId);
}

export async function revertEdit(
  editId: string,
  sessionId: string
): Promise<SectionEditResponse> {
  return request(`/api/tailor/edit/${editId}/revert`, { method: "POST" }, sessionId);
}

export function streamTailor(
  resumeId: string,
  jobId: string,
  sessionId: string,
  onToken: (token: string) => void,
  onSections: (sections: unknown) => void,
  onSaved: (id: string) => void,
  onError: (msg: string) => void
): () => void {
  let cancelled = false;

  (async () => {
    const res = await fetch(`${BASE}/api/tailor/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Session-Id": sessionId,
      },
      body: JSON.stringify({ resume_id: resumeId, job_id: jobId }),
    });

    if (!res.ok || !res.body) {
      onError(`Stream failed: ${res.status}`);
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    while (!cancelled) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() ?? "";

      for (const line of lines) {
        if (!line.startsWith("data: ")) continue;
        try {
          const event = JSON.parse(line.slice(6));
          if (event.type === "token") onToken(event.content);
          else if (event.type === "sections") onSections(event.sections);
          else if (event.type === "saved") onSaved(event.tailored_resume_id);
          else if (event.type === "error") onError(event.message);
        } catch {
          // malformed SSE line — skip
        }
      }
    }
  })().catch((e) => onError(String(e)));

  return () => {
    cancelled = true;
  };
}
