"use client";

import { useState } from "react";

import { JobStatusCard } from "@/components/JobStatusCard";
import { UploadForm } from "@/components/UploadForm";

export default function Home() {
  const [jobId, setJobId] = useState<string | null>(null);

  return (
    <main className="mx-auto flex min-h-screen w-full max-w-xl flex-col gap-6 px-4 py-16">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Automated Report Generator</h1>
        <p className="mt-1 text-sm text-slate-500">
          Upload a CSV. Claude decides what charts and insights matter, then builds a PDF report.
        </p>
      </div>

      <UploadForm onCreated={setJobId} />

      {jobId && <JobStatusCard key={jobId} jobId={jobId} />}

      {jobId && (
        <button
          type="button"
          onClick={() => setJobId(null)}
          className="self-start text-sm font-medium text-slate-500 underline-offset-2 hover:text-slate-700 hover:underline"
        >
          Start a new report
        </button>
      )}
    </main>
  );
}
