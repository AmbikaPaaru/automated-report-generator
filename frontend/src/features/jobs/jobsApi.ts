/**
 * RTK Query slice for the 3 backend calls this app needs:
 *  - createJob:    POST /jobs            (upload + kick off the pipeline)
 *  - getJobStatus: GET  /jobs/{id}       (polled by the component, see JobStatusCard)
 *  - downloadUrlFor(): GET /jobs/{id}/download -- not fetched via JS, just linked to
 *    directly so the browser handles the file download/Content-Disposition itself.
 */

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import type { JobCreateResponse, JobStatusResponse } from "./types";
import { isTerminalStatus } from "./types";

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
      // Live updates via Server-Sent Events instead of polling this query on an
      // interval. `query` above still runs once up front for the first paint;
      // this lifecycle hook then layers a push-based stream on top of that same
      // cache entry, so components keep calling the one hook (useGetJobStatusQuery)
      // exactly as before -- see backend GET /jobs/{id}/events for the server side.
      async onCacheEntryAdded(
        jobId,
        { updateCachedData, cacheDataLoaded, cacheEntryRemoved }
      ) {
        // Wait for the initial fetch to land in the cache before layering a stream
        // on top of it, so there's always a value to render immediately.
        await cacheDataLoaded;

        const source = new EventSource(`${API_BASE_URL}/jobs/${jobId}/events`);

        source.addEventListener("status", (event) => {
          const data = JSON.parse((event as MessageEvent<string>).data) as JobStatusResponse;
          updateCachedData(() => data);
          if (isTerminalStatus(data.status)) {
            // The backend already closes its end on a terminal status; closing here
            // too stops the browser's default auto-reconnect from re-opening it.
            source.close();
          }
        });

        // No manual reconnect logic: on a transient drop, EventSource retries on its
        // own by design. If the job doesn't exist, the backend sends one `error`
        // event and closes the stream itself rather than leaving it hanging.

        // Resolves when the last subscriber unmounts (e.g. JobStatusCard goes away).
        // Always close here too, so an abandoned job never leaks an open connection.
        await cacheEntryRemoved;
        source.close();
      },
    }),
  }),
});

export const { useCreateJobMutation, useGetJobStatusQuery } = jobsApi;

export function downloadUrlFor(jobId: string): string {
  return `${API_BASE_URL}/jobs/${jobId}/download`;
}
