import type { ReactNode } from "react";
import { Link } from "react-router-dom";

type Variant = "primary" | "ghost";
type Size = "md" | "lg";

const base =
  "inline-flex items-center justify-center gap-2 rounded-full font-medium whitespace-nowrap " +
  "transition-[transform,background-color,border-color,color,filter] duration-200 ease-out " +
  "active:translate-y-px active:scale-[0.985] focus-visible:outline-none select-none " +
  "disabled:pointer-events-none disabled:opacity-55";

const sizes: Record<Size, string> = {
  md: "h-10 px-5 text-sm",
  lg: "h-12 px-7 text-[0.95rem]",
};

const variants: Record<Variant, string> = {
  // amber fill + ink text => WCAG AA contrast in both themes
  primary: "bg-accent-hi text-accent-ink hover:brightness-[1.06]",
  ghost: "border border-border bg-transparent text-fg hover:bg-surface-2",
};

type ButtonProps = {
  children: ReactNode;
  variant?: Variant;
  size?: Size;
  className?: string;
  to?: string;
  href?: string;
} & Record<string, unknown>;

export function Button({
  children,
  variant = "primary",
  size = "md",
  className = "",
  to,
  href,
  ...rest
}: ButtonProps) {
  const cls = `${base} ${sizes[size]} ${variants[variant]} ${className}`;
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const extra = rest as any;

  if (to) {
    return (
      <Link to={to} className={cls} {...extra}>
        {children}
      </Link>
    );
  }
  if (href) {
    return (
      <a href={href} className={cls} {...extra}>
        {children}
      </a>
    );
  }
  return (
    <button className={cls} {...extra}>
      {children}
    </button>
  );
}
