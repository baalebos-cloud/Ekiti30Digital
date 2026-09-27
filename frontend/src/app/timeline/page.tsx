import type { Metadata } from "next";
import TimelineView from "@/components/TimelineView";

export const metadata: Metadata = {
  title: "30-Year Timeline — EKITI@30 DIGITAL",
  description:
    "A verified record of events and developments in Ekiti State from 1996 to 2026, sourced and dated.",
};

export default function TimelinePage() {
  return (
    <main>
      <section className="tl-hero">
        <div className="wrap">
          <div className="eyebrow-row">
            <span className="eyebrow-dot"></span> 1996 – 2026
          </div>
          <h1 className="hero-title" style={{ fontSize: "clamp(30px, 4vw, 46px)" }}>
            Thirty years, <em>one line</em>.
          </h1>
          <p className="hero-sub">
            Every event here is sourced and dated — and where the record is
            incomplete or disputed, we say so rather than smoothing it over.
            That&apos;s the standard this whole platform holds itself to.
          </p>
        </div>
      </section>
      <TimelineView />
    </main>
  );
}
