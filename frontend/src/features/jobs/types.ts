/** Mirrors backend/app/schemas.py and backend/app/models.py (JobStatus). */

export type JobStatusValue = "pending" | "processing" | "complete" | "failed";

export interface JobCreateResponse {
  id: string;
  filename: string;
  status: JobStatusValue;
  created_at: string;
}

export interface JobStatusResponse {
  id: string;
  filename: string;
  status: JobStatusValue;
  created_at: string;
  updated_at: string;
  completed_at: string | null;
  error_message: string | null;
  report_ready: boolean;
}

export function isTerminalStatus(status: JobStatusValue): boolean {
  return status === "complete" || status === "failed";
}
