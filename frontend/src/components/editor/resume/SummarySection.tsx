export function SummarySection({ summary }: { summary: string }) {
  return (
    <div>
      <h2 className="mb-2 text-xs font-semibold uppercase tracking-widest text-neutral-400">
        Summary
      </h2>
      <p className="text-sm leading-relaxed text-neutral-700">{summary}</p>
    </div>
  );
}
