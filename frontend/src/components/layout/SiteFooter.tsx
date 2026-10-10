import { Link } from "react-router-dom";
import { Container } from "@/components/ui/Container";
import { Logo } from "./Logo";

const COLS: { heading: string; links: { label: string; href: string; to?: string }[] }[] = [
  {
    heading: "Product",
    links: [
      { label: "How it works", href: "#how" },
      { label: "Features", href: "#features" },
      { label: "Reliability", href: "#reliability" },
    ],
  },
  {
    heading: "Dashboard",
    links: [
      { label: "Kit inventory", href: "", to: "/app" },
      { label: "Reservations", href: "", to: "/app" },
    ],
  },
];

export function SiteFooter() {
  return (
    <footer className="border-t border-border bg-surface">
      <Container className="py-14">
        <div className="grid gap-10 md:grid-cols-[1.4fr_1fr_1fr]">
          <div className="max-w-xs">
            <Logo />
            <p className="mt-4 text-sm leading-relaxed text-fg-muted">
              One shared AV kit, relayed across college clubs with an inspection between every
              handoff.
            </p>
          </div>
          {COLS.map((col) => (
            <nav key={col.heading} aria-label={col.heading}>
              <h3 className="text-sm font-semibold text-fg">{col.heading}</h3>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    {l.to ? (
                      <Link to={l.to} className="text-sm text-fg-muted transition-colors hover:text-fg">
                        {l.label}
                      </Link>
                    ) : (
                      <a href={l.href} className="text-sm text-fg-muted transition-colors hover:text-fg">
                        {l.label}
                      </a>
                    )}
                  </li>
                ))}
              </ul>
            </nav>
          ))}
        </div>
        <div className="mt-12 flex flex-col gap-2 border-t border-border pt-6 text-xs text-fg-faint sm:flex-row sm:items-center sm:justify-between">
          <span>Relay, a college event kit relay.</span>
          <span>Scaffold build. Add authentication before any shared deployment.</span>
        </div>
      </Container>
    </footer>
  );
}
