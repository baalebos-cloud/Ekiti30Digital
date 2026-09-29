"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useState } from "react";

import { AuditLine } from "@/components/content-admin/AuditLine";
import { Spinner } from "@/components/ui/Spinner";
import {
  NOUN,
  recordKey,
  recordTitle,
  type ContentAdminKind,
  type ContentRecord,
  type LgaRecord,
  type TimelineRecord,
} from "@/lib/contentAdmin";

const STATUS_CLASS: Record<string, string> = {
  Verified: "status-verified",
  "Single source": "status-single",
  "Needs primary source": "status-needs",
  "Conflicting sources": "status-conflict",
};

// Rows leave by shrinking and fading while the rest close the gap.
const rowMotion = {
  layout: true,
  initial: { opacity: 0, y: 10 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, scale: 0.94, transition: { duration: 0.26, ease: [0.4, 0, 1, 1] } },
  transition: { duration: 0.3, ease: [0.22, 1, 0.36, 1] },
} as const;

type Props = {
  kind: ContentAdminKind;
  items: ContentRecord[];
  onEdit: (record: ContentRecord) => void;
  /** Resolves to an error message, or null once deleted. */
  onDelete: (record: ContentRecord) => Promise<string | null>;
};

export function ContentList({ kind, items, onEdit, onDelete }: Props) {
  const [query, setQuery] = useState("");
  const needle = query.trim().toLowerCase();
  const shown = needle
    ? items.filter((item) =>
        [recordKey(kind, item), recordTitle(kind, item)].some((s) => s.toLowerCase().includes(needle)),
      )
    : items;

  return (
    <div className="flex flex-col gap-4">
      <div className="field max-w-sm">
        <label htmlFor={`${kind}-filter`} className="sr-only">
          Filter {NOUN[kind].many}
        </label>
        <input
          id={`${kind}-filter`}
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder={kind === "lgas" ? "Filter by name…" : "Filter by ID or title…"}
          className="input"
        />
      </div>
      <p className="text-xs text-ink-soft" aria-live="polite">
        {shown.length === items.length ? `${items.length} ${NOUN[kind].many}` : `${shown.length} of ${items.length} ${NOUN[kind].many}`}
      </p>
      <ul className="flex flex-col gap-3">
        <AnimatePresence mode="popLayout" initial={false}>
          {shown.map((item) => (
            <motion.li key={recordKey(kind, item)} {...rowMotion}>
              <ContentRow kind={kind} item={item} onEdit={() => onEdit(item)} onDelete={() => onDelete(item)} />
            </motion.li>
          ))}
        </AnimatePresence>
      </ul>
    </div>
  );
}

function ContentRow({
  kind,
  item,
  onEdit,
  onDelete,
}: {
  kind: ContentAdminKind;
  item: ContentRecord;
  onEdit: () => void;
  onDelete: () => Promise<string | null>;
}) {
  const controls = useAnimationControls();
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const title = recordTitle(kind, item);

  async function confirmDelete() {
    setBusy(true);
    setError(null);
    const failure = await onDelete();
    // On success the parent removes this row, so only failures land here.
    if (failure) {
      setBusy(false);
      setError(failure);
      controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
    }
  }

  return (
    <motion.div animate={controls} className="review-row">
      <div className="flex min-w-0 flex-[1_1_260px] flex-col items-start gap-1.5">
        {kind === "lgas" ? <LgaSummary lga={item as LgaRecord} /> : <EventSummary event={item as TimelineRecord} />}
        <AuditLine updatedBy={item.updated_by} updatedAt={item.updated_at} />
      </div>

      <div className="review-row-actions flex flex-col gap-2">
        <AnimatePresence initial={false}>
          {error && (
            <motion.div
              key="error"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="alert alert-error" role="alert">
                <span aria-hidden="true">●</span>
                <span>{error}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
        <AnimatePresence mode="wait" initial={false}>
          {confirming ? (
            <motion.div
              key="confirm"
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -4 }}
              transition={{ duration: 0.18 }}
              className="flex flex-col gap-2"
            >
              <p className="text-sm">
                Delete <strong>{title}</strong>? It disappears from the public site at once. This can&apos;t be undone here.
              </p>
              <div className="flex flex-wrap justify-end gap-2">
                <button type="button" className="btn-secondary btn-flex btn-sm" disabled={busy} onClick={() => setConfirming(false)} autoFocus>
                  Keep it
                </button>
                <motion.button
                  type="button"
                  className="btn-primary btn-flex btn-sm"
                  disabled={busy}
                  whileHover={busy ? undefined : { y: -1 }}
                  whileTap={busy ? undefined : { scale: 0.97 }}
                  onClick={confirmDelete}
                >
                  {busy ? (
                    <>
                      <Spinner size={14} /> Deleting…
                    </>
                  ) : (
                    `Delete ${NOUN[kind].one}`
                  )}
                </motion.button>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="actions"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="flex flex-wrap items-center justify-end gap-3"
            >
              <button type="button" className="link-btn is-danger" onClick={() => setConfirming(true)}>
                Delete
              </button>
              <motion.button
                type="button"
                className="btn-secondary btn-flex btn-sm"
                whileHover={{ y: -1 }}
                whileTap={{ scale: 0.97 }}
                onClick={onEdit}
              >
                Edit
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

function LgaSummary({ lga }: { lga: LgaRecord }) {
  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <p className="font-display text-lg font-medium">{lga.lga_name}</p>
        <span className="status-pill">{lga.verification_status}</span>
      </div>
      <p className="text-sm text-ink-soft">
        HQ {lga.headquarters} · {lga.latitude.toFixed(4)}, {lga.longitude.toFixed(4)} · checked {lga.last_checked}
      </p>
    </>
  );
}

function EventSummary({ event }: { event: TimelineRecord }) {
  return (
    <>
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs text-ink-soft">{event.id}</span>
        <span className={`tl-badge ${STATUS_CLASS[event.verification_status] ?? "status-single"}`}>{event.verification_status}</span>
      </div>
      <p className="font-display text-lg font-medium leading-snug">{event.event_title}</p>
      <p className="text-sm text-ink-soft">
        {event.date_display} · {event.category}
      </p>
    </>
  );
}
