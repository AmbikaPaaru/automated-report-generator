"use client";

import { useId, useRef, useState, type DragEvent, type FormEvent } from "react";

import { useCreateJobMutation } from "@/features/jobs/jobsApi";

import { AlertTriangleIcon, FileTextIcon, UploadCloudIcon, XIcon } from "./icons";
import { Spinner } from "./Spinner";

interface UploadFormProps {
  onCreated: (jobId: string) => void;
  disabled?: boolean;
}

export function UploadForm({ onCreated, disabled }: UploadFormProps) {
  const inputId = useId();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [createJob, { isLoading, error }] = useCreateJobMutation();

  const busy = disabled || isLoading;

  function pickFile(candidate: File | null) {
    setValidationError(null);
    if (!candidate) {
      setFile(null);
      return;
    }
    if (!candidate.name.toLowerCase().endsWith(".csv")) {
      setValidationError("That doesn't look like a CSV file. Please pick a .csv file.");
      setFile(null);
      return;
    }
    setFile(candidate);
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
    setIsDragging(false);
    if (busy) return;
    pickFile(event.dataTransfer.files?.[0] ?? null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) return;

    try {
      const job = await createJob(file).unwrap();
      onCreated(job.id);
      setFile(null);
    } catch {
      // surfaced below via `error` from the mutation hook
    }
  }

  const errorMessage = validationError ?? (error ? extractErrorMessage(error) : null);

  return (
    <form onSubmit={handleSubmit} className="flex flex-col gap-4">
      <div
        role="button"
        tabIndex={busy ? -1 : 0}
        aria-disabled={busy}
        onClick={() => !busy && fileInputRef.current?.click()}
        onKeyDown={(event) => {
          if ((event.key === "Enter" || event.key === " ") && !busy) {
            event.preventDefault();
            fileInputRef.current?.click();
          }
        }}
        onDragOver={(event) => {
          event.preventDefault();
          if (!busy) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleDrop}
        className={[
          "group relative flex cursor-pointer flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-200",
          busy ? "cursor-not-allowed opacity-60" : "hover:border-[var(--accent-1)] hover:bg-[var(--surface-muted)]",
          isDragging
            ? "scale-[1.01] border-[var(--accent-1)] bg-[var(--surface-muted)] shadow-inner"
            : "border-[var(--border)]",
        ].join(" ")}
      >
        <input
          ref={fileInputRef}
          id={inputId}
          type="file"
          accept=".csv"
          disabled={busy}
          onChange={(event) => pickFile(event.target.files?.[0] ?? null)}
          className="sr-only"
        />

        {file ? (
          <div className="animate-pop-in flex w-full max-w-sm items-center gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 text-left shadow-sm">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-[var(--surface-muted)] text-[var(--accent-1)]">
              <FileTextIcon className="h-5 w-5" />
            </span>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-[var(--foreground)]">{file.name}</p>
              <p className="text-xs text-[var(--muted)]">{formatBytes(file.size)}</p>
            </div>
            <button
              type="button"
              aria-label="Remove selected file"
              onClick={(event) => {
                event.stopPropagation();
                pickFile(null);
                if (fileInputRef.current) fileInputRef.current.value = "";
              }}
              disabled={busy}
              className="rounded-full p-1.5 text-[var(--muted)] transition hover:bg-[var(--surface-muted)] hover:text-[var(--foreground)] disabled:pointer-events-none"
            >
              <XIcon className="h-4 w-4" />
            </button>
          </div>
        ) : (
          <>
            <span
              className={[
                "flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent-1)] to-[var(--accent-3)] text-white shadow-lg shadow-[var(--accent-1)]/20 transition-transform duration-200",
                isDragging ? "scale-110" : "group-hover:scale-105",
              ].join(" ")}
            >
              <UploadCloudIcon className="h-6 w-6" />
            </span>
            <div>
              <p className="text-sm font-semibold text-[var(--foreground)]">
                {isDragging ? "Drop it right here" : "Drag & drop your CSV"}
              </p>
              <p className="mt-0.5 text-sm text-[var(--muted)]">
                or <span className="font-medium text-[var(--accent-1)]">browse from your computer</span>
              </p>
            </div>
          </>
        )}
      </div>

      <button
        type="submit"
        disabled={!file || busy}
        className="inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[var(--accent-1)] to-[var(--accent-2)] px-4 py-3 text-sm font-semibold text-white shadow-md shadow-[var(--accent-1)]/25 transition-all duration-200 hover:shadow-lg hover:shadow-[var(--accent-1)]/35 hover:brightness-105 active:scale-[0.98] disabled:cursor-not-allowed disabled:opacity-40 disabled:shadow-none"
      >
        {isLoading ? (
          <>
            <Spinner className="h-4 w-4" />
            Uploading...
          </>
        ) : (
          "Process report"
        )}
      </button>

      {errorMessage && (
        <p className="animate-fade-in-up flex items-start gap-2 rounded-lg bg-[var(--danger-bg)] p-3 text-sm text-[var(--danger)]">
          <AlertTriangleIcon className="mt-0.5 h-4 w-4 shrink-0" />
          {errorMessage}
        </p>
      )}
    </form>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes / 1024;
  let unitIndex = 0;
  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex += 1;
  }
  return `${value.toFixed(1)} ${units[unitIndex]}`;
}

function extractErrorMessage(error: unknown): string {
  if (
    typeof error === "object" &&
    error !== null &&
    "data" in error &&
    typeof (error as { data?: unknown }).data === "object"
  ) {
    const data = (error as { data?: { detail?: string } }).data;
    if (data?.detail) return data.detail;
  }
  return "Upload failed. Please try again.";
}
