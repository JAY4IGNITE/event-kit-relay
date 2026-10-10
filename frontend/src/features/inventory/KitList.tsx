import { useQuery } from "@tanstack/react-query";
import { CheckCircle, XCircle } from "@phosphor-icons/react";
import type { ReactNode } from "react";
import { apiGet } from "@/api/client";
import type { KitOut } from "@/api/schema";

// Semantic status dots: real state, not decoration.
const DOT: Record<string, string> = {
  AVAILABLE: "bg-emerald-500",
  AWAITING_INSPECTION: "bg-accent-hi",
  CHECKED_OUT: "bg-sky-500",
  RESERVED: "bg-sky-500",
  DAMAGED: "bg-rose-500",
  OUT_OF_SERVICE: "bg-rose-500",
};

export function KitList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["kits"],
    queryFn: () => apiGet<KitOut[]>("/kits"),
  });

  if (isLoading) return <SkeletonTable />;
  if (error) return <StateNote tone="error">Could not load kits. Check that the backend is running.</StateNote>;
  if (!data?.length) return <StateNote>No kits registered yet. Add one from the backend to see it here.</StateNote>;

  return (
    <div className="overflow-x-auto rounded-xl border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-surface-2/50 text-left font-mono text-[11px] uppercase tracking-[0.12em] text-fg-faint">
            <th className="px-4 py-3 font-medium">Kit</th>
            <th className="px-4 py-3 font-medium">Status</th>
            <th className="px-4 py-3 text-right font-medium">Complete</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-border">
          {data.map((k) => (
            <tr key={k.kit_id} className="transition-colors hover:bg-surface-2/40">
              <td className="px-4 py-3 font-mono text-fg">{k.kit_id}</td>
              <td className="px-4 py-3">
                <span className="inline-flex items-center gap-2 text-fg">
                  <span className={`h-2 w-2 rounded-full ${DOT[k.status] ?? "bg-fg-faint"}`} />
                  {k.status}
                </span>
              </td>
              <td className="px-4 py-3 text-right">
                {k.complete ? (
                  <CheckCircle className="inline text-accent" size={18} weight="fill" />
                ) : (
                  <XCircle className="inline text-fg-faint" size={18} />
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function SkeletonTable() {
  return (
    <div className="overflow-hidden rounded-xl border border-border" aria-busy="true">
      <div className="divide-y divide-border">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="flex items-center gap-4 px-4 py-3.5">
            <div className="h-3 w-28 rounded bg-surface-2 motion-safe:animate-pulse" />
            <div className="h-3 w-24 rounded bg-surface-2 motion-safe:animate-pulse" />
            <div className="ml-auto h-3 w-9 rounded bg-surface-2 motion-safe:animate-pulse" />
          </div>
        ))}
      </div>
    </div>
  );
}

function StateNote({ children, tone = "muted" }: { children: ReactNode; tone?: "muted" | "error" }) {
  return (
    <div
      className={`rounded-xl border border-dashed border-border px-5 py-10 text-center text-sm ${
        tone === "error" ? "text-rose-500" : "text-fg-muted"
      }`}
    >
      {children}
    </div>
  );
}
