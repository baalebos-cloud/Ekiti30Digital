"use client";

import { useMemo, useState } from "react";
import { timelineEvents, type VerificationStatus } from "@/data/timelineEvents";

const categories = [
  "All",
  ...Array.from(new Set(timelineEvents.map((e) => e.category))).sort(),
];

const statusLabel: Record<VerificationStatus, string> = {
  Verified: "Verified",
  "Single source": "Single source",
  "Needs primary source": "Needs primary source",
  "Conflicting sources": "Conflicting sources",
};

const statusClass: Record<VerificationStatus, string> = {
  Verified: "status-verified",
  "Single source": "status-single",
  "Needs primary source": "status-needs",
  "Conflicting sources": "status-conflict",
};

export default function TimelineView() {
  const [activeCategory, setActiveCategory] = useState("All");

  const filtered = useMemo(() => {
    if (activeCategory === "All") return timelineEvents;
    return timelineEvents.filter((e) => e.category === activeCategory);
  }, [activeCategory]);

  return (
    <div>
      <div className="wrap">
        <div className="tl-legend">
          <span className="tl-legend-item">
            <span className="tl-dot status-verified" /> Verified
          </span>
          <span className="tl-legend-item">
            <span className="tl-dot status-single" /> Single source
          </span>
          <span className="tl-legend-item">
            <span className="tl-dot status-needs" /> Needs primary source
          </span>
          <span className="tl-legend-item">
            <span className="tl-dot status-conflict" /> Conflicting sources
          </span>
        </div>

        <div className="tl-filters">
          {categories.map((cat) => (
            <button
              key={cat}
              className={`tl-chip ${activeCategory === cat ? "is-active" : ""}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </button>
          ))}
        </div>

        <p className="tl-count">
          Showing {filtered.length} of {timelineEvents.length} verified events
        </p>
      </div>

      <div className="wrap tl-list">
        <div className="tl-rail" />
        {filtered.map((event) => (
          <article className="tl-event" key={event.id}>
            <div className={`tl-marker ${statusClass[event.status]}`} />
            <div className="tl-card">
              <div className="tl-card-head">
                <span className="tl-date">{event.date}</span>
                <span className="tl-category">{event.category}</span>
              </div>
              <h3 className="tl-title">{event.title}</h3>
              <p className="tl-desc">{event.description}</p>
              <div className="tl-card-foot">
                <span className={`tl-badge ${statusClass[event.status]}`}>
                  {statusLabel[event.status]}
                </span>
                <a
                  href={event.sourceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="tl-source"
                >
                  {event.source} ↗
                </a>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
