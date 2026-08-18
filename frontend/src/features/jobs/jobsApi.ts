/**
 * RTK Query slice for the 3 backend calls this app needs:
 *  - createJob:    POST /jobs            (upload + kick off the pipeline)
 *  - getJobStatus: GET  /jobs/{id}       (polled by the component, see JobStatusCard)
 *  - downloadUrlFor(): GET /jobs/{id}/download -- not fetched via JS, just linked to
 *    directly so the browser handles the file download/Content-Disposition itself.
 */

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import type { JobCreateResponse, JobStatusResponse } from "./types";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export const jobsApi = createApi({
  reducerPath: "jobsApi",
  baseQuery: fetchBaseQuery({ baseUrl: API_BASE_URL }),
  tagTypes: ["Job"],
  endpoints: (builder) => ({
    createJob: builder.mutation<JobCreateResponse, File>({
      query: (file) => {
        const formData = new FormData();
        formData.append("file", file);
        return { url: "/jobs", method: "POST", body: formData };
      },
      invalidatesTags: (result) =>
        result ? [{ type: "Job", id: result.id }] : [],
    }),

    getJobStatus: builder.query<JobStatusResponse, string>({
      query: (jobId) => `/jobs/${jobId}`,
      providesTags: (_result, _error, jobId) => [{ type: "Job", id: jobId }],
    }),
  }),
});

export const { useCreateJobMutation, useGetJobStatusQuery } = jobsApi;

export function downloadUrlFor(jobId: string): string {
  return `${API_BASE_URL}/jobs/${jobId}/download`;
}
