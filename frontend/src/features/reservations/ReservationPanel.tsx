import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { ArrowRight, Warning } from "@phosphor-icons/react";
import type { ReactNode } from "react";
import { apiPost } from "@/api/client";
import type { ReservationOut } from "@/api/schema";
import { Button } from "@/components/ui/Button";

/**
 * Minimal reservation creator. Demonstrates the create -> confirm handshake;
 * a real UI would add slot pickers and equipment selection.
 */
export function ReservationPanel() {
  const [last, setLast] = useState<ReservationOut | null>(null);

  const create = useMutation({
    mutationFn: () =>
      apiPost<ReservationOut>("/reservations", {
        club_id: "club-demo",
        required_types: ["CAMERA", "MIC", "TRIPOD"],
        start: new Date().toISOString(),
        end: new Date(Date.now() + 2 * 3600_000).toISOString(),
        idempotency_key: crypto.randomUUID(),
      }),
    onSuccess: setLast,
  });

  const confirm = useMutation({
    mutationFn: (rid: string) => apiPost<ReservationOut>(`/reservations/${rid}/confirm`),
    onSuccess: setLast,
  });

  return (
    <div className="flex flex-col gap-5">
      <div>
        <Button onClick={() => create.mutate()} disabled={create.isPending}>
          {create.isPending ? "Creating hold…" : "Create reservation (soft hold)"}
          {!create.isPending && <ArrowRight size={16} weight="bold" />}
        </Button>
        {create.isError && <InlineError>Could not create the reservation. Is the backend running?</InlineError>}
      </div>
      {last && (
        <div className="rounded-xl border border-border bg-surface-2/40 p-4">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="min-w-0">
              <div className="font-mono text-[11px] uppercase tracking-[0.12em] text-fg-faint">
                reservation
              </div>
              <div className="mt-0.5 truncate font-mono text-sm text-fg">{last.reservation_id}</div>
            </div>
            <StatusChip status={last.status} />
          </div>

          <dl className="mt-4 grid grid-cols-2 gap-3 font-mono text-xs">
            <div>
              <dt className="text-fg-faint">effective start</dt>
              <dd className="mt-0.5 text-fg">{fmt(last.effective_start)}</dd>
            </div>
            <div>
              <dt className="text-fg-faint">effective end</dt>
              <dd className="mt-0.5 text-fg">{fmt(last.effective_end)}</dd>
            </div>
          </dl>

          {last.status === "PENDING" && (
            <div className="mt-4">
              <Button
                variant="ghost"
                onClick={() => confirm.mutate(last.reservation_id)}
                disabled={confirm.isPending}
              >
                {confirm.isPending ? "Confirming…" : "Confirm within hold window"}
              </Button>
              {confirm.isError && <InlineError>Confirm failed. The hold may have expired.</InlineError>}
            </div>
          )}

          <p className="mt-4 text-xs leading-relaxed text-fg-muted">
            If it is not confirmed before the hold deadline, the pending-expiry sweep auto-rejects it
            and the status becomes EXPIRED.
          </p>
        </div>
      )}
    </div>
  );
}

const TONE: Record<string, string> = {
  PENDING: "border-accent/40 text-accent",
  CONFIRMED: "border-emerald-500/40 text-emerald-500",
  ACTIVE: "border-emerald-500/40 text-emerald-500",
  COMPLETED: "border-emerald-500/40 text-emerald-500",
  REROUTED: "border-sky-500/40 text-sky-500",
  CANCELLED: "border-rose-500/40 text-rose-500",
  NO_SHOW: "border-rose-500/40 text-rose-500",
  EXPIRED: "border-rose-500/40 text-rose-500",
};

function StatusChip({ status }: { status: string }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 font-mono text-[11px] tracking-wide ${
        TONE[status] ?? "border-border text-fg-muted"
      }`}
    >
      {status}
    </span>
  );
}

function fmt(iso: string) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" });
}

function InlineError({ children }: { children: ReactNode }) {
  return (
    <p className="mt-2 inline-flex items-center gap-1.5 text-xs text-rose-500">
      <Warning size={14} weight="fill" />
      {children}
    </p>
  );
}
