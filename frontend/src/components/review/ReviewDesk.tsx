"use client";

import { AnimatePresence, motion } from "motion/react";
import { useState } from "react";

import { ContentManager } from "@/components/content-admin/ContentManager";
import { ContributorReviewRow } from "@/components/review/ContributorReviewRow";
import { MediaReviewCard } from "@/components/review/MediaReviewCard";
import { EmptyState, ErrorState, LoadingState } from "@/components/review/SectionStates";
import { sendReview, useReviewList, type ListState } from "@/components/review/useReviewList";
import { Spinner } from "@/components/ui/Spinner";
import { SuccessToast, useToast } from "@/components/ui/SuccessToast";
import type { PendingContributor, ReviewKind } from "@/lib/review";
import type { AssetRecord } from "@/lib/uploads";

// The two review queues, plus content editing (LGAs, timeline and the homepage).
type Tab = ReviewKind | "content";

const TABS: { kind: Tab; label: string }[] = [
  { kind: "assets", label: "Pending media" },
  { kind: "contributors", label: "Pending contributors" },
  { kind: "content", label: "Manage content" },
];

// Items leave by shrinking and fading while the rest close the gap.
const itemMotion = {
  layout: true,
  initial: { opacity: 0, y: 12 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, scale: 0.92, transition: { duration: 0.28, ease: [0.4, 0, 1, 1] } },
  transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] },
} as const;

export function ReviewDesk() {
  const media = useReviewList<AssetRecord>("assets");
  const contributors = useReviewList<PendingContributor>("contributors");
  const [tab, setTab] = useState<Tab>("assets");
  const { toast, show } = useToast();

  function reviewer<T extends { id: number }>(
    kind: ReviewKind,
    list: { remove: (id: number) => void },
    item: T,
    name: string,
  ) {
    return async (action: "approve" | "reject", reason?: string) => {
      const failure = await sendReview(kind, item.id, action, reason);
      if (!failure) {
        list.remove(item.id);
        show(`${action === "approve" ? "Approved" : "Rejected"} · ${name}`);
      }
      return failure;
    };
  }

  const states: Record<ReviewKind, ListState<{ id: number }>> = {
    assets: media.state,
    contributors: contributors.state,
  };
  const active = tab === "assets" ? media : tab === "contributors" ? contributors : null;

  return (
    <div className="mt-8">
      <div className="flex flex-wrap items-end justify-between gap-3 border-b border-line">
        <div role="tablist" aria-label="Review queues" className="flex gap-1">
          {TABS.map(({ kind, label }) => {
            const selected = tab === kind;
            return (
              <button
                key={kind}
                type="button"
                role="tab"
                id={`tab-${kind}`}
                aria-selected={selected}
                aria-controls={`panel-${kind}`}
                onClick={() => setTab(kind)}
                className={`review-tab ${selected ? "is-active" : ""}`}
              >
                {label}
                {kind !== "content" && <CountBadge state={states[kind]} />}
                {selected && (
                  <motion.span layoutId="review-tab-underline" className="review-tab-underline" transition={{ type: "spring", stiffness: 420, damping: 34 }} />
                )}
              </button>
            );
          })}
        </div>
        {active && (
          <button
            type="button"
            onClick={() => active.reload()}
            disabled={active.state.status === "loading"}
            className="link-btn mb-2 flex items-center gap-1.5"
          >
            {active.state.status === "loading" && <Spinner size={12} />}
            Refresh
          </button>
        )}
      </div>

      <AnimatePresence mode="wait" initial={false}>
        <motion.section
          key={tab}
          id={`panel-${tab}`}
          role="tabpanel"
          aria-labelledby={`tab-${tab}`}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -4 }}
          transition={{ duration: 0.2 }}
          className="review-panel"
        >
          {tab === "content" ? (
            <ContentManager />
          ) : tab === "assets" ? (
            media.state.status === "loading" ? (
              <LoadingState variant="cards" />
            ) : media.state.status === "error" ? (
              <ErrorState message={media.state.message} signInAgain={media.state.signInAgain} onRetry={media.reload} />
            ) : media.state.items.length === 0 ? (
              <EmptyState title="All caught up" body="No uploads are waiting for review. New photos and videos will appear here as contributors send them in." />
            ) : (
              <ul className="review-grid">
                <AnimatePresence mode="popLayout">
                  {media.state.items.map((asset) => (
                    <motion.li key={asset.id} {...itemMotion}>
                      <MediaReviewCard asset={asset} onReview={reviewer("assets", media, asset, asset.description ?? `upload #${asset.id}`)} />
                    </motion.li>
                  ))}
                </AnimatePresence>
              </ul>
            )
          ) : contributors.state.status === "loading" ? (
            <LoadingState variant="rows" />
          ) : contributors.state.status === "error" ? (
            <ErrorState message={contributors.state.message} signInAgain={contributors.state.signInAgain} onRetry={contributors.reload} />
          ) : contributors.state.items.length === 0 ? (
            <EmptyState title="No one waiting" body="There are no new signups to review. People who create a contributor account will appear here." />
          ) : (
            <ul className="flex flex-col gap-3">
              <AnimatePresence mode="popLayout">
                {contributors.state.items.map((person) => (
                  <motion.li key={person.id} {...itemMotion}>
                    <ContributorReviewRow contributor={person} onReview={reviewer("contributors", contributors, person, person.name)} />
                  </motion.li>
                ))}
              </AnimatePresence>
            </ul>
          )}
        </motion.section>
      </AnimatePresence>

      <SuccessToast toast={toast} />
    </div>
  );
}

function CountBadge({ state }: { state: ListState<{ id: number }> }) {
  if (state.status === "loading") return <span className="review-count"><Spinner size={10} /></span>;
  if (state.status === "error") return <span className="review-count is-error" aria-label="failed to load">!</span>;
  const count = state.items.length;
  return (
    <span className={`review-count ${count > 0 ? "has-items" : ""}`} aria-label={`${count} pending`}>
      <AnimatePresence mode="popLayout" initial={false}>
        <motion.span
          key={count}
          initial={{ y: -8, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 8, opacity: 0 }}
          transition={{ duration: 0.2 }}
          className="inline-block tabular-nums"
        >
          {count}
        </motion.span>
      </AnimatePresence>
    </span>
  );
}
