"use client";

import { useState, type FormEvent } from "react";

import { useCreateJobMutation } from "@/features/jobs/jobsApi";

interface UploadFormProps {
  onCreated: (jobId: string) => void;
  disabled?: boolean;
}

export function UploadForm({ onCreated, disabled }: UploadFormProps) {
  const [file, setFile] = useState<File | null>(null);
  const [createJob, { isLoading, error }] = useCreateJobMutation();

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

  const errorMessage = error ? extractErrorMessage(error) : null;

  return (
    <form
      onSubmit={handleSubmit}
      className="flex flex-col gap-4 rounded-xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div>
        <label htmlFor="csv-file" className="mb-1 block text-sm font-medium text-slate-700">
          CSV file
        </label>
        <input
          id="csv-file"
          type="file"
          accept=".csv"
          disabled={disabled || isLoading}
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          className="block w-full cursor-pointer rounded-lg border border-slate-300 text-sm text-slate-600 file:mr-4 file:cursor-pointer file:rounded-md file:border-0 file:bg-slate-900 file:px-4 file:py-2 file:text-sm file:font-medium file:text-white hover:file:bg-slate-700"
        />
      </div>

      <button
        type="submit"
        disabled={!file || disabled || isLoading}
        className="inline-flex items-center justify-center rounded-lg bg-indigo-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-300"
      >
        {isLoading ? "Uploading..." : "Process"}
      </button>

      {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}
    </form>
  );
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
