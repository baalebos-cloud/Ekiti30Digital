"use client";

import { SectionNotice, useHomepage } from "@/components/homepage/HomepageContent";
import { PlaceholderIcon } from "@/components/homepage/PlaceholderIcon";

function MomentsSkeleton() {
  return (
    <div className="spine" aria-busy="true" aria-label="Loading moments">
      <div className="spine-line"></div>
      {Array.from({ length: 5 }, (_, i) => (
        <div className="m-item" key={i}>
          <div className="m-photo skeleton-dark" />
          <div className="skeleton-dark mx-auto mb-1.5 h-4 w-12 rounded" />
          <div className="skeleton-dark mx-auto h-3 w-32 max-w-full rounded" />
        </div>
      ))}
    </div>
  );
}

export default function MomentsSpine() {
  const { state, retry } = useHomepage();
  return (
    <section className="moments" id="moments">
      <div className="wrap">
        <div className="section-head">
          <h2 className="section-title">Moments that shaped us</h2>
          <p className="section-desc">
            From creation to celebration — a journey, not just a timeline.
          </p>
        </div>
        {state.status === "loading" ? (
          <MomentsSkeleton />
        ) : state.status === "error" ? (
          <SectionNotice onRetry={retry}>We couldn&apos;t load these moments just now.</SectionNotice>
        ) : (
          <div className="spine">
            <div className="spine-line"></div>
            {state.content.moments.map((m) => (
              <div className={`m-item ${m.isAnchor ? "is-anchor" : ""}`} key={m.id}>
                <div className="m-photo">
                  {m.imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element -- remote Cloudinary image
                    <img src={m.imageUrl} alt="" loading="lazy" />
                  ) : (
                    <PlaceholderIcon name={m.placeholderIcon} />
                  )}
                </div>
                <p className="m-year">{m.year}</p>
                <p className="m-label">{m.label}</p>
              </div>
            ))}
            <div className="m-more">
              <div className="m-more-circle">+ more</div>
              <p className="m-label">More moments being added</p>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
