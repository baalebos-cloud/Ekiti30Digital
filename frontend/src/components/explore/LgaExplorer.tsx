"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useMemo, useRef, useState } from "react";

import type { Lga } from "@/data/lgas";

const TONES = ["tone-forest", "tone-teal", "tone-gold", "tone-rust"] as const;

// Stable per LGA, whatever order the feed returns them in.
function toneFor(lga: Lga): string {
  let sum = 0;
  for (const ch of lga.slug) sum += ch.charCodeAt(0);
  return TONES[sum % TONES.length];
}

// The feed only guarantees slug, name and headquarters; the rest may be absent.
function withDefaults(lga: Partial<Lga> & Pick<Lga, "slug" | "name" | "headquarters">): Lga {
  return { towns: [], notablePlaces: [], institutions: [], sources: [], lastChecked: "", verificationStatus: "", limitations: "", latitude: 0, longitude: 0, ...lga };
}

function listText(items: string[]): string {
  if (items.length <= 1) return items.join("");
  return `${items.slice(0, -1).join(", ")} and ${items.at(-1)}`;
}

/** A one-line summary built only from what the dataset actually records. */
function summary(lga: Lga): string {
  const parts = [`Headquartered at ${lga.headquarters}.`];
  if (lga.notablePlaces.length) parts.push(`Home to ${listText(lga.notablePlaces)}.`);
  else if (lga.towns.length > 1) parts.push(`Takes in ${listText(lga.towns.slice(1, 4))}.`);
  return parts.join(" ");
}

export function LgaExplorer({ lgas: feed }: { lgas: Lga[] }) {
  const lgas = useMemo(() => feed.map(withDefaults), [feed]);
  const [query, setQuery] = useState("");
  const [openSlug, setOpenSlug] = useState<string | null>(null);
  const lastTrigger = useRef<HTMLElement | null>(null);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return lgas;
    return lgas.filter((l) =>
      [l.name, l.headquarters, ...l.towns, ...l.notablePlaces].some((s) => s.toLowerCase().includes(q)),
    );
  }, [query, lgas]);

  const open = lgas.find((l) => l.slug === openSlug) ?? null;

  function close() {
    setOpenSlug(null);
    lastTrigger.current?.focus();
  }

  return (
    <>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div className="field w-full max-w-sm">
          <label htmlFor="lga-search" className="field-label">Find a place</label>
          <input
            id="lga-search"
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="input"
            placeholder="An LGA, town or landmark — e.g. Ikogosi"
            autoComplete="off"
          />
        </div>
        <p className="text-sm text-ink-soft" aria-live="polite">
          {visible.length === lgas.length ? `All ${lgas.length} local governments` : `${visible.length} of ${lgas.length} match`}
        </p>
      </div>

      <motion.ul layout className="lga-grid mt-8">
        <AnimatePresence mode="popLayout">
          {visible.map((lga, i) => (
            <motion.li
              key={lga.slug}
              layout
              initial={{ opacity: 0, y: 18 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.4, delay: query ? 0 : Math.min(i, 8) * 0.04, ease: [0.22, 1, 0.36, 1] }}
            >
              <motion.button
                type="button"
                layoutId={`lga-${lga.slug}`}
                onClick={(e) => {
                  lastTrigger.current = e.currentTarget;
                  setOpenSlug(lga.slug);
                }}
                whileHover={{ y: -4 }}
                className="lga-card"
                aria-haspopup="dialog"
              >
                <motion.div layoutId={`lga-art-${lga.slug}`} className={`lga-art ${toneFor(lga)}`}>
                  <span className="lga-art-name">{lga.headquarters}</span>
                  <span className="lga-art-coords">
                    {lga.latitude.toFixed(2)}° N · {lga.longitude.toFixed(2)}° E
                  </span>
                </motion.div>
                <div className="p-5 text-left">
                  <h3 className="font-display text-xl font-medium">{lga.name}</h3>
                  <p className="mt-1.5 text-sm text-ink-soft">{summary(lga)}</p>
                  <span className="lga-more">
                    Explore <span aria-hidden="true">→</span>
                  </span>
                </div>
              </motion.button>
            </motion.li>
          ))}
        </AnimatePresence>
      </motion.ul>

      {visible.length === 0 && (
        <p className="mt-10 text-center text-ink-soft">
          Nothing matches “{query}”. Try the name of a town or a local government.
        </p>
      )}

      <AnimatePresence>{open && <LgaDetail lga={open} onClose={close} />}</AnimatePresence>
    </>
  );
}

function LgaDetail({ lga, onClose }: { lga: Lga; onClose: () => void }) {
  const closeButton = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    closeButton.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    window.addEventListener("keydown", onKey);
    return () => {
      document.body.style.overflow = overflow;
      window.removeEventListener("keydown", onKey);
    };
  }, [onClose]);

  const sections: [string, string[]][] = [
    ["Towns & communities", lga.towns],
    ["Notable places", lga.notablePlaces],
    ["Institutions", lga.institutions],
  ];

  return (
    <motion.div
      className="lga-overlay"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      onClick={onClose}
    >
      <motion.div
        layoutId={`lga-${lga.slug}`}
        role="dialog"
        aria-modal="true"
        aria-labelledby={`lga-title-${lga.slug}`}
        className="lga-dialog"
        onClick={(e) => e.stopPropagation()}
      >
        <motion.div layoutId={`lga-art-${lga.slug}`} className={`lga-art lga-art-lg ${toneFor(lga)}`}>
          <span className="lga-art-name">{lga.name}</span>
          <span className="lga-art-coords">
            {lga.latitude.toFixed(4)}° N · {lga.longitude.toFixed(4)}° E
          </span>
          <button ref={closeButton} type="button" onClick={onClose} className="lga-close" aria-label="Close">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
              <path d="M6 6l12 12M18 6 6 18" />
            </svg>
          </button>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.35 }}
          className="p-6 sm:p-8"
        >
          <div className="flex flex-wrap items-center gap-3">
            <h2 id={`lga-title-${lga.slug}`} className="font-display text-3xl font-medium">{lga.name}</h2>
            <span className="status-pill">{lga.verificationStatus === "Pending" ? "Details pending review" : lga.verificationStatus}</span>
          </div>
          <p className="mt-1 text-ink-soft">
            Local government headquarters: <strong className="font-semibold text-ink">{lga.headquarters}</strong>
          </p>

          <div className="mt-6 grid gap-6 sm:grid-cols-3">
            {sections.map(([title, items]) => (
              <div key={title}>
                <h3 className="lga-section-title">{title}</h3>
                {items.length ? (
                  <ul className="mt-2 flex flex-col gap-1.5 text-sm">
                    {items.map((item) => (
                      <li key={item} className="flex gap-2">
                        <span className="mt-[7px] h-1.5 w-1.5 shrink-0 rounded-full bg-gold" aria-hidden="true" />
                        {item}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="mt-2 text-sm italic text-ink-soft">Still being researched.</p>
                )}
              </div>
            ))}
          </div>

          <div className="mt-7 rounded-[var(--radius-s)] border border-line bg-bg-warm p-4 text-xs text-ink-soft">
            <p>
              <strong className="font-semibold text-ink">About this information:</strong>{" "}
              {/\.\s*$/.test(lga.limitations) ? lga.limitations : `${lga.limitations}.`} Last
              checked {lga.lastChecked}.
            </p>
            {lga.sources.length > 0 && (
              <p className="mt-2 flex flex-wrap gap-x-4 gap-y-1">
                Sources:
                {lga.sources.map((s) => (
                  <a key={s.url} href={s.url} target="_blank" rel="noopener noreferrer" className="tl-source">
                    {s.name} ↗
                  </a>
                ))}
              </p>
            )}
          </div>
        </motion.div>
      </motion.div>
    </motion.div>
  );
}
