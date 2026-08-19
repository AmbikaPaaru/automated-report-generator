"use client";

import { useState } from "react";

import { InstructionsModal } from "@/components/InstructionsModal";
import { JobStatusCard } from "@/components/JobStatusCard";
import { DownloadIcon, SparklesIcon } from "@/components/icons";
import { UploadForm } from "@/components/UploadForm";

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-lg flex-col items-center justify-center gap-6 px-4 py-16 sm:py-20">
      <header className="flex flex-col items-center gap-3 text-center">
        <span className="animate-pop-in flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-[var(--accent-1)] to-[var(--accent-3)] text-white shadow-lg shadow-[var(--accent-1)]/25">
          <SparklesIcon className="h-6 w-6" />
        </span>
        <h1 className="text-3xl font-bold tracking-tight text-[var(--foreground)] sm:text-4xl">
          Automated <span className="text-gradient">Report</span> Generator
        </h1>
        <p className="max-w-sm text-sm leading-relaxed text-[var(--muted)] sm:text-base">
          Upload a CSV. An LLM agent decides what charts and insights matter, then builds you a
          polished PDF report.
        </p>
      </header>

      <div className="w-full rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-5 shadow-xl shadow-black/[0.03] sm:p-6">
        {jobId ? (
          <JobStatusCard key={jobId} jobId={jobId} />
        ) : (
          <div className="flex flex-col gap-4">
            <div className="flex items-center justify-end gap-1">
              <a
                href="/report-template.csv"
                download
                className="inline-flex items-center gap-1.5 text-sm font-medium text-[var(--accent-1)] transition hover:underline"
              >
                <DownloadIcon className="h-3.5 w-3.5" />
                Download template
              </a>
              <InstructionsModal />
            </div>
            <UploadForm onCreated={setJobId} />
          </div>
        )}
      </div>

      {jobId && (
        <button
          type="button"
          onClick={() => setJobId(null)}
          className="animate-fade-in inline-flex items-center gap-1.5 text-sm font-medium text-[var(--muted)] transition hover:text-[var(--accent-1)]"
        >
          <span aria-hidden="true">&larr;</span> Start a new report
        </button>
      )}
    </main>
  );
}
