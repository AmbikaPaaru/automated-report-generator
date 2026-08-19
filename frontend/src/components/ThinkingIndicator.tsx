"use client";

import { useEffect, useState } from "react";

import { SparklesIcon } from "./icons";

/**
 * Claude-style "thinking" indicator for the single opaque `processing` status
 * the backend reports. The real pipeline (load -> plan -> chart -> summarize -> PDF)
 * doesn't report granular progress, so instead of a static "Processing..." string
 * we rotate through the actual pipeline stages (see backend/README.md's
 * `load_data -> plan_analysis -> generate_charts -> summarize -> PDF -> Postgres`)
 * on a timer. It's cosmetic pacing, not a truth claim about server-side progress --
 * the moment the real status flips to complete/failed, the parent unmounts this.
 */
const STAGES = [
  "Reading your data...",
  "Deciding what matters...",
  "Sketching the charts...",
  "Writing the insights...",
  "Assembling the PDF...",
];

const STAGE_INTERVAL_MS = 2800;

export function ThinkingIndicator() {
  const [stageIndex, setStageIndex] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setStageIndex((i) => (i + 1) % STAGES.length);
    }, STAGE_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-2.5">
        <span className="relative flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[var(--accent-1)] to-[var(--accent-3)] text-white">
          <SparklesIcon className="h-3.5 w-3.5 animate-breathe" />
        </span>
        <p
          key={stageIndex}
          className="animate-fade-in text-sm font-medium text-[var(--foreground)]"
          aria-live="polite"
        >
          {STAGES[stageIndex]}
        </p>
      </div>

      <div className="h-1.5 w-full overflow-hidden rounded-full bg-[var(--surface-muted)]">
        <div className="progress-indeterminate h-full w-full rounded-full" />
      </div>
    </div>
  );
}
