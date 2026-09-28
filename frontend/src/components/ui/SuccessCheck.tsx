"use client";

import { motion } from "motion/react";

// Forest-green circle that pops in, then draws its checkmark.
export function SuccessCheck({ size = 56 }: { size?: number }) {
  return (
    <motion.svg
      width={size}
      height={size}
      viewBox="0 0 52 52"
      initial={{ scale: 0.6, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ type: "spring", stiffness: 260, damping: 18 }}
      aria-hidden="true"
    >
      <circle cx="26" cy="26" r="25" fill="var(--forest)" />
      <motion.path
        d="M15 27l7 7 15-16"
        fill="none"
        stroke="var(--gold-soft)"
        strokeWidth="4"
        strokeLinecap="round"
        strokeLinejoin="round"
        initial={{ pathLength: 0 }}
        animate={{ pathLength: 1 }}
        transition={{ delay: 0.15, duration: 0.4, ease: "easeOut" }}
      />
    </motion.svg>
  );
}
