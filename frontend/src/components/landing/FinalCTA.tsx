import { ArrowRight } from "@phosphor-icons/react";
import { Container } from "@/components/ui/Container";
import { Button } from "@/components/ui/Button";
import { Reveal } from "@/components/motion/Reveal";
import { RelayMark } from "@/components/layout/Logo";

export function FinalCTA() {
  return (
    <section className="py-20 md:py-28">
      <Container>
        <Reveal>
          <div className="relative overflow-hidden rounded-2xl border border-border bg-surface-2 px-6 py-14 text-center md:px-10 md:py-20">
            <RelayMark className="mx-auto mb-6 h-9 w-9 text-fg" />
            <h2 className="mx-auto max-w-[16ch] text-3xl font-semibold tracking-[-0.02em] text-fg md:text-5xl">
              Put one kit to work across every club
            </h2>
            <p className="mx-auto mt-4 max-w-[46ch] text-base leading-relaxed text-fg-muted">
              Open the dashboard, line up the bookings, and let the relay run itself.
            </p>
            <div className="mt-9 flex justify-center">
              <Button to="/app" size="lg">
                Open dashboard
                <ArrowRight size={18} weight="bold" />
              </Button>
            </div>
          </div>
        </Reveal>
      </Container>
    </section>
  );
}
