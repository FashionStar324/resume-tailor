"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { useSession } from "@/hooks/useSession";
import { getTailoredResume, editSection, getEditHistory, revertEdit } from "@/lib/api";
import type { ParsedResume, EditHistoryEntry } from "@/lib/types";
import { SectionBlock } from "./SectionBlock";
import { EditPanel } from "./EditPanel";
import { ContactHeader } from "./resume/ContactHeader";
import { SummarySection } from "./resume/SummarySection";
import { ExperienceEntry } from "./resume/ExperienceEntry";
import { SkillsSection } from "./resume/SkillsSection";
import { ProjectEntry } from "./resume/ProjectEntry";
import { EducationEntry } from "./resume/EducationEntry";
import { Loader2, ArrowLeft, Download } from "lucide-react";

interface Props {
  tailoredResumeId: string;
}

function applyRevision(sections: ParsedResume, sectionName: string, revised: unknown): ParsedResume {
  const [key, indexStr] = sectionName.split(".");
  const updated = { ...sections } as Record<string, unknown>;
  if (indexStr !== undefined) {
    const arr = [...(updated[key] as unknown[])];
    arr[parseInt(indexStr)] = revised;
    updated[key] = arr;
  } else {
    updated[key] = revised;
  }
  return updated as unknown as ParsedResume;
}

export function EditorClient({ tailoredResumeId }: Props) {
  const sessionId = useSession();

  const [sections, setSections] = useState<ParsedResume | null>(null);
  const [history, setHistory] = useState<EditHistoryEntry[]>([]);
  const [loadError, setLoadError] = useState<string | null>(null);

  const [activeSection, setActiveSection] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [editLoading, setEditLoading] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [flashSection, setFlashSection] = useState<string | null>(null);
  const [reverting, setReverting] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;
    getTailoredResume(tailoredResumeId, sessionId)
      .then((r) => setSections(r.sections))
      .catch((e) => setLoadError(e.message));
    getEditHistory(tailoredResumeId, sessionId)
      .then(setHistory)
      .catch(() => {});
  }, [tailoredResumeId, sessionId]);

  const handleEdit = useCallback((sectionName: string) => {
    setActiveSection(sectionName);
    setNote("");
    setEditError(null);
  }, []);

  const handleClose = useCallback(() => {
    setActiveSection(null);
    setNote("");
    setEditError(null);
  }, []);

  async function handleSubmit() {
    if (!activeSection || !sessionId || !sections) return;
    setEditLoading(true);
    setEditError(null);
    try {
      const result = await editSection(tailoredResumeId, activeSection, note, sessionId);
      setSections((prev) => prev ? applyRevision(prev, activeSection, result.revised_content) : prev);
      // Refresh history
      const updated = await getEditHistory(tailoredResumeId, sessionId);
      setHistory(updated);
      // Flash the revised section briefly
      setFlashSection(activeSection);
      setTimeout(() => setFlashSection(null), 1200);
      handleClose();
    } catch (e) {
      setEditError(e instanceof Error ? e.message : "Edit failed.");
    } finally {
      setEditLoading(false);
    }
  }

  async function handleRevert(editId: string) {
    if (!sessionId || !sections) return;
    setReverting(editId);
    try {
      const result = await revertEdit(editId, sessionId);
      const edit = history.find((h) => h.id === editId);
      if (edit) {
        setSections((prev) =>
          prev ? applyRevision(prev, edit.section_name, result.revised_content) : prev
        );
        setFlashSection(edit.section_name);
        setTimeout(() => setFlashSection(null), 1200);
      }
      const updated = await getEditHistory(tailoredResumeId, sessionId);
      setHistory(updated);
    } catch {
      // silent — revert errors don't need a modal
    } finally {
      setReverting(null);
    }
  }

  if (loadError) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <p className="text-sm text-red-500">{loadError}</p>
        <Link href="/" className="mt-4 inline-flex items-center gap-1 text-sm text-neutral-500 hover:text-neutral-800">
          <ArrowLeft className="h-3.5 w-3.5" /> Back
        </Link>
      </div>
    );
  }

  if (!sections) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <Loader2 className="h-6 w-6 animate-spin text-neutral-400" />
      </div>
    );
  }

  return (
    <div className="mx-auto w-full max-w-5xl px-4 py-8">
      {/* Top bar */}
      <div className="mb-6 flex items-center justify-between">
        <Link href="/" className="flex items-center gap-1.5 text-sm text-neutral-500 hover:text-neutral-800">
          <ArrowLeft className="h-3.5 w-3.5" /> New resume
        </Link>
        <div className="flex items-center gap-3">
          <span className="text-sm font-semibold text-neutral-900">Resume Tailer</span>
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/api/tailor/${tailoredResumeId}/pdf`}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-1.5 rounded-lg bg-neutral-900 px-3 py-2 text-xs font-semibold text-white hover:bg-neutral-700"
          >
            <Download className="h-3.5 w-3.5" /> Download PDF
          </a>
        </div>
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1fr_300px]">
        {/* Resume preview */}
        <div className="flex flex-col gap-4 rounded-xl border border-neutral-200 bg-white p-6 shadow-sm">
          <ContactHeader contact={sections.contact} />

          {sections.summary && (
            <SectionBlock
              sectionName="summary"
              label="Summary"
              isActive={activeSection === "summary"}
              onEdit={handleEdit}
              flash={flashSection === "summary"}
            >
              <SummarySection summary={sections.summary} />
            </SectionBlock>
          )}

          {sections.experience.length > 0 && (
            <div>
              <h2 className="mb-2 px-4 text-xs font-semibold uppercase tracking-widest text-neutral-400">
                Experience
              </h2>
              <div className="flex flex-col gap-2">
                {sections.experience.map((entry, i) => (
                  <SectionBlock
                    key={i}
                    sectionName={`experience.${i}`}
                    label={`${entry.role} at ${entry.company}`}
                    isActive={activeSection === `experience.${i}`}
                    onEdit={handleEdit}
                    flash={flashSection === `experience.${i}`}
                  >
                    <ExperienceEntry entry={entry} />
                  </SectionBlock>
                ))}
              </div>
            </div>
          )}

          {sections.projects.length > 0 && (
            <div>
              <h2 className="mb-2 px-4 text-xs font-semibold uppercase tracking-widest text-neutral-400">
                Projects
              </h2>
              <div className="flex flex-col gap-2">
                {sections.projects.map((entry, i) => (
                  <SectionBlock
                    key={i}
                    sectionName={`projects.${i}`}
                    label={entry.name}
                    isActive={activeSection === `projects.${i}`}
                    onEdit={handleEdit}
                    flash={flashSection === `projects.${i}`}
                  >
                    <ProjectEntry entry={entry} />
                  </SectionBlock>
                ))}
              </div>
            </div>
          )}

          <SectionBlock
            sectionName="skills"
            label="Skills"
            isActive={activeSection === "skills"}
            onEdit={handleEdit}
            flash={flashSection === "skills"}
          >
            <SkillsSection skills={sections.skills} />
          </SectionBlock>

          {sections.education.length > 0 && (
            <div>
              <h2 className="mb-2 px-4 text-xs font-semibold uppercase tracking-widest text-neutral-400">
                Education
              </h2>
              <div className="flex flex-col gap-2">
                {sections.education.map((entry, i) => (
                  <SectionBlock
                    key={i}
                    sectionName={`education.${i}`}
                    label={entry.institution}
                    isActive={activeSection === `education.${i}`}
                    onEdit={handleEdit}
                    flash={flashSection === `education.${i}`}
                  >
                    <EducationEntry entry={entry} />
                  </SectionBlock>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Edit panel */}
        <div className="lg:sticky lg:top-8 lg:self-start">
          {editError && (
            <div className="mb-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-600 ring-1 ring-red-200">
              {editError}
            </div>
          )}
          <EditPanel
            activeSection={activeSection}
            note={note}
            onNoteChange={setNote}
            onSubmit={handleSubmit}
            onClose={handleClose}
            loading={editLoading}
            history={history}
            onRevert={handleRevert}
            reverting={reverting}
          />
        </div>
      </div>
    </div>
  );
}
