"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useEffect, useState } from "react";

import { FieldError } from "@/components/ui/FieldError";
import { FILE_ACCEPT, fileFormat, formatBytes, isVideo, listFormats, MAX_UPLOAD_BYTES } from "@/lib/uploads";

type Props = {
  file: File | null;
  previewUrl: string | null;
  error: string | null;
  /** Bumped by the parent on every failed validation, to replay the shake. */
  errorTick: number;
  disabled: boolean;
  onSelect: (file: File | null) => void;
};

const INPUT_ID = "upload-file";

export function FileDrop({ file, previewUrl, error, errorTick, disabled, onSelect }: Props) {
  const [dragging, setDragging] = useState(false);
  const controls = useAnimationControls();

  useEffect(() => {
    if (error) controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
  }, [error, errorTick, controls]);

  function takeFiles(files: FileList | null) {
    const picked = files?.[0];
    if (picked) onSelect(picked);
  }

  const input = (
    <input
      id={INPUT_ID}
      type="file"
      accept={FILE_ACCEPT}
      className="sr-only"
      disabled={disabled}
      aria-invalid={error ? true : undefined}
      aria-describedby={error ? `${INPUT_ID}-error` : `${INPUT_ID}-hint`}
      onChange={(event) => {
        takeFiles(event.target.files);
        // Let the same file be picked again after removing it.
        event.target.value = "";
      }}
    />
  );

  return (
    <motion.div animate={controls} className="field">
      <AnimatePresence mode="wait" initial={false}>
        {file ? (
          <motion.div
            key="chosen"
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -6, scale: 0.98 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="file-chip"
          >
            <motion.div
              className="file-thumb"
              initial={{ rotate: -6, scale: 0.8 }}
              animate={{ rotate: -2, scale: 1 }}
              transition={{ type: "spring", stiffness: 260, damping: 16 }}
            >
              {previewUrl &&
                (isVideo(file) ? (
                  <video src={previewUrl} muted playsInline preload="metadata" />
                ) : (
                  // Hidden if the browser can't decode it; the tile's gradient shows instead.
                  // eslint-disable-next-line @next/next/no-img-element -- local blob preview
                  <img src={previewUrl} alt="" onError={(e) => (e.currentTarget.style.visibility = "hidden")} />
                ))}
            </motion.div>
            <div className="min-w-0 flex-1">
              <p className="truncate font-medium" title={file.name}>{file.name}</p>
              <p className="mt-0.5 text-xs text-ink-soft">
                {fileFormat(file)?.toUpperCase() ?? "Unknown type"} · {formatBytes(file.size)}
              </p>
              <div className="mt-1.5 flex gap-3">
                <label htmlFor={INPUT_ID} className={`link-btn ${disabled ? "pointer-events-none opacity-50" : ""}`}>
                  Change
                </label>
                <button type="button" className="link-btn is-danger" disabled={disabled} onClick={() => onSelect(null)}>
                  Remove
                </button>
              </div>
            </div>
            {input}
          </motion.div>
        ) : (
          <motion.label
            key="empty"
            htmlFor={INPUT_ID}
            initial={{ opacity: 0 }}
            animate={{ opacity: 1, scale: dragging ? 1.01 : 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className={`dropzone adire-bg ${dragging ? "is-dragging" : ""} ${error ? "is-invalid" : ""} ${disabled ? "is-disabled" : ""}`}
            onDragEnter={(event) => {
              event.preventDefault();
              if (!disabled) setDragging(true);
            }}
            onDragOver={(event) => event.preventDefault()}
            onDragLeave={(event) => {
              if (!event.currentTarget.contains(event.relatedTarget as Node | null)) setDragging(false);
            }}
            onDrop={(event) => {
              event.preventDefault();
              setDragging(false);
              if (!disabled) takeFiles(event.dataTransfer.files);
            }}
          >
            <motion.span
              className="dropzone-icon"
              animate={dragging ? { y: -4, scale: 1.08 } : { y: 0, scale: 1 }}
              transition={{ type: "spring", stiffness: 300, damping: 15 }}
              aria-hidden="true"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M12 16V4" />
                <path d="m6 10 6-6 6 6" />
                <path d="M4 17v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2" />
              </svg>
            </motion.span>
            <span className="dropzone-title">
              {dragging ? "Drop it here" : <>Drag a photo or video here, or <u>browse</u></>}
            </span>
            <span id={`${INPUT_ID}-hint`} className="field-hint">
              {listFormats()} · up to {formatBytes(MAX_UPLOAD_BYTES)}
            </span>
            {input}
          </motion.label>
        )}
      </AnimatePresence>
      <FieldError id={`${INPUT_ID}-error`} message={error} />
    </motion.div>
  );
}
