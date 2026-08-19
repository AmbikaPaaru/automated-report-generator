"use client";

import { useRef } from "react";

import { InfoIcon, XIcon } from "./icons";

/**
 * A native <dialog> instead of a hand-rolled overlay: showModal() gives us focus
 * trapping, Escape-to-close, and a ::backdrop for free, with no extra dependency.
 * Clicking the backdrop closes it too -- checking event.target === the dialog
 * itself (not a child) is the standard way to detect that, since a real click
 * lands on the dialog's own box outside its inner content wrapper.
 *
 * The backend only enforces the .csv extension (see POST /jobs) -- there's no
 * server-side row/size limit yet -- so the size guidance below is a recommendation
 * for reliable results, not a hard rule the app will reject you for crossing. It
 * comes from how the pipeline actually works: app/services/profiling.py caps the
 * text profile handed to the LLM at 6000 characters, so a very wide or very long
 * CSV just gets silently truncated in what the model sees, rather than failing.
 */
export function InstructionsModal() {
  const dialogRef = useRef<HTMLDialogElement>(null);

  return (
    <>
      <button
        type="button"
        aria-label="Upload instructions"
        onClick={() => dialogRef.current?.showModal()}
        className="flex h-8 w-8 cursor-pointer items-center justify-center rounded-full text-[var(--muted)] transition hover:bg-[var(--surface-muted)] hover:text-[var(--accent-1)]"
      >
        <InfoIcon className="h-4.5 w-4.5" />
      </button>

      <dialog
        ref={dialogRef}
        onClick={(event) => {
          if (event.target === dialogRef.current) dialogRef.current?.close();
        }}
        className="modal-dialog"
      >
        <div className="flex flex-col gap-4 p-5 sm:p-6">
          <div className="flex items-start justify-between gap-3">
            <h2 className="text-base font-semibold text-[var(--foreground)]">Before you upload</h2>
            <button
              type="button"
              aria-label="Close"
              onClick={() => dialogRef.current?.close()}
              className="flex h-7 w-7 shrink-0 cursor-pointer items-center justify-center rounded-full text-[var(--muted)] transition hover:bg-[var(--surface-muted)] hover:text-[var(--foreground)]"
            >
              <XIcon className="h-4 w-4" />
            </button>
          </div>

          <ul className="flex flex-col gap-2.5 text-sm text-[var(--muted)]">
            <li>
              <strong className="font-medium text-[var(--foreground)]">Format:</strong> a plain{" "}
              <code className="rounded bg-[var(--surface-muted)] px-1 py-0.5 font-mono text-xs">.csv</code>{" "}
              file &mdash; not Excel (.xlsx) or any other format.
            </li>
            <li>
              <strong className="font-medium text-[var(--foreground)]">Shape:</strong> one header
              row naming each column, then one row per record. Any columns work &mdash; sales,
              budgets, inventory, survey data, and similar are all fine.
            </li>
            <li>
              <strong className="font-medium text-[var(--foreground)]">Size:</strong> keep it to a
              few thousand rows and a handful of columns for the most reliable results &mdash;
              very large files may have parts of their data summarized rather than considered in
              full.
            </li>
          </ul>
        </div>
      </dialog>
    </>
  );
}
