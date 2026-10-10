import { lazy, Suspense } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Landing } from "@/routes/Landing";

// Keep the dashboard (and its data layer) out of the landing page's initial chunk.
const Dashboard = lazy(() =>
  import("@/routes/Dashboard").then((m) => ({ default: m.Dashboard })),
);

/**
 * Two surfaces share one shell language:
 *   /      marketing landing page (public entry point)
 *   /app   organizer + club dashboards, wrapped in the app shell
 */
export function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route
          path="/app"
          element={
            <Suspense fallback={<div className="min-h-dvh bg-bg" />}>
              <Dashboard />
            </Suspense>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
