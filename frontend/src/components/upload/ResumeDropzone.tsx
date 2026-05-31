"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import { UploadCloud, FileText, X } from "lucide-react";
import { cn } from "@/lib/utils";

interface Props {
  file: File | null;
  onChange: (file: File | null) => void;
  disabled?: boolean;
}

export function ResumeDropzone({ file, onChange, disabled }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onChange(accepted[0]);
    },
    [onChange]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { "application/pdf": [".pdf"], "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"] },
    maxFiles: 1,
    disabled,
  });

  if (file) {
    return (
      <div className="flex items-center gap-3 rounded-lg border border-neutral-200 bg-neutral-50 px-4 py-3">
        <FileText className="h-5 w-5 shrink-0 text-neutral-500" />
        <span className="flex-1 truncate text-sm text-neutral-700">{file.name}</span>
        <button
          onClick={() => onChange(null)}
          disabled={disabled}
          className="rounded p-0.5 text-neutral-400 hover:text-neutral-600 disabled:opacity-40"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    );
  }

  return (
    <div
      {...getRootProps()}
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-2 rounded-lg border-2 border-dashed px-6 py-10 text-center transition-colors",
        isDragActive
          ? "border-neutral-900 bg-neutral-50"
          : "border-neutral-200 hover:border-neutral-400",
        disabled && "pointer-events-none opacity-50"
      )}
    >
      <input {...getInputProps()} />
      <UploadCloud className="h-8 w-8 text-neutral-400" />
      <div>
        <p className="text-sm font-medium text-neutral-700">
          {isDragActive ? "Drop it here" : "Drag & drop your resume"}
        </p>
        <p className="mt-0.5 text-xs text-neutral-400">PDF or DOCX, max 5 MB</p>
      </div>
    </div>
  );
}
