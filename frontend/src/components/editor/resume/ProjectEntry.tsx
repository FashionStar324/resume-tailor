import type { ProjectEntry as IProjectEntry } from "@/lib/types";

export function ProjectEntry({ entry }: { entry: IProjectEntry }) {
  return (
    <div>
      <div className="flex items-baseline gap-2">
        <p className="text-sm font-semibold text-neutral-900">{entry.name}</p>
        {entry.technologies.length > 0 && (
          <span className="text-xs text-neutral-400">{entry.technologies.join(", ")}</span>
        )}
      </div>
      {entry.description && (
        <p className="mt-0.5 text-sm text-neutral-600">{entry.description}</p>
      )}
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
