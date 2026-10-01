import type { PlaceholderIconName } from "@/lib/homepage";

/**
 * The line-art a homepage card shows until it has a real image. Keys match
 * the backend's PLACEHOLDER_ICONS (app/models/homepage.py).
 *
 * The hero's polaroids drew two icons slightly differently from the cards
 * (a bigger sun over the springs, a smaller person), so `variant="hero"`
 * keeps those exactly as they were.
 */
export function PlaceholderIcon({ name, variant = "card" }: { name: PlaceholderIconName; variant?: "hero" | "card" }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true">
      {paths(name, variant)}
    </svg>
  );
}

function paths(name: PlaceholderIconName, variant: "hero" | "card") {
  switch (name) {
    case "document":
      return <path d="M4 19V6a2 2 0 012-2h9l5 5v10a2 2 0 01-2 2H6a2 2 0 01-2-2z" />;
    case "person":
      return (
        <>
          <circle cx="12" cy="8" r="3.4" />
          <path d="M5 20c1-4 4-6 7-6s6 2 7 6" />
        </>
      );
    case "springs":
      return (
        <>
          <path d="M2 18c3-6 6-9 10-9s7 3 10 9" />
          <circle cx="17" cy="7" r={variant === "hero" ? "2.4" : "2.2"} />
        </>
      );
    case "waterfall":
      return <path d="M12 3l4 6h-3v5l6 7H5l6-7v-5H8l4-6z" />;
    case "hill":
      return <path d="M3 20l6-11 4 6 3-5 5 10H3z" />;
    case "star":
      return <path d="M12 2l2.9 6 6.6.6-5 4.4 1.6 6.4L12 16l-5.9 3.4 1.5-6.4-5-4.4 6.6-.6z" />;
    case "house":
      return <path d="M4 21V10l8-6 8 6v11M9 21v-6h6v6" />;
    case "book":
      return <path d="M4 4.5A2.5 2.5 0 016.5 2H20v17H6.5A2.5 2.5 0 004 16.5v-12z" />;
    case "pin":
      return (
        <>
          <path d="M12 21s-7-4.6-7-10a7 7 0 0114 0c0 5.4-7 10-7 10z" />
          <circle cx="12" cy="11" r="2.2" />
        </>
      );
    case "celebration":
      return <path d="M4 21c1.5-5 4-7 8-7s6.5 2 8 7M8 11a4 4 0 118 0c0 2-2 3-2 5H10c0-2-2-3-2-5z" />;
  }
}

/** A leader's portrait placeholder (drawn a little differently from the "person" icon). */
export function LeaderIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" aria-hidden="true">
      <circle cx="12" cy="8" r="3.6" />
      <path d="M4.5 20c1.2-4.4 4.3-6.6 7.5-6.6s6.3 2.2 7.5 6.6" />
    </svg>
  );
}
