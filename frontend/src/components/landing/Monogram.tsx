import type { Club } from "@/lib/clubs";

/** Generated monogram mark (frame + letter) for an invented club brand.
 *  Single-color via currentColor so it renders in light and dark. */
export function Monogram({ club, size = 34 }: { club: Club; size?: number }) {
  const c = size / 2;
  const frame =
    club.shape === "circle" ? (
      <circle cx={c} cy={c} r={c - 1.5} fill="none" stroke="currentColor" strokeWidth="1.5" />
    ) : club.shape === "square" ? (
      <rect
        x="1.5"
        y="1.5"
        width={size - 3}
        height={size - 3}
        rx="7"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    ) : (
      <path
        d={`M${c} 1.8 L${size - 2.5} ${c * 0.5 + 0.9} L${size - 2.5} ${c * 1.5 - 0.9} L${c} ${size - 1.8} L2.5 ${c * 1.5 - 0.9} L2.5 ${c * 0.5 + 0.9} Z`}
        fill="none"
        stroke="currentColor"
        strokeWidth="1.5"
      />
    );
  return (
    <svg
      viewBox={`0 0 ${size} ${size}`}
      width={size}
      height={size}
      aria-hidden="true"
      className="shrink-0"
    >
      {frame}
      <text
        x="50%"
        y="52%"
        dominantBaseline="central"
        textAnchor="middle"
        fontSize={size * 0.42}
        fontWeight="600"
        fill="currentColor"
        style={{ fontFamily: "var(--font-sans)" }}
      >
        {club.monogram}
      </text>
    </svg>
  );
}
