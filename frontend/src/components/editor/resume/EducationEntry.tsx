import type { EducationEntry as IEducationEntry } from "@/lib/types";

export function EducationEntry({ entry }: { entry: IEducationEntry }) {
  return (
    <div className="flex items-start justify-between gap-2">
      <div>
        <p className="text-sm font-semibold text-neutral-900">{entry.institution}</p>
        {(entry.degree || entry.field) && (
          <p className="text-sm text-neutral-600">
            {[entry.degree, entry.field].filter(Boolean).join(", ")}
            {entry.gpa ? ` · GPA ${entry.gpa}` : ""}
          </p>
        )}
      </div>
      {entry.graduation_date && (
        <span className="shrink-0 text-xs text-neutral-400">{entry.graduation_date}</span>
      )}
    </div>
  );
}
