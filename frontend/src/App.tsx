import { KitList } from "@/features/inventory/KitList";
import { ReservationPanel } from "@/features/reservations/ReservationPanel";

/**
 * Root shell. Two dashboards share this page in v1:
 *  - Organizer: kit inventory + inspection actions
 *  - Club: create/confirm reservations
 * Routing can be split later with react-router-dom.
 */
export function App() {
  return (
    <main style={{ fontFamily: "system-ui", maxWidth: 960, margin: "2rem auto", padding: "0 1rem" }}>
      <h1>College Event Kit Relay</h1>
      <p style={{ color: "#555" }}>
        Shared AV kits relayed between clubs with a mandatory 15-minute inspection window.
      </p>
      <section>
        <h2>Kits</h2>
        <KitList />
      </section>
      <section>
        <h2>Reservations</h2>
        <ReservationPanel />
      </section>
    </main>
  );
}
