"use client";

import { useState } from "react";

import { ChevronDownIcon, CopyIcon } from "./icons";

/**
 * The backend sometimes reports `error_message` as a full Python traceback
 * (see backend/app/services/pipeline.py). Dumping that raw into a fixed-width
 * card blew out the layout -- long unbroken lines pushed past the card edge
 * and the whole block just kept growing vertically with the page.
 *
 * Instead: show a short, human summary line up front (the exception's own
 * message, i.e. the traceback's last line) and tuck the full traceback behind
 * a "Show details" toggle inside a capped, scrollable, monospace box.
 */
export function ErrorDetails({ message }: { message: string }) {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  const { summary, details } = summarize(message);

  return (
    <div className="flex flex-col gap-2 rounded-lg bg-[var(--danger-bg)] p-3">
      <p className="break-words text-sm text-[var(--danger)]">{summary}</p>

      {details && (
        <>
          <button
            type="button"
            onClick={() => setExpanded((v) => !v)}
            className="inline-flex w-fit items-center gap-1 text-xs font-medium text-[var(--danger)]/80 transition hover:text-[var(--danger)]"
          >
            <ChevronDownIcon className={`h-3.5 w-3.5 transition-transform duration-200 ${expanded ? "rotate-180" : ""}`} />
            {expanded ? "Hide details" : "Show details"}
          </button>

          {expanded && (
            <div className="animate-fade-in-up relative">
              <pre className="max-h-48 overflow-auto whitespace-pre-wrap break-words rounded-md bg-black/[0.04] p-3 font-mono text-xs leading-relaxed text-[var(--danger)]/90 dark:bg-white/[0.04]">
                {details}
              </pre>
              <button
                type="button"
                onClick={async () => {
                  await navigator.clipboard.writeText(details);
                  setCopied(true);
                  setTimeout(() => setCopied(false), 1500);
                }}
                className="absolute right-2 top-2 inline-flex items-center gap-1 rounded-md bg-[var(--surface)] px-2 py-1 text-xs font-medium text-[var(--muted)] shadow-sm transition hover:text-[var(--foreground)]"
              >
                <CopyIcon className="h-3 w-3" />
                {copied ? "Copied" : "Copy"}
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

function summarize(message: string): { summary: string; details: string | null } {
  const trimmed = message.trim();
  const lines = trimmed.split("\n").filter((line) => line.trim().length > 0);

  const looksLikeTraceback = /^Traceback \(most recent call last\)/.test(trimmed) && lines.length > 1;
  if (!looksLikeTraceback) {
    return { summary: trimmed, details: null };
  }

  const lastLine = lines[lines.length - 1].trim();
  return { summary: lastLine, details: trimmed };
}
