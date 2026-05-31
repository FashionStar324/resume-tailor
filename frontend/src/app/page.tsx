"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useSession } from "@/hooks/useSession";
import { ResumeDropzone } from "@/components/upload/ResumeDropzone";
import { JobDescriptionInput } from "@/components/upload/JobDescriptionInput";
import { ScoreCard } from "@/components/score/ScoreCard";
import { uploadResume, scoreJob, streamTailor } from "@/lib/api";
import type { JobScoreResponse } from "@/lib/types";
import { Loader2 } from "lucide-react";

type Step = "upload" | "analyzing" | "scored" | "tailoring";

export default function Home() {
  const sessionId = useSession();

  const [file, setFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [step, setStep] = useState<Step>("upload");
  const [error, setError] = useState<string | null>(null);

  const [resumeId, setResumeId] = useState<string | null>(null);
  const [jobId, setJobId] = useState<string | null>(null);
  const [scoreResult, setScoreResult] = useState<JobScoreResponse | null>(null);

  const router = useRouter();
  const canAnalyze = file !== null && jobDescription.length >= 50 && sessionId;
  const busy = step === "analyzing" || step === "tailoring";

  async function handleAnalyze() {
    if (!file || !sessionId) return;
    setError(null);
    setStep("analyzing");

    try {
      const uploaded = await uploadResume(file, sessionId);
      setResumeId(uploaded.id);

      const scored = await scoreJob(uploaded.id, jobDescription, sessionId);
      setJobId(scored.job_id);
      setScoreResult(scored);
      setStep("scored");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong.");
      setStep("upload");
    }
  }

  function handleTailor() {
    if (!resumeId || !jobId || !sessionId) return;
    setStep("tailoring");
    setError(null);

    const cancel = streamTailor(
      resumeId,
      jobId,
      sessionId,
      () => {},
      () => {},
      (id) => {
        cancel();
        router.push(`/edit/${id}`);
      },
      (msg) => {
        setError(msg);
        setStep("scored");
        cancel();
      }
    );
  }

  return (
    <main className="mx-auto w-full max-w-2xl px-4 py-12">
      <div className="mb-10">
        <h1 className="text-2xl font-bold tracking-tight text-neutral-900">Resume Tailer</h1>
        <p className="mt-1 text-sm text-neutral-500">
          Upload your resume, paste a job description, and get a tailored version in seconds.
        </p>
      </div>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 px-4 py-3 text-sm text-red-600 ring-1 ring-red-200">
          {error}
        </div>
      )}

      {(step === "upload" || step === "analyzing") && (
        <div className="flex flex-col gap-6">
          <div className="flex flex-col gap-1.5">
            <label className="text-sm font-medium text-neutral-700">Resume</label>
            <ResumeDropzone file={file} onChange={setFile} disabled={busy} />
          </div>

          <JobDescriptionInput
            value={jobDescription}
            onChange={setJobDescription}
            disabled={busy}
          />

          <button
            onClick={handleAnalyze}
            disabled={!canAnalyze || busy}
            className="flex items-center justify-center gap-2 rounded-lg bg-neutral-900 py-3 text-sm font-semibold text-white transition-colors hover:bg-neutral-700 disabled:opacity-40"
          >
            {step === "analyzing" && <Loader2 className="h-4 w-4 animate-spin" />}
            {step === "analyzing" ? "Analyzing…" : "Analyze Match"}
          </button>
        </div>
      )}

      {(step === "scored" || step === "tailoring") && scoreResult && (
        <ScoreCard
          result={scoreResult}
          onTailor={handleTailor}
          tailoring={step === "tailoring"}
        />
      )}

    </main>
  );
}
