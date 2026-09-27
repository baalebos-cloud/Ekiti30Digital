"use client";

import { motion } from "motion/react";

/** "Nothing here yet" — warm, not broken-looking. `children` holds any call to action. */
export function ContentEmpty({
  title = "Nothing here yet — check back soon",
  body,
  children,
}: {
  title?: string;
  body: string;
  children?: React.ReactNode;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: [0.22, 1, 0.36, 1] }}
      className="empty-state adire-bg"
    >
      <motion.span
        className="empty-state-icon"
        initial={{ scale: 0.6, rotate: -20 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 16, delay: 0.1 }}
        aria-hidden="true"
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M12 7v5l3 2" />
          <circle cx="12" cy="12" r="8.5" />
        </svg>
      </motion.span>
      <p className="mt-4 font-display text-xl">{title}</p>
      <p className="mt-1 max-w-[46ch] text-sm text-ink-soft">{body}</p>
      {children && <div className="mt-5">{children}</div>}
    </motion.div>
  );
}

export function ContentError({ what, onRetry }: { what: string; onRetry: () => void }) {
  return (
    <div className="alert alert-error items-center justify-between gap-4" role="alert">
      <span className="flex gap-2.5">
        <span aria-hidden="true">●</span>
        Couldn&apos;t load {what} right now. Check your connection and try again.
      </span>
      <button type="button" onClick={onRetry} className="btn-secondary btn-sm shrink-0">
        Try again
      </button>
    </div>
  );
}

export function TimelineSkeleton() {
  return (
    <div className="wrap tl-list" aria-busy="true" aria-label="Loading timeline">
      <div className="tl-rail" />
      <div className="skeleton mb-5 ml-1 h-8 w-32 rounded" />
      {[0, 1, 2, 3].map((i) => (
        <div key={i} className="tl-event">
          <div className="tl-marker skeleton" />
          <div className="tl-card" style={{ background: "var(--bg)" }}>
            <div className="tl-card-body flex flex-col gap-3">
              <div className="skeleton h-4 w-28 rounded" />
              <div className="skeleton h-5 w-3/4 rounded" />
              <div className="skeleton h-12 rounded" />
            </div>
            <div className="tl-thumb skeleton" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function LgaGridSkeleton() {
  return (
    <ul className="lga-grid" aria-busy="true" aria-label="Loading local governments">
      {Array.from({ length: 8 }, (_, i) => (
        <li key={i} className="lga-card" style={{ cursor: "default" }}>
          <div className="lga-art skeleton" />
          <div className="flex flex-col gap-2.5 p-5">
            <div className="skeleton h-5 w-1/2 rounded" />
            <div className="skeleton h-3 w-5/6 rounded" />
            <div className="skeleton h-3 w-2/3 rounded" />
          </div>
        </li>
      ))}
    </ul>
  );
}

export function CardListSkeleton({ className }: { className: string }) {
  return (
    <div className={className} aria-busy="true" aria-label="Loading">
      {[0, 1, 2].map((i) => (
        <div key={i} className="story-card flex flex-col gap-3">
          <div className="skeleton h-5 w-28 rounded-full" />
          <div className="skeleton h-6 w-3/4 rounded" />
          <div className="skeleton h-20 rounded" />
          <div className="skeleton h-3 w-1/3 rounded" />
        </div>
      ))}
    </div>
  );
}
