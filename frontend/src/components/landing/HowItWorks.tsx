import {
  CalendarPlus,
  CheckCircle,
  Package,
  MagnifyingGlass,
  ArrowBendDownRight,
  type Icon,
} from "@phosphor-icons/react";
import { Section } from "@/components/ui/Section";
import { Reveal } from "@/components/motion/Reveal";

type Step = { title: string; body: string; Icon: Icon };

const STEPS: Step[] = [
  {
    title: "Reserve",
    body: "A club books a slot. The kit is held and a deposit goes on hold while the booking stays pending.",
    Icon: CalendarPlus,
  },
  {
    title: "Confirm",
    body: "The club confirms before the hold deadline. Miss it and a sweep auto-rejects the booking and frees the kit.",
    Icon: CheckCircle,
  },
  {
    title: "Check out",
    body: "Once confirmed, the kit is handed over and custody passes to the club for the length of its slot.",
    Icon: Package,
  },
  {
    title: "Return and inspect",
    body: "The kit comes back and runs a 15-minute inspection. Any damage is logged against whoever just held it.",
    Icon: MagnifyingGlass,
  },
  {
    title: "Hand off",
    body: "A clean pass sets the next club's effective start. A late return shifts that time and the delay cascades forward.",
    Icon: ArrowBendDownRight,
  },
];

export function HowItWorks() {
  return (
    <Section id="how">
      <Reveal className="max-w-2xl">
        <h2 className="text-3xl font-semibold tracking-[-0.015em] text-fg md:text-4xl">
          How one kit moves through a day
        </h2>
        <p className="mt-4 max-w-[60ch] text-base leading-relaxed text-fg-muted">
          Every booking rides the same path, from a soft hold to a clean handoff.
        </p>
      </Reveal>

      <ol className="mt-12 md:mt-14">
        {STEPS.map((s, i) => (
          <Reveal
            as="li"
            key={s.title}
            delay={i * 0.08}
            className="relative flex gap-5 pb-10 last:pb-0"
          >
            <div className="flex flex-col items-center">
              <span className="z-10 flex h-11 w-11 shrink-0 items-center justify-center rounded-full border border-border bg-surface text-accent">
                <s.Icon size={20} weight="regular" />
              </span>
              {i < STEPS.length - 1 && <span className="mt-1 w-px flex-1 bg-border" />}
            </div>
            <div className="pt-1.5">
              <h3 className="text-lg font-semibold text-fg">{s.title}</h3>
              <p className="mt-1.5 max-w-[54ch] text-sm leading-relaxed text-fg-muted">{s.body}</p>
            </div>
          </Reveal>
        ))}
      </ol>
    </Section>
  );
}
