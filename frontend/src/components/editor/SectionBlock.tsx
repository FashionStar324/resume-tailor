"use client";

import { cn } from "@/lib/utils";
import { Pencil } from "lucide-react";

interface Props {
  sectionName: string;
  label: string;
  isActive: boolean;
  onEdit: (sectionName: string) => void;
  children: React.ReactNode;
  flash?: boolean;
}

export function SectionBlock({ sectionName, label, isActive, onEdit, children, flash }: Props) {
  return (
    <div
      className={cn(
        "group relative rounded-lg border px-4 py-3 transition-all duration-200",
        isActive
          ? "border-neutral-900 bg-neutral-50 shadow-sm"
          : "border-transparent hover:border-neutral-200 hover:bg-neutral-50",
        flash && "animate-pulse border-emerald-300 bg-emerald-50"
      )}
    >
      {children}

      <button
        onClick={() => onEdit(sectionName)}
        aria-label={`Edit ${label}`}
        className={cn(
          "absolute right-2 top-2 flex items-center gap-1 rounded-md px-2 py-1 text-xs font-medium transition-all",
          isActive
            ? "bg-neutral-900 text-white"
            : "bg-white text-neutral-500 opacity-0 shadow-sm ring-1 ring-neutral-200 group-hover:opacity-100"
        )}
      >
        <Pencil className="h-3 w-3" />
        {isActive ? "Editing" : "Edit"}
      </button>
    </div>
  );
}
