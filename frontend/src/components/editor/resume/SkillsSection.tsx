import type { SkillsSection as ISkillsSection } from "@/lib/types";

function SkillGroup({ label, items }: { label: string; items: string[] }) {
  if (!items.length) return null;
  return (
    <div className="flex gap-2">
      <span className="shrink-0 text-xs font-medium text-neutral-500">{label}:</span>
      <span className="text-xs text-neutral-700">{items.join(", ")}</span>
    </div>
  );
}

export function SkillsSection({ skills }: { skills: ISkillsSection }) {
  return (
    <div>
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-widest text-neutral-400">
        Skills
      </h2>
      <div className="flex flex-col gap-1.5">
        <SkillGroup label="Languages" items={skills.languages} />
        <SkillGroup label="Frameworks" items={skills.frameworks} />
        <SkillGroup label="Tools" items={skills.tools} />
        <SkillGroup label="Other" items={skills.other} />
      </div>
    </div>
  );
}
