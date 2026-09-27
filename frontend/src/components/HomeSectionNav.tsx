"use client";

import { motion } from "motion/react";
import { useEffect, useState } from "react";

const SECTIONS = [
  { id: "leaders", label: "Leaders" },
  { id: "landmarks", label: "Places" },
  { id: "moments", label: "Moments" },
  { id: "features", label: "Ways in" },
] as const;

/**
 * Sticky "on this page" bar for the homepage. Highlights the section that
 * currently fills the middle of the screen.
 */
export function HomeSectionNav() {
  const [active, setActive] = useState<string | null>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.filter((e) => e.isIntersecting);
        if (visible.length) setActive(visible[0].target.id);
      },
      // A thin band across the middle of the viewport decides "current".
      { rootMargin: "-45% 0px -50% 0px" },
    );
    for (const { id } of SECTIONS) {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    }
    return () => observer.disconnect();
  }, []);

  return (
    <nav className="section-nav" aria-label="On this page">
      <div className="wrap section-nav-inner">
        <span className="section-nav-label">On this page</span>
        <ul>
          {SECTIONS.map(({ id, label }, i) => (
            <li key={id}>
              <a href={`#${id}`} className={active === id ? "is-active" : ""} aria-current={active === id ? "true" : undefined}>
                <span className="section-nav-num">{String(i + 1).padStart(2, "0")}</span>
                {label}
                {active === id && (
                  <motion.span layoutId="section-nav-pill" className="section-nav-pill" transition={{ type: "spring", stiffness: 420, damping: 34 }} />
                )}
              </a>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
