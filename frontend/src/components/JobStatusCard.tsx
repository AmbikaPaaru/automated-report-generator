"use client";

import { useState } from "react";

import { useGetJobStatusQuery } from "@/features/jobs/jobsApi";
import { isTerminalStatus } from "@/features/jobs/types";

import { DownloadButton } from "./DownloadButton";

const POLL_INTERVAL_MS = 2000;

const STATUS_LABEL: Record<string, string> = {
  pending: "Queued...",
  processing: "Claude is analyzing your data...",
  complete: "Report ready.",
  failed: "Something went wrong.",
};

export function JobStatusCard({ jobId }: { jobId: string }) {
  // Poll every 2s until the job reaches a terminal state, then stop: setting
  // pollingInterval to 0 cancels RTK Query's scheduled refetch. We adjust this
  // state *during render* (React's documented pattern for "derive state from a
  // changing value", guarded so it only fires once per actual status change)
  // rather than in a useEffect, which the stricter react-hooks rules now flag
  // as an avoidable cascading render: https://react.dev/learn/you-might-not-need-an-effect
  const [pollingInterval, setPollingInterval] = useState(POLL_INTERVAL_MS);
  const [lastSeenStatus, setLastSeenStatus] = useState<string | null>(null);

  const { data: job, isLoading, isError } = useGetJobStatusQuery(jobId, {
    pollingInterval,
    skipPollingIfUnfocused: true,
  });

  if (job && job.status !== lastSeenStatus) {
    setLastSeenStatus(job.status);
    if (isTerminalStatus(job.status)) {
      setPollingInterval(0);
    }
  }

  return (
    <div className="flex flex-col gap-3 rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <h2 className="text-sm font-medium text-slate-500">Job status</h2>

      {isLoading && <p className="text-sm text-slate-600">Loading...</p>}
      {isError && <p className="text-sm text-red-600">Could not reach the backend.</p>}

      {job && (
        <>
          <div className="flex items-center gap-2">
            <StatusDot status={job.status} />
            <p className="text-base font-semibold text-slate-800">
              {STATUS_LABEL[job.status] ?? job.status}
            </p>
          </div>
          <p className="text-sm text-slate-500">{job.filename}</p>

          {job.status === "failed" && job.error_message && (
            <p className="rounded-md bg-red-50 p-3 text-sm text-red-700">
              {job.error_message}
            </p>
          )}

          {job.report_ready && <DownloadButton jobId={job.id} />}
        </>
      )}
    </div>
  );
}

function StatusDot({ status }: { status: string }) {
  const color =
    status === "complete"
      ? "bg-emerald-500"
      : status === "failed"
        ? "bg-red-500"
        : "bg-amber-500 animate-pulse";

  return <span className={`h-2.5 w-2.5 rounded-full ${color}`} />;
}
