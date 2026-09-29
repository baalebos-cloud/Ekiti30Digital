"use client";

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useState } from "react";

export type Toast = { id: number; message: string };

/** A toast that hides itself after a few seconds. Show one by setting it. */
export function useToast() {
  const [toast, setToast] = useState<Toast | null>(null);

  useEffect(() => {
    if (!toast) return;
    const timer = setTimeout(() => setToast(null), 3200);
    return () => clearTimeout(timer);
  }, [toast]);

  return { toast, show: (message: string) => setToast({ id: Date.now(), message }) };
}

/** Bottom-of-screen confirmation pill with a drawn check. */
export function SuccessToast({ toast }: { toast: Toast | null }) {
  return (
    <div className="review-toast-wrap" aria-live="polite">
      <AnimatePresence>
        {toast && (
          <motion.div
            key={toast.id}
            initial={{ opacity: 0, y: 24, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 12, scale: 0.98 }}
            transition={{ type: "spring", stiffness: 380, damping: 28 }}
            className="review-toast"
            role="status"
          >
            <svg width="18" height="18" viewBox="0 0 52 52" aria-hidden="true">
              <circle cx="26" cy="26" r="25" fill="var(--gold-soft)" />
              <motion.path
                d="M15 27l7 7 15-16"
                fill="none"
                stroke="var(--forest)"
                strokeWidth="5"
                strokeLinecap="round"
                strokeLinejoin="round"
                initial={{ pathLength: 0 }}
                animate={{ pathLength: 1 }}
                transition={{ delay: 0.1, duration: 0.35 }}
              />
            </svg>
            <span className="truncate">{toast.message}</span>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
