"use client";

import { SectionNotice, useHomepage } from "@/components/homepage/HomepageContent";
import { LeaderIcon } from "@/components/homepage/PlaceholderIcon";
import { AutoScrollRow } from "@/components/ui/AutoScrollRow";

function LeadersSkeleton() {
  return (
    <div className="leader-row" aria-busy="true" aria-label="Loading leaders">
      {Array.from({ length: 7 }, (_, i) => (
        <div className="leader-card" key={i}>
          <div className="leader-photo skeleton" />
          <div className="skeleton mx-auto mb-1.5 h-4 w-24 rounded" />
          <div className="skeleton mx-auto h-3 w-16 rounded" />
        </div>
      ))}
    </div>
  );
}

export default function LeadersStrip() {
  const { state, retry } = useHomepage();
  return (
    <section className="leaders" id="leaders">
      <div className="wrap">
        <div className="section-head">
          <h2 className="section-title">The people who led us home</h2>
          <p className="section-desc">
            Every administrator and governor since Ekiti&apos;s creation on 1
            October 1996. Real, verified photos to follow once sourced.
          </p>
        </div>
        {state.status === "loading" ? (
          <LeadersSkeleton />
        ) : state.status === "error" ? (
          <SectionNotice onRetry={retry}>We couldn&apos;t load the leaders just now.</SectionNotice>
        ) : state.content.leaders.length === 0 ? (
          <SectionNotice>The leaders will appear here soon.</SectionNotice>
        ) : (
          <AutoScrollRow className="leader-row">
            {state.content.leaders.map((leader) => (
              <div className="leader-card" key={leader.id}>
                <div className="leader-photo">
                  {leader.imageUrl ? (
                    // eslint-disable-next-line @next/next/no-img-element -- remote Cloudinary portrait
                    <img src={leader.imageUrl} alt={leader.name} loading="lazy" />
                  ) : (
                    <LeaderIcon />
                  )}
                </div>
                <p className="leader-name">{leader.name}</p>
                <p className="leader-term">{leader.term}</p>
              </div>
            ))}
          </AutoScrollRow>
        )}
      </div>
    </section>
  );
}
