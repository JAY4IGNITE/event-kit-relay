import { Section } from "@/components/ui/Section";
import { Reveal } from "@/components/motion/Reveal";

type Role = {
  name: string;
  line: string;
  seed: string;
  actions: string[];
};

const ROLES: Role[] = [
  {
    name: "Clubs",
    line: "Book it, use it, bring it back clean.",
    seed: "relay-club-film-shoot",
    actions: [
      "Reserve a slot and confirm before the hold runs out",
      "Check the kit out for the length of your event",
      "Return on time to keep your deposit and loyalty intact",
    ],
  },
  {
    name: "Organizers",
    line: "Keep the kit moving, and keep it honest.",
    seed: "relay-av-inspection-bench",
    actions: [
      "Inspect every return inside the 15-minute window",
      "Log damage, then replace, reroute or cancel",
      "Warn clubs and settle deposits as returns land",
    ],
  },
];

export function Personas() {
  return (
    <Section>
      <Reveal className="max-w-2xl">
        <h2 className="text-3xl font-semibold tracking-[-0.015em] text-fg md:text-4xl">
          Two sides of the counter
        </h2>
        <p className="mt-4 max-w-[60ch] text-base leading-relaxed text-fg-muted">
          Relay gives each side exactly what it needs, and lets the scheduler handle the clock.
        </p>
      </Reveal>

      <div className="mt-12 grid gap-5 md:grid-cols-2">
        {ROLES.map((role, i) => (
          <Reveal key={role.name} delay={i * 0.1}>
            <article className="group flex h-full flex-col overflow-hidden rounded-2xl border border-border bg-surface">
              <div className="relative aspect-[16/9] overflow-hidden bg-surface-2">
                <img
                  src={`https://picsum.photos/seed/${role.seed}/800/450`}
                  alt=""
                  loading="lazy"
                  width={800}
                  height={450}
                  className="h-full w-full object-cover grayscale transition-[filter,transform] duration-500 group-hover:scale-[1.03] group-hover:grayscale-0"
                />
              </div>
              <div className="flex flex-1 flex-col p-6">
                <h3 className="text-xl font-semibold text-fg">{role.name}</h3>
                <p className="mt-1 text-sm text-fg-muted">{role.line}</p>
                <ul className="mt-5 space-y-3 border-t border-border pt-5">
                  {role.actions.map((a) => (
                    <li key={a} className="flex gap-3 text-sm leading-relaxed text-fg">
                      <span className="mt-2 h-1 w-4 shrink-0 rounded-full bg-accent" />
                      {a}
                    </li>
                  ))}
                </ul>
              </div>
            </article>
          </Reveal>
        ))}
      </div>
    </Section>
  );
}
