import {
  ArrowsClockwise,
  ArrowBendUpRight,
  XCircle,
  CaretRight,
  type Icon,
} from "@phosphor-icons/react";
import { Section } from "@/components/ui/Section";
import { Reveal } from "@/components/motion/Reveal";

type Rung = { title: string; body: string; Icon: Icon };

const LADDER: Rung[] = [
  { title: "Replace", body: "Swap the broken item for a spare and keep the booking on schedule.", Icon: ArrowsClockwise },
  { title: "Reroute", body: "No spare for it? Move the booking onto another kit that can cover the slot.", Icon: ArrowBendUpRight },
  { title: "Cancel", body: "No kit fits? Cancel cleanly, settle the deposit and notify the club.", Icon: XCircle },
];

export function InspectionWindow() {
  return (
    <Section tint>
      <Reveal className="max-w-2xl">
        <h2 className="text-3xl font-semibold tracking-[-0.015em] text-fg md:text-4xl">
          Every return runs the inspection
        </h2>
        <p className="mt-4 max-w-[60ch] text-base leading-relaxed text-fg-muted">
          The 15-minute window checks each item before the next club can touch the kit. When
          something fails, Relay works down one fixed ladder.
        </p>
      </Reveal>

      <Reveal delay={0.1} className="mt-6">
        <p className="max-w-[62ch] border-l-2 border-accent pl-4 text-sm leading-relaxed text-fg">
          Damage sticks to whoever held the kit, never the club that receives it next.
        </p>
      </Reveal>

      <div className="mt-12 flex flex-col gap-3 md:flex-row md:items-stretch">
        {LADDER.map((rung, i) => (
          <div key={rung.title} className="flex flex-col md:flex-1 md:flex-row md:items-stretch">
            <Reveal delay={i * 0.1} className="flex-1">
              <div className="h-full rounded-2xl border border-border bg-surface p-6">
                <span className="inline-flex h-10 w-10 items-center justify-center rounded-full bg-accent/10 text-accent">
                  <rung.Icon size={20} weight="regular" />
                </span>
                <h3 className="mt-4 text-base font-semibold text-fg">{rung.title}</h3>
                <p className="mt-1.5 text-sm leading-relaxed text-fg-muted">{rung.body}</p>
              </div>
            </Reveal>
            {i < LADDER.length - 1 && (
              <div className="flex items-center justify-center py-1 text-fg-faint md:px-1">
                <CaretRight size={18} weight="bold" className="rotate-90 md:rotate-0" />
              </div>
            )}
          </div>
        ))}
      </div>
    </Section>
  );
}
