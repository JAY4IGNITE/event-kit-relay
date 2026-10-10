import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { apiPost } from "@/api/client";
import type { ReservationOut } from "@/api/schema";

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
    mutationFn: (rid: string) => apiPost(`/reservations/${rid}/confirm`),
  });

  return (
    <div>
      <button onClick={() => create.mutate()} disabled={create.isPending}>
        Create reservation (soft hold)
      </button>
      {last && (
        <div style={{ marginTop: 12 }}>
          <code>
            {last.reservation_id} — {last.status}
          </code>{" "}
          <button onClick={() => confirm.mutate(last.reservation_id)} disabled={confirm.isPending}>
            Confirm within hold window
          </button>
          <p style={{ color: "#777", fontSize: 13 }}>
            If not confirmed before the hold deadline, the pending-expiry cron auto-rejects it
            (status → EXPIRED).
          </p>
        </div>
      )}
    </div>
  );
}
