import type { Metadata } from "next";
import Link from "next/link";

import { StoriesFeed } from "@/components/content/Feeds";
import { Reveal } from "@/components/ui/Reveal";

export const metadata: Metadata = {
  title: "My Ekiti Story — EKITI@30 DIGITAL",
  description: "Personal memories and family journeys from Ekiti people at home and abroad.",
};

const UPLOAD_HREF = "/upload?folder=EKITI30/Community_Stories";

export default function MyEkitiStoryPage() {
  return (
    <main className="flex-1">
      <section className="page-hero adire-bg">
        <div className="wrap grid items-end gap-6 md:grid-cols-[1fr_auto]">
          <div>
            <div className="eyebrow-row">
              <span className="eyebrow-dot" /> Ìtàn wa · Our stories
            </div>
            <h1 className="hero-title">
              My Ekiti <em>Story</em>
            </h1>
            <p className="hero-sub" style={{ marginBottom: 0 }}>
              Market mornings, first harvests, festival drums heard from far away — thirty years of
              Ekiti, remembered by the people who lived it.
            </p>
          </div>
          <div className="flex flex-col items-start gap-2 md:items-end">
            <Link href={UPLOAD_HREF} className="btn-primary btn-flex">
              <CameraIcon /> Share a photo or video
            </Link>
            <span className="text-xs text-ink-soft">Written stories open soon.</span>
          </div>
        </div>
      </section>

      <section className="wrap content-section">
        <p className="standing-note mb-6">
          <span aria-hidden="true">❝</span>
          These are personal accounts shared by citizens. They are not automatically verified history.
          Facts marked Verified have been checked against a source.
        </p>
        <StoriesFeed uploadHref={UPLOAD_HREF} />
      </section>

      <Reveal as="section" className="wrap">
        <div className="cta-band">
          <div>
            <h2 className="font-display text-3xl font-medium">
              Your story belongs <em className="text-gold-soft">here</em>.
            </h2>
            <p className="mt-2 max-w-[52ch] opacity-85">
              Have a photo or video from your town, your family or a festival? Share it — every
              upload is reviewed by the EKITI@30 team before it appears.
            </p>
          </div>
          <Link href={UPLOAD_HREF} className="btn-primary btn-flex shrink-0">
            <CameraIcon /> Share a photo or video
          </Link>
        </div>
      </Reveal>
    </main>
  );
}

function CameraIcon() {
  return (
    <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M4 8h3l2-3h6l2 3h3v11H4z" />
      <circle cx="12" cy="13" r="3.5" />
    </svg>
  );
}
