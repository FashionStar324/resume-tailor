import { cn } from "@/lib/utils";

interface Props {
  label: string;
  value: number; // 0–1
  description?: string;
}

function scoreColor(value: number): string {
  if (value >= 0.75) return "bg-emerald-500";
  if (value >= 0.5) return "bg-amber-400";
  return "bg-red-400";
}

function scoreTextColor(value: number): string {
  if (value >= 0.75) return "text-emerald-600";
  if (value >= 0.5) return "text-amber-500";
  return "text-red-500";
}

export function ScoreMeter({ label, value, description }: Props) {
  const pct = Math.round(value * 100);

  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-baseline justify-between">
        <span className="text-sm font-medium text-neutral-700">{label}</span>
        <span className={cn("text-sm font-semibold tabular-nums", scoreTextColor(value))}>
          {pct}%
        </span>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-neutral-100">
        <div
          className={cn("h-full rounded-full transition-all duration-500", scoreColor(value))}
          style={{ width: `${pct}%` }}
        />
      </div>
      {description && (
        <p className="text-xs text-neutral-400">{description}</p>
      )}
    </div>
  );
}
