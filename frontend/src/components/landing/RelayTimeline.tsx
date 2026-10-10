import { motion, useReducedMotion } from "motion/react";
import { CheckCircle, Timer, MagnifyingGlass } from "@phosphor-icons/react";
import { CLUBS } from "@/lib/clubs";
import { Monogram } from "./Monogram";

type Status = "done" | "live" | "next" | "queued";
type Slot = { name: string; time: string; status: Status; note?: string; shape: (typeof CLUBS)[number]["shape"]; monogram: string };

const SLOTS: Slot[] = [
  { ...pick(0), time: "09:00", status: "done" },
  { ...pick(1), time: "11:30", status: "live" },
  { ...pick(2), time: "14:15", status: "next", note: "eff. +15m" },
  { ...pick(5), time: "16:30", status: "queued" },
];

function pick(i: number) {
  const c = CLUBS[i];
  return { name: c.name.split(" ").slice(0, 2).join(" "), monogram: c.monogram, shape: c.shape };
}

const EASE = [0.16, 1, 0.3, 1] as const;

/** Signature hero asset: one kit relayed across a day of club slots, with a
 *  15-minute inspection between each handoff. A schematic, not a screenshot. */
export function RelayTimeline() {
  const reduce = useReducedMotion();
  return (
    <div className="relative rounded-2xl border border-border bg-surface p-5 shadow-[var(--shadow)] sm:p-6">
      <div className="mb-5 flex items-center justify-between">
        <span className="font-mono text-[11px] uppercase tracking-[0.16em] text-fg-faint">
          One kit, one day
        </span>
        <span className="inline-flex items-center gap-1.5 font-mono text-[11px] text-fg-faint">
          <span className="relative flex h-2 w-2">
            {!reduce && (
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent-hi opacity-60" />
            )}
            <span className="relative inline-flex h-2 w-2 rounded-full bg-accent-hi" />
          </span>
          live
        </span>
      </div>
      <ol className="flex flex-col md:flex-row md:items-stretch">
        {SLOTS.map((slot, i) => (
          <SlotView key={i} slot={slot} index={i} last={i === SLOTS.length - 1} reduce={!!reduce} />
        ))}
      </ol>
    </div>
  );
}

function SlotView({ slot, index, last, reduce }: { slot: Slot; index: number; last: boolean; reduce: boolean }) {
  const live = slot.status === "live";
  return (
    <li className="flex flex-col md:flex-1 md:flex-row md:items-stretch">
      <motion.div
        initial={reduce ? false : { opacity: 0, y: 14 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true, amount: 0.4 }}
        transition={{ duration: 0.5, delay: index * 0.12, ease: EASE }}
        className={`relative flex-1 rounded-xl border p-3.5 ${
          live ? "border-accent/55 bg-accent/[0.06]" : "border-border bg-surface-2/50"
        }`}
      >
        <div className="flex items-center gap-2.5">
          <span className={live ? "text-accent" : "text-fg-faint"}>
            <Monogram club={{ name: slot.name, monogram: slot.monogram, shape: slot.shape }} size={28} />
          </span>
          <div className="min-w-0">
            <div className="truncate text-[13px] font-medium text-fg">{slot.name}</div>
            <div className="font-mono text-[11px] text-fg-muted">
              {slot.time}
              {slot.note ? ` · ${slot.note}` : ""}
            </div>
          </div>
        </div>
        <StatusRow status={slot.status} reduce={reduce} />
      </motion.div>
      {!last && <Gap />}
    </li>
  );
}

function StatusRow({ status, reduce }: { status: Status; reduce: boolean }) {
  if (status === "live") {
    return (
      <div className="mt-3">
        <div className="mb-1.5 inline-flex items-center gap-1 font-mono text-[10.5px] text-accent">
          <Timer size={12} weight="bold" /> in use
        </div>
        <div className="h-1 w-full overflow-hidden rounded-full bg-border">
          <motion.div
            className="h-full w-full origin-left rounded-full bg-accent-hi"
            initial={{ scaleX: reduce ? 0.62 : 0.12 }}
            animate={reduce ? { scaleX: 0.62 } : { scaleX: [0.12, 0.72] }}
            transition={
              reduce ? undefined : { duration: 3.2, ease: "easeInOut", repeat: Infinity, repeatType: "reverse" }
            }
          />
        </div>
      </div>
    );
  }
  const label = status === "done" ? "clean return" : status === "next" ? "next up" : "queued";
  return (
    <div className="mt-3 inline-flex items-center gap-1.5 font-mono text-[10.5px] text-fg-faint">
      {status === "done" ? (
        <CheckCircle size={12} weight="fill" className="text-fg-muted" />
      ) : (
        <span className="h-1.5 w-1.5 rounded-full border border-fg-faint" />
      )}
      {label}
    </div>
  );
}

function Gap() {
  return (
    <div
      className="flex items-center justify-center gap-1.5 py-1.5 md:flex-col md:px-1 md:py-0"
      aria-label="15 minute inspection window"
    >
      <span className="h-px w-5 bg-border md:h-4 md:w-px" />
      <span className="inline-flex items-center gap-1 whitespace-nowrap rounded-full border border-accent/30 bg-accent/[0.07] px-2 py-0.5 font-mono text-[10px] text-accent">
        <MagnifyingGlass size={11} weight="bold" /> 15m
      </span>
      <span className="h-px w-5 bg-border md:h-4 md:w-px" />
    </div>
  );
}
