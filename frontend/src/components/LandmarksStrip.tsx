"use client";

import { SectionNotice, useHomepage } from "@/components/homepage/HomepageContent";
import { PlaceholderIcon } from "@/components/homepage/PlaceholderIcon";
import { landmarkTone } from "@/lib/homepage";

function LandmarksSkeleton() {
  return (
    <div className="land-row" aria-busy="true" aria-label="Loading places">
      {Array.from({ length: 4 }, (_, i) => (
        <div className="land-card" key={i}>
          <div className="land-photo skeleton" />
          <div className="land-meta">
            <div className="skeleton mb-2 h-4 w-3/4 rounded" />
            <div className="skeleton h-3 w-5/6 rounded" />
          </div>
        </div>
      ))}
    </div>
  );
}

export default function LandmarksStrip() {
  const { state, retry } = useHomepage();
  return (
    <section className="landmarks" id="landmarks">
      <div className="wrap">
        <div className="section-head">
          <h2 className="section-title">The land that raised us</h2>
          <p className="section-desc">
            Hills, springs and places every Ekiti child grew up hearing
            about. This list will grow as more places are added.
          </p>
        </div>
        {state.status === "loading" ? (
          <LandmarksSkeleton />
        ) : state.status === "error" ? (
          <SectionNotice onRetry={retry}>We couldn&apos;t load these places just now.</SectionNotice>
        ) : (
          <div className="land-row">
            {state.content.landmarks.map((land, i) => (
              <div className={`land-card ${landmarkTone(i)}`} key={land.id}>
                <div className="land-photo">
                  {land.imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element -- remote Cloudinary image
                    <img src={land.imageUrl} alt={land.name} loading="lazy" />
                  ) : (
                    <PlaceholderIcon name={land.placeholderIcon} />
                  )}
                </div>
                <div className="land-meta">
                  <p className="name">{land.name}</p>
                  <p className="loc">{land.description}</p>
                </div>
              </div>
            ))}
            <div className="land-more">
              + more places
              <br />
              coming soon
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
