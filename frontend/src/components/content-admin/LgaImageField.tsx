"use client";

/**
 * The LGA editor's image control. LGAs only: the timeline has no images, so
 * ContentEditor renders this for kind "lgas" and nothing else.
 *
 * It only stages a file. ContentEditor uploads it (POST .../lgas/{slug}/image)
 * after the LGA itself has been saved, and passes the progress back in.
 */

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useId, useRef, useState } from "react";

import { FieldError } from "@/components/ui/FieldError";
import { IMAGE_ACCEPT, imageProblem } from "@/lib/contentAdmin";

type Props = {
  /** The image the LGA has now, if any. */
  currentUrl: string | null;
  staged: File | null;
  onStage: (file: File | null) => void;
  /** 0..1 while the staged file is being sent; null otherwise. */
  progress: number | null;
  disabled: boolean;
};

export function LgaImageField({ currentUrl, staged, onStage, progress, disabled }: Props) {
  const id = useId();
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [problem, setProblem] = useState<string | null>(null);
  // The object URL of the local preview, so it can be released.
  const previewRef = useRef<string | null>(null);

  function setPreview(file: File | null) {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    previewRef.current = file ? URL.createObjectURL(file) : null;
    setPreviewUrl(previewRef.current);
  }

  // Release the last preview when the field goes away.
  useEffect(() => () => {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
  }, []);

  const shown = (staged && previewUrl) || currentUrl;
  const uploading = progress !== null;

  function stage(file: File | null) {
    setPreview(file);
    onStage(file);
  }

  return (
    <div className="field sm:col-span-2">
      <div className="field-label-row">
        <label htmlFor={id} className="field-label">
          Image
        </label>
        <span className="field-optional">Optional</span>
      </div>
      <div className="flex flex-wrap items-center gap-4">
        <div className="lga-image-thumb">
          <AnimatePresence mode="wait" initial={false}>
            {shown ? (
              <motion.div
                key={shown}
                initial={{ opacity: 0, scale: 0.96 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className="h-full w-full"
              >
                {/* eslint-disable-next-line @next/next/no-img-element -- local preview or remote Cloudinary image */}
                <img src={shown} alt={staged ? "Selected image, not saved yet" : "Current LGA image"} />
              </motion.div>
            ) : (
              <span className="text-xs text-ink-soft">No image yet</span>
            )}
          </AnimatePresence>
        </div>
        <div className="flex min-w-0 flex-1 flex-col gap-2">
          <p className="text-sm">
            {staged ? (
              <>
                <span className="font-semibold">{staged.name}</span>
                <span className="text-ink-soft"> · uploads when you save</span>
              </>
            ) : currentUrl ? (
              <span className="text-ink-soft">This LGA has an image. Choosing another replaces it.</span>
            ) : (
              <span className="text-ink-soft">JPG, PNG or WebP, up to 10 MB.</span>
            )}
          </p>
          <div className="flex flex-wrap items-center gap-3">
            <label className={`btn-secondary btn-flex btn-sm cursor-pointer ${disabled ? "pointer-events-none opacity-55" : ""}`}>
              <input
                id={id}
                type="file"
                accept={IMAGE_ACCEPT}
                className="sr-only"
                disabled={disabled}
                aria-describedby={`${id}-error`}
                onChange={(e) => {
                  const file = e.target.files?.[0] ?? null;
                  e.target.value = "";
                  if (!file) return;
                  const issue = imageProblem(file);
                  setProblem(issue);
                  if (!issue) stage(file);
                }}
              />
              {currentUrl || staged ? "Replace image" : "Choose image"}
            </label>
            {staged && !uploading && (
              <button type="button" className="link-btn" onClick={() => stage(null)} disabled={disabled}>
                Keep the {currentUrl ? "current image" : "LGA without an image"}
              </button>
            )}
          </div>
          <AnimatePresence initial={false}>
            {uploading && (
              <motion.div
                key="progress"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <div className="upload-meter" role="progressbar" aria-label="Image upload" aria-valuemin={0} aria-valuemax={100} aria-valuenow={Math.round((progress ?? 0) * 100)}>
                  <motion.span animate={{ width: `${Math.max(4, (progress ?? 0) * 100)}%` }} transition={{ duration: 0.2 }} />
                </div>
                <p className="mt-1 text-xs text-ink-soft">
                  {progress !== null && progress < 1 ? `Uploading… ${Math.round(progress * 100)}%` : "Saving the image…"}
                </p>
              </motion.div>
            )}
          </AnimatePresence>
          <FieldError id={`${id}-error`} message={problem} />
        </div>
      </div>
    </div>
  );
}
