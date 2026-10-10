import { motion, useReducedMotion } from "motion/react";
import type { ReactNode } from "react";

const EASE = [0.16, 1, 0.3, 1] as const;
const MAP = { div: motion.div, li: motion.li, span: motion.span };

/** Fade-and-rise on scroll into view. Collapses to static under reduced motion. */
export function Reveal({
  children,
  delay = 0,
  y = 20,
  className = "",
  as = "div",
}: {
  children: ReactNode;
  delay?: number;
  y?: number;
  className?: string;
  as?: keyof typeof MAP;
}) {
  const reduce = useReducedMotion();
  const Comp = MAP[as] as typeof motion.div;
  return (
    <Comp
      className={className}
      initial={reduce ? false : { opacity: 0, y }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.3 }}
      transition={{ duration: 0.6, delay, ease: EASE }}
    >
      {children}
    </Comp>
  );
}
