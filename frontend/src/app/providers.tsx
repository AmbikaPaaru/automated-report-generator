"use client";

import { useState } from "react";
import { Provider } from "react-redux";

import { makeStore } from "@/lib/store";

export function Providers({ children }: { children: React.ReactNode }) {
  // Lazy useState initializer: runs makeStore() exactly once on mount, without
  // touching a ref's .current during render (which the newer react-hooks rules
  // flag as unsafe under the React Compiler's assumptions).
  const [store] = useState(makeStore);

  return <Provider store={store}>{children}</Provider>;
}
