import { ArrowRight } from "@phosphor-icons/react";
import { motion, useReducedMotion } from "motion/react";
import { Button } from "@/components/ui/Button";
import { Container } from "@/components/ui/Container";
import { RelayTimeline } from "./RelayTimeline";

const EASE = [0.16, 1, 0.3, 1] as const;

export function Hero() {
  const reduce = useReducedMotion();
  const rise = (delay: number) => ({
    initial: reduce ? false : { opacity: 0, y: 22 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.7, delay, ease: EASE },
  });

  return (
    <div className="relative overflow-hidden border-b border-border">
      <Container className="grid min-h-[calc(100dvh-4rem)] items-center gap-12 py-12 pt-10 md:grid-cols-[1.05fr_0.95fr] md:gap-10 md:pt-16 lg:gap-16">
        <div className="max-w-xl">
          <motion.h1
            {...rise(0.05)}
            className="text-[2.6rem] font-semibold leading-[1.04] tracking-[-0.02em] text-fg sm:text-5xl md:text-6xl"
          >
            One kit. Every club. <span className="text-accent">No collisions.</span>
          </motion.h1>

          <motion.p
            {...rise(0.16)}
            className="mt-6 max-w-[46ch] text-base leading-relaxed text-fg-muted md:text-lg"
          >
            One shared camera, mic, tripod and light kit, relayed through back-to-back club
            slots with a 15-minute inspection between every handoff.
          </motion.p>

          <motion.div {...rise(0.27)} className="mt-9 flex flex-wrap items-center gap-3">
            <Button to="/app" size="lg">
              Open dashboard
              <ArrowRight size={18} weight="bold" />
            </Button>
            <Button href="#how" variant="ghost" size="lg">
              See how it works
            </Button>
          </motion.div>
        </div>

        <motion.div
          initial={reduce ? false : { opacity: 0, y: 28, scale: 0.98 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.3, ease: EASE }}
        >
          <RelayTimeline />
        </motion.div>
      </Container>
    </div>
  );
}
