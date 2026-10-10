import type { ReactNode } from "react";
import { Container } from "./Container";

/** Section with the one vertical-rhythm scale. `tint` shifts the band within
 *  the same theme family (surface-2), never into an inverted theme. */
export function Section({
  id,
  children,
  tint = false,
  className = "",
}: {
  id?: string;
  children: ReactNode;
  tint?: boolean;
  className?: string;
}) {
  return (
    <section
      id={id}
      className={`scroll-mt-24 py-20 md:py-28 ${tint ? "bg-surface-2" : ""} ${className}`}
    >
      <Container>{children}</Container>
    </section>
  );
}
