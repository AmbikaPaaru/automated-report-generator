import { downloadUrlFor } from "@/features/jobs/jobsApi";

import { DownloadIcon } from "./icons";

export function DownloadButton({ jobId }: { jobId: string }) {
  return (
    <a
      href={downloadUrlFor(jobId)}
      download
      className="animate-ring-pulse inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[var(--success)] px-4 py-3 text-sm font-semibold text-white shadow-md shadow-[var(--success)]/20 transition-all duration-200 hover:brightness-105 active:scale-[0.98]"
    >
      <DownloadIcon className="h-4 w-4" />
      Download report
    </a>
  );
}
