"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useId, useState } from "react";

import { FieldError } from "@/components/ui/FieldError";
import { Spinner } from "@/components/ui/Spinner";

type Props = {
  /** Used in button and field labels, e.g. "upload" or "signup". */
  noun: string;
  /** Example reasons shown in the empty rejection box. */
  reasonExamples: string;
  /** When set, Approve is disabled and this explains why. */
  approveBlockedReason?: string;
  /**
   * Performs the review. Resolves to an error message to show on this item,
   * or null on success (the parent then removes the item).
   */
  onReview: (action: "approve" | "reject", reason?: string) => Promise<string | null>;
};

type Busy = "approve" | "reject" | null;

/** Approve / reject controls for one pending item, with an inline rejection reason. */
export function ReviewActions({ noun, reasonExamples, approveBlockedReason, onReview }: Props) {
  const id = useId();
  const controls = useAnimationControls();
  const [rejecting, setRejecting] = useState(false);
  const [reason, setReason] = useState("");
  const [reasonError, setReasonError] = useState<string | null>(null);
  const [busy, setBusy] = useState<Busy>(null);
  const [error, setError] = useState<string | null>(null);

  async function run(action: "approve" | "reject") {
    if (action === "reject" && !reason.trim()) {
      setReasonError("Add a short reason — it's kept with the record.");
      controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
      document.getElementById(`${id}-reason`)?.focus();
      return;
    }
    setError(null);
    setBusy(action);
    const failure = await onReview(action, action === "reject" ? reason.trim() : undefined);
    // On success the parent removes this item, so only failures land here.
    if (failure) {
      setBusy(null);
      setError(failure);
      controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
    }
  }

  return (
    <motion.div animate={controls} className="flex flex-col gap-3">
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
        {rejecting ? (
          <motion.div
            key="reject"
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.22, ease: [0.22, 1, 0.36, 1] }}
            className="overflow-hidden"
          >
            <div className="field">
              <label htmlFor={`${id}-reason`} className="field-label">
                Why are you rejecting this {noun}?
              </label>
              <textarea
                id={`${id}-reason`}
                value={reason}
                onChange={(e) => {
                  setReason(e.target.value);
                  if (reasonError) setReasonError(null);
                }}
                rows={2}
                autoFocus
                disabled={busy !== null}
                aria-invalid={reasonError ? true : undefined}
                aria-describedby={`${id}-reason-error`}
                className="input review-reason"
                placeholder={reasonExamples}
              />
              <FieldError id={`${id}-reason-error`} message={reasonError} />
            </div>
            <div className="mt-3 flex flex-wrap justify-end gap-2">
              <button
                type="button"
                className="btn-secondary btn-flex btn-sm"
                disabled={busy !== null}
                onClick={() => {
                  setRejecting(false);
                  setReasonError(null);
                }}
              >
                Cancel
              </button>
              <motion.button
                type="button"
                className="btn-primary btn-flex btn-sm"
                disabled={busy !== null}
                whileHover={busy ? undefined : { y: -1 }}
                whileTap={busy ? undefined : { scale: 0.97 }}
                onClick={() => run("reject")}
              >
                {busy === "reject" ? (
                  <>
                    <Spinner size={14} /> Rejecting…
                  </>
                ) : (
                  `Reject ${noun}`
                )}
              </motion.button>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="choose"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.15 }}
            className="flex flex-wrap items-center justify-end gap-2"
          >
            {approveBlockedReason && (
              <p className="mr-auto text-xs text-ink-soft">{approveBlockedReason}</p>
            )}
            <button
              type="button"
              className="btn-secondary btn-flex btn-sm"
              disabled={busy !== null}
              onClick={() => setRejecting(true)}
            >
              Reject
            </button>
            <motion.button
              type="button"
              className="btn-approve btn-flex btn-sm"
              disabled={busy !== null || Boolean(approveBlockedReason)}
              whileHover={busy || approveBlockedReason ? undefined : { y: -1 }}
              whileTap={busy || approveBlockedReason ? undefined : { scale: 0.97 }}
              onClick={() => run("approve")}
            >
              {busy === "approve" ? (
                <>
                  <Spinner size={14} /> Approving…
                </>
              ) : (
                <>
                  <CheckIcon /> Approve
                </>
              )}
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  );
}
