import type { Metadata } from "next";
import Link from "next/link";

import { VisionFeed } from "@/components/content/Feeds";
import { Reveal } from "@/components/ui/Reveal";

export const metadata: Metadata = {
  title: "Ekiti 2056 — EKITI@30 DIGITAL",
  description: "Citizen visions for Ekiti's next thirty years.",
};

const UPLOAD_HREF = "/upload?folder=EKITI30/Ekiti_2056";

export default function Ekiti2056Page() {
  return (
    <main className="flex-1">
      <section className="vision-hero">
        <div className="vision-sun" aria-hidden="true" />
        <div className="vision-horizon" aria-hidden="true" />
        <div className="wrap relative">
          <div className="eyebrow-row vision-eyebrow">
            <span className="eyebrow-dot" /> Ọ̀la wa · Our tomorrow
          </div>
          <h1 className="hero-title vision-title">
            Ekiti <em>2056</em>
          </h1>
          <p className="hero-sub vision-sub" style={{ marginBottom: 0 }}>
            Thirty years of statehood behind us, thirty ahead. What should a child growing up in your
            community find there in 2056?
          </p>
        </div>
      </section>

      <section className="wrap content-section">
        <p className="standing-note is-future mb-6">
          <span aria-hidden="true">✦</span>
          These are personal visions shared by citizens. They are not government policy or a
          commitment, and they are not endorsed by EKITI@30 DIGITAL.
        </p>
        <VisionFeed />
      </section>

      <Reveal as="section" className="wrap">
        <div className="cta-band is-future">
          <div>
            <h2 className="font-display text-3xl font-medium">
              What should Ekiti be known for in <em className="text-gold-soft">2056</em>?
            </h2>
            <p className="mt-2 max-w-[54ch] opacity-85">
              A written vision form is coming. Until then, share a photo or video of the future you
              want to see — a sketch, a model, a place that needs changing.
            </p>
          </div>
          <Link href={UPLOAD_HREF} className="btn-primary btn-flex shrink-0">
            Share your vision <span aria-hidden="true">→</span>
          </Link>
        </div>
      </Reveal>
    </main>
  );
}
