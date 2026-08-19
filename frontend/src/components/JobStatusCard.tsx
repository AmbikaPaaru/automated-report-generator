"use client";

import { useGetJobStatusQuery } from "@/features/jobs/jobsApi";
import { DownloadButton } from "./DownloadButton";
import { ErrorDetails } from "./ErrorDetails";
import { AlertTriangleIcon, CheckCircleIcon, ClockIcon, FileTextIcon } from "./icons";
import { ThinkingIndicator } from "./ThinkingIndicator";

export function JobStatusCard({ jobId }: Readonly<{ jobId: string }>) {
  const { data: job, isLoading, isError } = useGetJobStatusQuery(jobId);

  return (
    <div className="animate-fade-in-up flex flex-col gap-4 rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm shadow-black/[0.02]">
      <h2 className="text-xs font-semibold uppercase tracking-wide text-[var(--muted)]">Job status</h2>

      {isLoading && <StatusSkeleton />}

      {isError && (
        <p className="flex items-center gap-2 text-sm text-[var(--danger)]">
          <AlertTriangleIcon className="h-4 w-4 shrink-0" />
          Could not reach the backend. Is it running on port 8000?
        </p>
      )}

      {job && (
        <div key={job.status} className="animate-fade-in flex flex-col gap-4">
          <div className="flex items-center gap-3">
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-[var(--surface-muted)] text-[var(--muted)]">
              <FileTextIcon className="h-4.5 w-4.5" />
            </span>
            <p className="min-w-0 truncate text-sm font-medium text-[var(--foreground)]">{job.filename}</p>
          </div>

          {job.status === "pending" && (
            <div className="flex items-center gap-2.5 text-sm font-medium text-[var(--muted)]">
              <ClockIcon className="h-4 w-4 animate-breathe" />
              Queued -- your job will start any moment.
            </div>
          )}

          {job.status === "processing" && <ThinkingIndicator />}

          {job.status === "complete" && (
            <div className="animate-pop-in flex items-center gap-2.5">
              <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[var(--success-bg)] text-[var(--success)]">
                <CheckCircleIcon className="h-4 w-4" />
              </span>
              <p className="text-sm font-semibold text-[var(--foreground)]">Report ready</p>
            </div>
          )}

          {job.status === "failed" && (
            <div className="flex flex-col gap-2">
              <div className="flex items-center gap-2.5">
                <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-[var(--danger-bg)] text-[var(--danger)]">
                  <AlertTriangleIcon className="h-4 w-4" />
                </span>
                <p className="text-sm font-semibold text-[var(--foreground)]">Something went wrong</p>
              </div>
              {job.error_message && <ErrorDetails message={job.error_message} />}
            </div>
          )}

          {job.report_ready && (
            <div className="animate-fade-in-up">
              <DownloadButton jobId={job.id} />
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StatusSkeleton() {
  return (
    <div className="flex flex-col gap-3" aria-hidden="true">
      <div className="flex items-center gap-3">
        <div className="skeleton h-9 w-9 rounded-lg" />
        <div className="skeleton h-4 w-40 rounded" />
      </div>
      <div className="skeleton h-4 w-56 rounded" />
    </div>
  );
}
