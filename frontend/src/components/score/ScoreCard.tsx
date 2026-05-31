import { cn } from "@/lib/utils";
import type { JobScoreResponse } from "@/lib/types";
import { ScoreMeter } from "./ScoreMeter";
import { CheckCircle2, AlertCircle, Lightbulb } from "lucide-react";

interface Props {
  result: JobScoreResponse;
  onTailor: () => void;
  tailoring: boolean;
}

function overallLabel(score: number): string {
  if (score >= 0.8) return "Strong Match";
  if (score >= 0.65) return "Good Match";
  if (score >= 0.5) return "Partial Match";
  return "Weak Match";
}

function overallColors(score: number) {
  if (score >= 0.8) return { ring: "ring-emerald-200", bg: "bg-emerald-50", text: "text-emerald-700" };
  if (score >= 0.65) return { ring: "ring-amber-200", bg: "bg-amber-50", text: "text-amber-700" };
  return { ring: "ring-red-200", bg: "bg-red-50", text: "text-red-600" };
}

export function ScoreCard({ result, onTailor, tailoring }: Props) {
  const { score, parsed_requirements } = result;
  const pct = Math.round(score.overall * 100);
  const colors = overallColors(score.overall);

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-neutral-900">Match Analysis</h2>
          {parsed_requirements.title && (
            <p className="mt-0.5 text-sm text-neutral-500">
              {parsed_requirements.title}
              {parsed_requirements.company ? ` · ${parsed_requirements.company}` : ""}
            </p>
          )}
        </div>
        <div className={cn("flex flex-col items-center rounded-xl px-4 py-2 ring-2", colors.ring, colors.bg)}>
          <span className={cn("text-3xl font-bold tabular-nums", colors.text)}>{pct}</span>
          <span className={cn("text-xs font-medium", colors.text)}>{overallLabel(score.overall)}</span>
        </div>
      </div>

      {/* Score meters */}
      <div className="flex flex-col gap-4 rounded-lg border border-neutral-100 bg-neutral-50 p-4">
        <ScoreMeter
          label="Keyword Match"
          value={score.keyword_match}
          description="Required skills present in your resume"
        />
        <ScoreMeter
          label="Experience Alignment"
          value={score.experience_alignment}
          description="Seniority, domain, and years of experience"
        />
        <ScoreMeter
          label="Impact Language"
          value={score.impact_language}
          description="Metrics, scale, and outcomes in your bullets"
        />
      </div>

      {/* Missing keywords */}
      {score.missing.length > 0 && (
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5">
            <AlertCircle className="h-4 w-4 text-red-400" />
            <span className="text-sm font-medium text-neutral-700">Missing Keywords</span>
          </div>
          <div className="flex flex-wrap gap-1.5">
            {score.missing.map((kw) => (
              <span key={kw} className="rounded-md bg-red-50 px-2 py-0.5 text-xs font-medium text-red-600 ring-1 ring-red-200">
                {kw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Strengths */}
      {score.strengths.length > 0 && (
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4 text-emerald-500" />
            <span className="text-sm font-medium text-neutral-700">Strengths</span>
          </div>
          <ul className="flex flex-col gap-1">
            {score.strengths.map((s) => (
              <li key={s} className="text-sm text-neutral-600">{s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* Suggestions */}
      {score.suggestions.length > 0 && (
        <div className="flex flex-col gap-2">
          <div className="flex items-center gap-1.5">
            <Lightbulb className="h-4 w-4 text-amber-400" />
            <span className="text-sm font-medium text-neutral-700">Suggestions</span>
          </div>
          <ul className="flex flex-col gap-1.5">
            {score.suggestions.map((s) => (
              <li key={s} className="text-sm text-neutral-600">{s}</li>
            ))}
          </ul>
        </div>
      )}

      {/* CTA */}
      <button
        onClick={onTailor}
        disabled={tailoring}
        className="w-full rounded-lg bg-neutral-900 py-3 text-sm font-semibold text-white transition-colors hover:bg-neutral-700 disabled:opacity-60"
      >
        {tailoring ? "Tailoring…" : "Tailor My Resume"}
      </button>
    </div>
  );
}
