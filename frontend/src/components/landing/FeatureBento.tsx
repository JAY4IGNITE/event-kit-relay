import { Coins, BellRinging, ShieldCheck, Medal, type Icon } from "@phosphor-icons/react";
import { Section } from "@/components/ui/Section";
import { Badge } from "@/components/ui/Badge";
import { Reveal } from "@/components/motion/Reveal";

export function FeatureBento() {
  return (
    <Section id="features">
      <Reveal className="max-w-2xl">
        <Badge tone="accent">Capabilities</Badge>
        <h2 className="mt-4 text-3xl font-semibold tracking-[-0.015em] text-fg md:text-4xl">
          The scheduling logic, handled
        </h2>
        <p className="mt-4 max-w-[60ch] text-base leading-relaxed text-fg-muted">
          Relay keeps the chain honest end to end: the times, the money, the trust, and the
          messages that go out the moment a plan changes.
        </p>
      </Reveal>

      <div className="mt-12 grid grid-cols-1 gap-4 md:auto-rows-[1fr] md:grid-cols-6">
        <Reveal className="md:col-span-4 md:row-span-2">
          <article className="flex h-full flex-col rounded-2xl border border-border bg-surface p-6 md:p-8">
            <h3 className="text-xl font-semibold text-fg">Delays cascade, booked times stay put</h3>
            <p className="mt-2 max-w-[48ch] text-sm leading-relaxed text-fg-muted">
              A late return shifts every later club's effective start by the overrun. The original
              booking is preserved untouched, so the record and the operating schedule never blur.
            </p>
            <div className="mt-auto pt-8">
              <DelayDiagram />
            </div>
          </article>
        </Reveal>

        <Reveal delay={0.06} className="md:col-span-2">
          <Cell
            tint
            icon={Coins}
            title="Deposits settle themselves"
            body="Held on booking, refunded on a clean on-time return, forfeited when it is not."
          />
        </Reveal>

        <Reveal delay={0.12} className="md:col-span-2">
          <LoyaltyCell />
        </Reveal>

        <Reveal delay={0.06} className="md:col-span-3">
          <Cell
            icon={BellRinging}
            title="Nothing changes silently"
            body="Delay, damage, reroute, cancel or expiry: the affected clubs and organizers all get told."
          />
        </Reveal>

        <Reveal delay={0.12} className="md:col-span-3">
          <Cell
            icon={ShieldCheck}
            title="A kit must be whole to go out"
            body="Incomplete or damaged kits cannot be reserved or handed over. No exceptions at the counter."
          />
        </Reveal>
      </div>
    </Section>
  );
}

function Cell({
  icon: Ico,
  title,
  body,
  tint = false,
}: {
  icon: Icon;
  title: string;
  body: string;
  tint?: boolean;
}) {
  return (
    <article
      className={`flex h-full flex-col rounded-2xl border border-border p-6 ${
        tint ? "bg-accent/[0.06]" : "bg-surface"
      }`}
    >
      <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-accent">
        <Ico size={20} weight="regular" />
      </span>
      <h3 className="mt-4 text-base font-semibold text-fg">{title}</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-fg-muted">{body}</p>
    </article>
  );
}

function LoyaltyCell() {
  return (
    <article className="flex h-full flex-col rounded-2xl border border-border bg-surface p-6">
      <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-accent">
        <Medal size={20} weight="regular" />
      </span>
      <h3 className="mt-4 text-base font-semibold text-fg">Loyalty gates who can book</h3>
      <p className="mt-1.5 text-sm leading-relaxed text-fg-muted">
        A club's score tracks its history. Dip below the line and new bookings pause until it recovers.
      </p>
      <div className="mt-auto pt-5">
        <div className="relative h-2 w-full rounded-full bg-surface-2">
          <div className="h-full w-[64%] rounded-full bg-accent-hi" />
          <span className="absolute left-1/2 top-1/2 h-3.5 w-px -translate-y-1/2 bg-fg/40" />
        </div>
        <div className="mt-2 flex justify-between font-mono text-[10px] text-fg-faint">
          <span>below pauses booking</span>
          <span>eligible</span>
        </div>
      </div>
    </article>
  );
}

function DelayDiagram() {
  return (
    <div className="font-mono text-[11px]">
      <div className="mb-1.5 text-fg-faint">booked</div>
      <div className="relative h-7 overflow-hidden rounded-lg bg-surface-2">
        <div className="absolute left-0 top-0 flex h-full w-[46%] items-center rounded-lg border border-border bg-fg/[0.06] px-2.5 text-fg-muted">
          14:00
        </div>
      </div>
      <div className="mb-1.5 mt-3 text-fg-faint">effective</div>
      <div className="relative h-7 overflow-hidden rounded-lg bg-surface-2">
        <div className="inspect-hatch absolute left-0 top-0 h-full w-[13%]" />
        <div className="absolute left-[13%] top-0 flex h-full w-[46%] items-center rounded-lg border border-accent/40 bg-accent/15 px-2.5 text-accent">
          14:15
        </div>
      </div>
      <div className="mt-2.5 text-fg-faint">+15m carried forward</div>
    </div>
  );
}
