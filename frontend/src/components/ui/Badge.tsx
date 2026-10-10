import type { ReactNode } from "react";

/**
 * Small mono-caps chip. Used sparingly for status / category where it earns
 * its place, NOT as a per-section eyebrow (see eyebrow restraint rule).
 */
export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "accent";
}) {
  const tones = {
    neutral: "border-border text-fg-muted",
    accent: "border-accent/40 text-accent",
  } as const;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1 font-mono text-[11px] uppercase tracking-[0.14em] ${tones[tone]}`}
    >
      {children}
    </span>
  );
}
