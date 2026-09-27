"use client";

import { AnimatePresence, motion } from "motion/react";
import { useMemo, useState } from "react";

import type { CitizenVision } from "@/data/visions";

/** Published citizen visions, filterable by category. */
export function VisionBoard({ visions }: { visions: CitizenVision[] }) {
  const categories = useMemo(() => ["All", ...Array.from(new Set(visions.map((v) => v.category)))], [visions]);
  const [category, setCategory] = useState("All");
  const shown = category === "All" ? visions : visions.filter((v) => v.category === category);

  return (
    <>
      <div className="tl-filters" role="group" aria-label="Filter by theme">
        {categories.map((c) => (
          <motion.button
            key={c}
            type="button"
            whileTap={{ scale: 0.95 }}
            aria-pressed={category === c}
            onClick={() => setCategory(c)}
            className={`tl-chip vision-chip ${category === c ? "is-active" : ""}`}
          >
            {c}
          </motion.button>
        ))}
      </div>

      <motion.ul layout className="vision-grid mt-6">
        <AnimatePresence mode="popLayout" initial={false}>
          {shown.map((vision, i) => (
            <motion.li
              key={vision.id}
              layout
              initial={{ opacity: 0, y: 26, scale: 0.98 }}
              whileInView={{ opacity: 1, y: 0, scale: 1 }}
              viewport={{ once: true, margin: "0px 0px -40px 0px" }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.5, delay: (i % 3) * 0.07, ease: [0.22, 1, 0.36, 1] }}
              className="vision-card"
            >
              <span className="label-pill is-future self-start">Citizen vision</span>
              <p className="vision-category">{vision.category}</p>
              <h2 className="vision-headline">{vision.headline}</h2>
              <p className="mt-3 leading-relaxed">{vision.vision}</p>
              {vision.whyItMatters && (
                <div className="vision-why">
                  <span>Why it matters</span>
                  <p>{vision.whyItMatters}</p>
                </div>
              )}
              <div className="story-meta mt-auto">
                <span className="font-semibold text-ink">{vision.sharedBy}</span>
                <span>
                  {[vision.lga, vision.language, vision.published && `Published ${vision.published}`]
                    .filter(Boolean)
                    .join(" · ")}
                </span>
              </div>
            </motion.li>
          ))}
        </AnimatePresence>
      </motion.ul>
    </>
  );
}
