"use client";

import { motion } from "motion/react";
import Link from "next/link";

/** Placeholder cards while a list loads. */
export function LoadingState({ variant }: { variant: "cards" | "rows" }) {
  return (
    <div
      className={variant === "cards" ? "review-grid" : "flex flex-col gap-3"}
      aria-busy="true"
      aria-label="Loading"
    >
      {[0, 1, 2].map((i) =>
        variant === "cards" ? (
          <div key={i} className="review-card">
            <div className="skeleton aspect-[4/3]" />
            <div className="flex flex-col gap-3 p-5">
              <div className="skeleton h-5 w-3/4 rounded" />
              <div className="skeleton h-3 w-1/2 rounded" />
              <div className="skeleton h-16 rounded" />
            </div>
          </div>
        ) : (
          <div key={i} className="review-row">
            <div className="skeleton h-12 w-12 shrink-0 rounded-full" />
            <div className="flex flex-1 flex-col gap-2">
              <div className="skeleton h-4 w-1/3 rounded" />
              <div className="skeleton h-3 w-1/2 rounded" />
            </div>
          </div>
        ),
      )}
    </div>
  );
}

/** Nothing waiting — reads as good news, not an empty table. */
export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
      className="review-empty adire-bg"
    >
      <motion.span
        className="review-empty-icon"
        initial={{ scale: 0.6, rotate: -20 }}
        animate={{ scale: 1, rotate: 0 }}
        transition={{ type: "spring", stiffness: 260, damping: 16, delay: 0.1 }}
        aria-hidden="true"
      >
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round">
          <path d="M5 12.5l4.5 4.5L19 7.5" />
        </svg>
      </motion.span>
      <p className="mt-4 font-display text-xl">{title}</p>
      <p className="mt-1 max-w-[40ch] text-sm text-ink-soft">{body}</p>
    </motion.div>
  );
}

/** A list couldn't load: say why and offer the way forward. */
export function ErrorState({
  message,
  signInAgain,
  onRetry,
}: {
  message: string;
  signInAgain: boolean;
  onRetry: () => void;
}) {
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="alert alert-error items-center justify-between gap-4" role="alert">
      <span className="flex gap-2.5">
        <span aria-hidden="true">●</span>
        {message}
      </span>
      {signInAgain ? (
        <Link href="/login?callbackUrl=/admin" className="btn-secondary btn-sm shrink-0">
          Sign in again
        </Link>
      ) : (
        <button type="button" onClick={onRetry} className="btn-secondary btn-sm shrink-0">
          Try again
        </button>
      )}
    </motion.div>
  );
}
