import type { Metadata } from "next";

import { ExploreFeed } from "@/components/content/Feeds";

export const metadata: Metadata = {
  title: "Explore Ekiti — EKITI@30 DIGITAL",
  description: "The 16 Local Government Areas of Ekiti State — their towns, landmarks and institutions.",
};

export default function ExplorePage() {
  return (
    <main className="flex-1">
      <section className="page-hero adire-bg">
        <div className="wrap">
          <div className="eyebrow-row">
            <span className="eyebrow-dot" /> Ilẹ̀ wa · Our land
          </div>
          <h1 className="hero-title">
            Explore <em>Ekiti</em>
          </h1>
          <p className="hero-sub" style={{ marginBottom: 0 }}>
            Sixteen local governments, from the hills of Efon to the warm springs of Ikogosi. Pick one
            to see its towns, landmarks and institutions.
          </p>
        </div>
      </section>
      <section className="wrap content-section">
        <ExploreFeed />
      </section>
    </main>
  );
}
