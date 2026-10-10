import { useState } from "react";
import type { ReactNode } from "react";
import { Shield, UserCircle } from "@phosphor-icons/react";
import { AppShell } from "@/components/layout/AppShell";
import { KitList } from "@/features/inventory/KitList";
import { ReservationPanel } from "@/features/reservations/ReservationPanel";

type TabId = "organizer" | "club";
const TABS = [
  { id: "organizer" as const, label: "Organizer", Icon: Shield },
  { id: "club" as const, label: "Club", Icon: UserCircle },
];

export function Dashboard() {
  const [tab, setTab] = useState<TabId>("organizer");

  return (
    <AppShell>
      <div className="flex flex-col gap-6">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-fg">Relay dashboard</h1>
          <p className="mt-1 text-sm text-fg-muted">
            One kit, one timeline. Switch sides of the counter below.
          </p>
        </div>

        <div
          role="tablist"
          aria-label="Dashboard view"
          className="inline-flex w-fit rounded-full border border-border bg-surface p-1"
        >
          {TABS.map((t) => {
            const active = tab === t.id;
            return (
              <button
                key={t.id}
                role="tab"
                aria-selected={active}
                onClick={() => setTab(t.id)}
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2 text-sm font-medium transition-colors ${
                  active ? "bg-accent-hi text-accent-ink" : "text-fg-muted hover:text-fg"
                }`}
              >
                <t.Icon size={16} weight="regular" />
                {t.label}
              </button>
            );
          })}
        </div>

        {tab === "organizer" ? (
          <Panel title="Kit inventory" caption="Status of every kit on the relay.">
            <KitList />
          </Panel>
        ) : (
          <Panel title="Reservations" caption="Create a soft hold and confirm it within the window.">
            <ReservationPanel />
          </Panel>
        )}
      </div>
    </AppShell>
  );
}

function Panel({ title, caption, children }: { title: string; caption: string; children: ReactNode }) {
  return (
    <section className="rounded-2xl border border-border bg-surface">
      <div className="border-b border-border px-5 py-4">
        <h2 className="text-base font-semibold text-fg">{title}</h2>
        <p className="mt-0.5 text-sm text-fg-muted">{caption}</p>
      </div>
      <div className="p-5">{children}</div>
    </section>
  );
}
