import { downloadUrlFor } from "@/features/jobs/jobsApi";

export function DownloadButton({ jobId }: { jobId: string }) {
  return (
    <a
      href={downloadUrlFor(jobId)}
      download
      className="inline-flex items-center justify-center rounded-lg bg-emerald-600 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-500"
    >
      Download report
    </a>
  );
}
