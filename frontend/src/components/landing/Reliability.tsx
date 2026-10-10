import { HourglassMedium, UserMinus, type Icon } from "@phosphor-icons/react";
import { Section } from "@/components/ui/Section";
import { Reveal } from "@/components/motion/Reveal";

const METRICS = [
  { value: "100%", label: "of returned kits pass an inspection before anyone reuses them" },
  { value: "0", label: "double-bookings of one kit under concurrent requests" },
  { value: "≤60s", label: "from a hold's deadline to automatic expiry" },
];

const SWEEPS: { Icon: Icon; title: string; body: string }[] = [
  {
    Icon: HourglassMedium,
    title: "Pending-expiry sweep",
    body: "Watches soft holds. When a hold deadline passes, the booking flips to expired, the kit is released and the deposit is voided.",
  },
  {
    Icon: UserMinus,
    title: "No-show sweep",
    body: "Watches confirmed bookings that never check out. Past the grace period it flags a no-show and forfeits the deposit.",
  },
];

export function Reliability() {
  return (
    <Section id="reliability" tint>
      <Reveal className="max-w-2xl">
        <h2 className="text-3xl font-semibold tracking-[-0.015em] text-fg md:text-4xl">
          Two sweeps keep the schedule true
        </h2>
        <p className="mt-4 max-w-[62ch] text-base leading-relaxed text-fg-muted">
          Time moves whether or not anyone clicks. Relay runs recurring sweeps that read the clock,
          reconcile state, and catch up on their own after any downtime.
        </p>
      </Reveal>

      <div className="mt-12 grid gap-px overflow-hidden rounded-2xl border border-border bg-border sm:grid-cols-3">
        {METRICS.map((m, i) => (
          <Reveal key={m.value} delay={i * 0.08} className="bg-surface p-6">
            <div className="text-4xl font-semibold tracking-tight tabular-nums text-fg md:text-5xl">
              {m.value}
            </div>
            <p className="mt-2 text-sm leading-relaxed text-fg-muted">{m.label}</p>
          </Reveal>
        ))}
      </div>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        {SWEEPS.map((s, i) => (
          <Reveal key={s.title} delay={i * 0.08}>
            <article className="h-full rounded-2xl border border-border bg-surface p-6">
              <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-accent">
                <s.Icon size={20} weight="regular" />
              </span>
              <h3 className="mt-4 text-base font-semibold text-fg">{s.title}</h3>
              <p className="mt-1.5 text-sm leading-relaxed text-fg-muted">{s.body}</p>
            </article>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
