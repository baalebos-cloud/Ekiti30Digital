"use client";

import { motion } from "motion/react";
import { Fragment } from "react";

export type UploadPhase = "preparing" | "uploading" | "verifying";

const STEPS: { phase: UploadPhase; label: string }[] = [
  { phase: "preparing", label: "Preparing" },
  { phase: "uploading", label: "Uploading" },
  { phase: "verifying", label: "Verifying" },
];

/** Three-step trail shown while an upload runs. */
export function UploadSteps({ phase, uploadFraction }: { phase: UploadPhase; uploadFraction: number }) {
  const current = STEPS.findIndex((s) => s.phase === phase);

  return (
    <div className="steps" aria-hidden="true">
      {STEPS.map((step, index) => {
        const state = index < current ? "done" : index === current ? "active" : "todo";
        // The line after "Uploading" tracks real upload progress.
        const lineFill = index < current ? 1 : index === current && step.phase === "uploading" ? uploadFraction : 0;
        return (
          <Fragment key={step.phase}>
            <div className={`step is-${state}`}>
              <span className="step-dot">
                {state === "done" ? (
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none">
                    <motion.path
                      d="M5 12.5l4.5 4.5L19 7.5"
                      stroke="var(--gold-soft)"
                      strokeWidth="3.2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ duration: 0.3, ease: "easeOut" }}
                    />
                  </svg>
                ) : state === "active" ? (
                  <motion.span
                    className="absolute inset-[-6px] rounded-full"
                    style={{ border: "2px solid var(--gold)" }}
                    animate={{ scale: [0.85, 1.15], opacity: [0.9, 0] }}
                    transition={{ duration: 1.2, repeat: Infinity, ease: "easeOut" }}
                  />
                ) : null}
              </span>
              {step.label}
            </div>
            {index < STEPS.length - 1 && (
              <div className="step-line">
                <motion.div
                  initial={false}
                  animate={{ scaleX: lineFill }}
                  transition={{ duration: 0.35, ease: "easeOut" }}
                />
              </div>
            )}
          </Fragment>
        );
      })}
    </div>
  );
}
