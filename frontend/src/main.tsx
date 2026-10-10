import React from "react";
import ReactDOM from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Self-hosted variable fonts (no external <link>, swap-friendly).
import "@fontsource-variable/geist";
import "@fontsource-variable/geist-mono";
import "./index.css";

import { App } from "./App";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // relay/schedule state changes over time — poll on an interval
      refetchInterval: 30_000,
      staleTime: 10_000,
    },
  },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
