"use client";

import { Loader2, X, RotateCcw } from "lucide-react";
import type { EditHistoryEntry } from "@/lib/types";

interface Props {
  activeSection: string | null;
  note: string;
  onNoteChange: (v: string) => void;
  onSubmit: () => void;
  onClose: () => void;
  loading: boolean;
  history: EditHistoryEntry[];
  onRevert: (editId: string) => void;
  reverting: string | null;
}

function sectionLabel(name: string): string {
  const [key, index] = name.split(".");
  const labels: Record<string, string> = {
    summary: "Summary",
    skills: "Skills",
    experience: "Experience",
    projects: "Projects",
    education: "Education",
  };
  const base = labels[key] ?? key;
  return index !== undefined ? `${base} #${parseInt(index) + 1}` : base;
}

export function EditPanel({
  activeSection,
  note,
  onNoteChange,
  onSubmit,
  onClose,
  loading,
  history,
  onRevert,
  reverting,
}: Props) {
  if (!activeSection) {
    return (
      <div className="flex flex-col gap-3 rounded-xl border border-neutral-100 bg-neutral-50 p-5">
        <p className="text-sm font-medium text-neutral-500">Section Editor</p>
        <p className="text-xs text-neutral-400 leading-relaxed">
          Hover over any section in the resume and click <strong>Edit</strong> to revise it.
          Only that section will be rewritten — the rest stays untouched.
        </p>

        {history.length > 0 && (
          <div className="mt-2 flex flex-col gap-2">
            <p className="text-xs font-semibold uppercase tracking-wider text-neutral-400">
              Edit History
            </p>
            <div className="flex flex-col gap-2">
              {history.map((e) => (
                <div
                  key={e.id}
                  className="rounded-lg border border-neutral-200 bg-white p-3"
                >
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-xs font-medium text-neutral-700">
                        {sectionLabel(e.section_name)}
                      </p>
                      {e.user_note && (
                        <p className="mt-0.5 text-xs text-neutral-400 line-clamp-2">
                          {e.user_note}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => onRevert(e.id)}
                      disabled={reverting === e.id}
                      className="flex shrink-0 items-center gap-1 rounded-md px-2 py-1 text-xs text-neutral-500 ring-1 ring-neutral-200 hover:bg-neutral-50 disabled:opacity-50"
                    >
                      {reverting === e.id ? (
                        <Loader2 className="h-3 w-3 animate-spin" />
                      ) : (
                        <RotateCcw className="h-3 w-3" />
                      )}
                      Revert
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 rounded-xl border border-neutral-900 bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-semibold text-neutral-900">
            Editing: {sectionLabel(activeSection)}
          </p>
          <p className="mt-0.5 text-xs text-neutral-400">
            Full resume context is included — only this section will change.
          </p>
        </div>
        <button onClick={onClose} className="rounded-md p-1 text-neutral-400 hover:text-neutral-600">
          <X className="h-4 w-4" />
        </button>
      </div>

      <div className="flex flex-col gap-1.5">
        <label className="text-xs font-medium text-neutral-600">
          What should change?
        </label>
        <textarea
          value={note}
          onChange={(e) => onNoteChange(e.target.value)}
          disabled={loading}
          placeholder="e.g. Emphasize leadership and mention the Kubernetes migration I led."
          rows={4}
          className="w-full resize-none rounded-lg border border-neutral-200 px-3 py-2 text-sm text-neutral-800 placeholder:text-neutral-400 focus:border-neutral-500 focus:outline-none disabled:opacity-50"
          autoFocus
        />
      </div>

      <button
        onClick={onSubmit}
        disabled={loading || note.trim().length === 0}
        className="flex items-center justify-center gap-2 rounded-lg bg-neutral-900 py-2.5 text-sm font-semibold text-white hover:bg-neutral-700 disabled:opacity-40"
      >
        {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        {loading ? "Revising…" : "Revise Section"}
      </button>
    </div>
  );
}
