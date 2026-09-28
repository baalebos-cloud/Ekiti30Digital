"use client";

import { AnimatePresence, motion } from "motion/react";
import { useMemo, useState } from "react";

import type { TimelineEvent, VerificationStatus } from "@/data/timelineEvents";

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

// Placeholder image tint per category, until real photographs are sourced.
const categoryTone: Record<string, string> = {
  Government: "tone-forest",
  Education: "tone-teal",
  Health: "tone-rust",
  Culture: "tone-gold",
  Tourism: "tone-forest",
  Infrastructure: "tone-teal",
  Technology: "tone-teal",
  Agriculture: "tone-forest",
  Sports: "tone-rust",
};

/** First four-digit year in a date label like "Oct 2006 (day disputed)". */
function yearOf(event: TimelineEvent): number {
  return Number(event.date.match(/\d{4}/)?.[0] ?? 0);
}

function decadeLabel(year: number): string {
  return `${Math.floor(year / 10) * 10}s`;
}

/** The full timeline for the events it's given (from the /api/content/timeline feed). */
export default function TimelineView({ events: timelineEvents }: { events: TimelineEvent[] }) {
  const [activeCategory, setActiveCategory] = useState("All");

  const categories = useMemo(
    () => ["All", ...Array.from(new Set(timelineEvents.map((e) => e.category))).sort()],
    [timelineEvents],
  );

  const groups = useMemo(() => {
    const filtered =
      activeCategory === "All" ? timelineEvents : timelineEvents.filter((e) => e.category === activeCategory);
    const byDecade = new Map<string, TimelineEvent[]>();
    for (const event of filtered) {
      const decade = decadeLabel(yearOf(event));
      byDecade.set(decade, [...(byDecade.get(decade) ?? []), event]);
    }
    return Array.from(byDecade, ([decade, events]) => ({ decade, events }));
  }, [activeCategory, timelineEvents]);

  const shown = groups.reduce((n, g) => n + g.events.length, 0);

  return (
    <div>
      <div className="wrap">
        <div className="tl-legend">
          {(Object.keys(statusLabel) as VerificationStatus[]).map((status) => (
            <span key={status} className="tl-legend-item">
              <span className={`tl-dot ${statusClass[status]}`} /> {statusLabel[status]}
            </span>
          ))}
        </div>

        <div className="tl-filters" role="group" aria-label="Filter by category">
          {categories.map((cat) => (
            <motion.button
              key={cat}
              type="button"
              whileTap={{ scale: 0.95 }}
              aria-pressed={activeCategory === cat}
              className={`tl-chip ${activeCategory === cat ? "is-active" : ""}`}
              onClick={() => setActiveCategory(cat)}
            >
              {cat}
            </motion.button>
          ))}
        </div>

        <p className="tl-count" aria-live="polite">
          Showing {shown} of {timelineEvents.length} events
        </p>
      </div>

      <div className="wrap tl-list">
        <div className="tl-rail" />
        <AnimatePresence mode="popLayout" initial={false}>
          {groups.map(({ decade, events }) => (
            <motion.section
              key={`${activeCategory}-${decade}`}
              layout
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              aria-label={decade}
              className="tl-group"
            >
              <motion.h2
                className="tl-decade"
                initial={{ opacity: 0, x: -12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              >
                <span className="tl-decade-dot" aria-hidden="true" />
                {decade}
              </motion.h2>
              {events.map((event) => (
                <motion.article
                  key={event.id}
                  className="tl-event"
                  initial={{ opacity: 0, y: 24 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true, margin: "0px 0px -40px 0px" }}
                  transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
                >
                  <div className={`tl-marker ${statusClass[event.status] ?? "status-single"}`} />
                  <div className="tl-card">
                    <div className="tl-card-body">
                      <div className="tl-card-head">
                        <span className="tl-date">{event.date}</span>
                        <span className="tl-category">{event.category}</span>
                      </div>
                      <h3 className="tl-title">{event.title}</h3>
                      <p className="tl-desc">{event.description}</p>
                      <div className="tl-card-foot">
                        <span className={`tl-badge ${statusClass[event.status] ?? "status-single"}`}>{statusLabel[event.status] ?? event.status}</span>
                        <a href={event.sourceUrl} target="_blank" rel="noopener noreferrer" className="tl-source">
                          {event.source} ↗
                        </a>
                      </div>
                    </div>
                    <div className={`tl-thumb ${categoryTone[event.category] ?? "tone-gold"}`} aria-hidden="true">
                      <PhotoIcon />
                      <span>Photo to come</span>
                    </div>
                  </div>
                </motion.article>
              ))}
            </motion.section>
          ))}
        </AnimatePresence>
      </div>
    </div>
  );
}

function PhotoIcon() {
  return (
    <svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <circle cx="9" cy="10" r="1.6" />
      <path d="m21 16-5-5-8 8" />
    </svg>
  );
}
