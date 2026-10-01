"use client";

/** Manage content -> Homepage: the hero (text and photos), leaders, landmarks and moments. */

import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

import { HeroEditor } from "@/components/homepage-admin/HeroEditor";
import { ListManager } from "@/components/homepage-admin/ListManager";

const SECTIONS = [
  { key: "hero", label: "Hero" },
  { key: "leaders", label: "Leaders" },
  { key: "landmarks", label: "Landmarks" },
  { key: "moments", label: "Moments" },
] as const;
type Section = (typeof SECTIONS)[number]["key"];

export function HomepageManager({ onToast }: { onToast: (message: string) => void }) {
  const [section, setSection] = useState<Section>("hero");

  return (
    <div className="flex flex-col gap-5">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div role="tablist" aria-label="Homepage section" className="flex flex-wrap gap-1.5">
          {SECTIONS.map(({ key, label }) => (
            <button
              key={key}
              type="button"
              role="tab"
              aria-selected={section === key}
              onClick={() => setSection(key)}
              className={`homepage-section-tab ${section === key ? "is-active" : ""}`}
            >
              {label}
            </button>
          ))}
        </div>
        <a href="/" target="_blank" rel="noreferrer" className="link-btn">
          View the homepage ↗
        </a>
      </div>

      <AnimatePresence mode="wait" initial={false}>
        <motion.div
          key={section}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2 }}
          className="flex flex-col gap-8"
        >
          {section === "hero" ? (
            <>
              <HeroEditor onToast={onToast} />
              <div className="flex flex-col gap-3">
                <h3 className="font-display text-xl">Hero photos</h3>
                <ListManager list="hero/images" onToast={onToast} />
              </div>
            </>
          ) : (
            <ListManager list={section} onToast={onToast} />
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
