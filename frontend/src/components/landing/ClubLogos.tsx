import { Container } from "@/components/ui/Container";
import { Reveal } from "@/components/motion/Reveal";
import { CLUBS } from "@/lib/clubs";
import { Monogram } from "./Monogram";

/** Social proof: the clubs that share one kit on the relay. Marks only, no labels. */
export function ClubLogos() {
  return (
    <div className="border-b border-border py-14">
      <Container>
        <Reveal>
          <p className="text-center text-sm text-fg-faint">
            One kit relayed across six campus clubs this term.
          </p>
        </Reveal>
        <ul className="mt-9 grid grid-cols-2 gap-x-6 gap-y-7 sm:grid-cols-3 lg:grid-cols-6">
          {CLUBS.map((club, i) => (
            <Reveal
              as="li"
              key={club.name}
              delay={i * 0.05}
              className="group flex items-center justify-center gap-2.5 text-fg-faint transition-colors hover:text-fg"
            >
              <Monogram club={club} size={30} />
              <span className="text-[13px] font-medium leading-tight">{club.name}</span>
            </Reveal>
          ))}
        </ul>
      </Container>
    </div>
  );
}
