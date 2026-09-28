"use client";

import { AnimatePresence, motion } from "motion/react";

/** Inline error under a form field; slides in and out as it changes. */
export function FieldError({ id, message }: { id: string; message: string | null | undefined }) {
  return (
    <AnimatePresence mode="wait" initial={false}>
      {message && (
        <motion.p
          key={message}
          id={id}
          initial={{ opacity: 0, height: 0, y: -4 }}
          animate={{ opacity: 1, height: "auto", y: 0 }}
          exit={{ opacity: 0, height: 0 }}
          transition={{ duration: 0.2 }}
          className="field-error overflow-hidden"
          role="alert"
        >
          <span aria-hidden="true">●</span>
          {message}
        </motion.p>
      )}
    </AnimatePresence>
  );
}
