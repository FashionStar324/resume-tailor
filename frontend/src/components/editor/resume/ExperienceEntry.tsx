import type { ExperienceEntry as IExperienceEntry } from "@/lib/types";

export function ExperienceEntry({ entry }: { entry: IExperienceEntry }) {
  return (
    <div>
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-sm font-semibold text-neutral-900">{entry.role}</p>
          <p className="text-sm text-neutral-600">
            {entry.company}
            {entry.location ? ` · ${entry.location}` : ""}
          </p>
        </div>
        {(entry.start_date || entry.end_date) && (
          <span className="shrink-0 text-xs text-neutral-400">
            {entry.start_date} – {entry.end_date ?? "Present"}
          </span>
        )}
      </div>
      {entry.bullets.length > 0 && (
        <ul className="mt-2 flex flex-col gap-1">
          {entry.bullets.map((b, i) => (
            <li key={i} className="flex gap-2 text-sm text-neutral-700">
              <span className="mt-1.5 h-1 w-1 shrink-0 rounded-full bg-neutral-400" />
              <span>{b}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
