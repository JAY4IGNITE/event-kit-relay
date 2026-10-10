import { Link } from "react-router-dom";

/** Minimal geometric mark: a kit token travelling a track past a handoff chevron. */
export function RelayMark({ className = "" }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" className={className} aria-hidden="true" fill="none">
      <path d="M3 12H21" stroke="currentColor" strokeWidth="2" strokeLinecap="round" opacity="0.3" />
      <path
        d="M13 7l5 5-5 5"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="7" cy="12" r="3.2" fill="var(--accent-hi)" />
    </svg>
  );
}

export function Logo() {
  return (
    <Link to="/" className="group inline-flex items-center gap-2.5" aria-label="Relay home">
      <RelayMark className="h-6 w-6 text-fg transition-transform duration-300 group-hover:translate-x-0.5" />
      <span className="text-[1.05rem] font-semibold tracking-tight text-fg">Relay</span>
    </Link>
  );
}
