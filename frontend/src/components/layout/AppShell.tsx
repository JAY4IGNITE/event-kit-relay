import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ArrowLeft } from "@phosphor-icons/react";
import { Logo } from "./Logo";
import { ThemeToggle } from "./ThemeToggle";

/** Chrome for the /app surface. Same tokens and shell language as the site. */
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <div className="min-h-dvh bg-bg text-fg">
      <header className="sticky top-0 z-40 border-b border-border bg-bg/70 backdrop-blur-md">
        <div className="mx-auto flex h-16 w-full max-w-6xl items-center justify-between px-4 sm:px-6 lg:px-8">
          <Logo />
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Link
              to="/"
              className="inline-flex h-10 items-center gap-2 rounded-full border border-border px-4 text-sm text-fg-muted transition-colors hover:bg-surface-2 hover:text-fg"
            >
              <ArrowLeft size={16} weight="bold" />
              Back to site
            </Link>
          </div>
        </div>
      </header>
      <main className="mx-auto w-full max-w-6xl px-4 py-10 sm:px-6 lg:px-8 lg:py-12">{children}</main>
    </div>
  );
}
