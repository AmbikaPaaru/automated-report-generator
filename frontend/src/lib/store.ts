/**
 * Store factory (not a module-level singleton) per Redux Toolkit's recommended
 * pattern for Next.js App Router -- Providers.tsx creates one instance per mount
 * via useRef so state can't leak across requests/users during SSR.
 */

import { configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";

import { jobsApi } from "@/features/jobs/jobsApi";

export function makeStore() {
  const store = configureStore({
    reducer: {
      [jobsApi.reducerPath]: jobsApi.reducer,
    },
    middleware: (getDefaultMiddleware) =>
      getDefaultMiddleware().concat(jobsApi.middleware),
  });

  setupListeners(store.dispatch);
  return store;
}

export type AppStore = ReturnType<typeof makeStore>;
export type RootState = ReturnType<AppStore["getState"]>;
export type AppDispatch = AppStore["dispatch"];
