"use client";

import { AnimatePresence, motion, useAnimationControls, type Variants } from "motion/react";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";

import { FieldError } from "@/components/ui/FieldError";
import { Spinner } from "@/components/ui/Spinner";
import { FileDrop } from "@/components/upload/FileDrop";
import { UploadSteps, type UploadPhase } from "@/components/upload/UploadSteps";
import { UploadSuccess } from "@/components/upload/UploadSuccess";
import {
  completeUpload,
  initUpload,
  UploadError,
  uploadToCloudinary,
  type CloudinaryResult,
} from "@/lib/uploadClient";
import {
  checkFile,
  EKITI_LGAS,
  isVideo,
  RIGHTS_OPTIONS,
  UPLOAD_FOLDERS,
  type AssetRecord,
  type InitResponse,
} from "@/lib/uploads";

type Fields = {
  contributor: string;
  rights_status: string;
  folder: string;
  source: string;
  location_lga: string;
  description: string;
  related_content_id: string;
};
type FieldName = keyof Fields | "file";

const EMPTY: Fields = {
  contributor: "",
  rights_status: "",
  folder: "",
  source: "",
  location_lga: "",
  description: "",
  related_content_id: "",
};

// Progress through the whole submission, for the button fill.
const PHASE_SPAN: Record<UploadPhase, [number, number]> = {
  preparing: [0, 0.06],
  uploading: [0.06, 0.92],
  verifying: [0.92, 0.97],
};

const BUTTON_LABEL: Record<UploadPhase, string> = {
  preparing: "Preparing your upload…",
  uploading: "Uploading",
  verifying: "Verifying upload…",
};

/**
 * An asset created by /init that hasn't been completed yet. Kept so a retry
 * with the same file and details resumes it instead of starting a new one.
 */
type Pending = { key: string; init: InitResponse; uploaded?: CloudinaryResult };

const stagger: Variants = { show: { transition: { staggerChildren: 0.07, delayChildren: 0.1 } } };
const rise: Variants = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.4, ease: [0.22, 1, 0.36, 1] } },
};

function trimmedOrNull(value: string): string | null {
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

export function UploadForm({ initialFolder }: { initialFolder?: string }) {
  const card = useAnimationControls();
  const [fields, setFields] = useState<Fields>({ ...EMPTY, folder: initialFolder ?? "" });
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [errors, setErrors] = useState<Partial<Record<FieldName, string>>>({});
  const [errorTick, setErrorTick] = useState(0);
  const [phase, setPhase] = useState<UploadPhase | "idle" | "success">("idle");
  const [uploadFraction, setUploadFraction] = useState(0);
  const [formError, setFormError] = useState<{ message: string; signInAgain: boolean } | null>(null);
  const [result, setResult] = useState<AssetRecord | null>(null);
  const [showLink, setShowLink] = useState(false);
  // True when the last attempt failed partway and "Try again" will resume it.
  const [resumable, setResumable] = useState(false);
  const pending = useRef<Pending | null>(null);
  const abort = useRef<AbortController | null>(null);

  const busy = phase === "preparing" || phase === "uploading" || phase === "verifying";

  // Revoke each preview URL once it's replaced or the form unmounts.
  useEffect(() => {
    return () => {
      if (previewUrl) URL.revokeObjectURL(previewUrl);
    };
  }, [previewUrl]);

  // Warn before leaving mid-upload.
  useEffect(() => {
    if (!busy) return;
    const warn = (event: BeforeUnloadEvent) => event.preventDefault();
    window.addEventListener("beforeunload", warn);
    return () => window.removeEventListener("beforeunload", warn);
  }, [busy]);

  function setField(name: keyof Fields, value: string) {
    setFields((f) => ({ ...f, [name]: value }));
    if (errors[name]) setErrors((e) => ({ ...e, [name]: undefined }));
  }

  function selectFile(next: File | null) {
    // A bad pick is refused outright, keeping any file already chosen.
    const problem = next ? checkFile(next) : null;
    setErrors((e) => ({ ...e, file: problem ? `“${next!.name}”: ${problem}` : undefined }));
    if (problem) {
      setErrorTick((t) => t + 1);
      return;
    }
    setFile(next);
    setPreviewUrl(next ? URL.createObjectURL(next) : null);
  }

  function validate(): Partial<Record<FieldName, string>> {
    const found: Partial<Record<FieldName, string>> = {};
    if (!file) found.file = "Choose a photo or video to upload.";
    else {
      const problem = checkFile(file);
      if (problem) found.file = problem;
    }
    if (!fields.folder) found.folder = "Pick the collection this belongs in.";
    if (!fields.contributor.trim()) found.contributor = "Tell us who to credit.";
    if (!fields.rights_status) found.rights_status = "Let us know whether we can share it.";
    return found;
  }

  function fail(message: string, signInAgain = false) {
    setFormError({ message, signInAgain });
    card.start({ x: [0, -10, 9, -6, 4, 0], transition: { duration: 0.45 } });
  }

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (busy) return;
    setFormError(null);

    const found = validate();
    setErrors(found);
    if (Object.keys(found).length > 0 || !file) {
      setErrorTick((t) => t + 1);
      fail("A few details need your attention before we can upload.");
      const first = (["file", "folder", "contributor", "rights_status"] as const).find((k) => found[k]);
      const target = first && document.getElementById(first === "file" ? "upload-file" : first);
      if (target) {
        target.focus({ preventScroll: true });
        target.closest(".field")?.scrollIntoView({ behavior: "smooth", block: "center" });
      }
      return;
    }

    const payload = {
      contributor: fields.contributor.trim(),
      rights_status: fields.rights_status,
      folder: fields.folder,
      source: trimmedOrNull(fields.source),
      location_lga: trimmedOrNull(fields.location_lga),
      description: trimmedOrNull(fields.description),
      related_content_id: trimmedOrNull(fields.related_content_id),
    };
    const key = JSON.stringify([payload, file.name, file.size, file.lastModified]);
    let current = pending.current?.key === key ? pending.current : null;

    const controller = new AbortController();
    abort.current = controller;
    setUploadFraction(0);

    try {
      if (!current) {
        setPhase("preparing");
        const init = await initUpload(payload);
        // The backend's limits win over the form's built-in copy.
        const problem = checkFile(file, init.allowed_formats, init.max_file_bytes);
        if (problem) {
          setErrors({ file: problem });
          setErrorTick((t) => t + 1);
          throw new UploadError(problem, true);
        }
        current = { key, init };
        pending.current = current;
      }

      if (!current.uploaded) {
        setPhase("uploading");
        current.uploaded = await uploadToCloudinary(file, current.init, setUploadFraction, controller.signal);
      } else {
        setUploadFraction(1);
      }

      setPhase("verifying");
      const asset = await completeUpload(current.init.asset_id, current.uploaded);
      pending.current = null;
      setResult(asset);
      setPhase("success");
    } catch (err) {
      const error =
        err instanceof UploadError ? err : new UploadError("Something went wrong. Please try again.", true);
      if (error.startOver) pending.current = null;
      setResumable(pending.current !== null);
      setPhase("idle");
      if (!controller.signal.aborted) fail(error.message, error.signInAgain);
      else setFormError({ message: "Upload cancelled. Your details are still here when you're ready.", signInAgain: false });
    } finally {
      abort.current = null;
    }
  }

  function startAnother() {
    setFields((f) => ({ ...EMPTY, contributor: f.contributor, rights_status: f.rights_status }));
    selectFile(null);
    setResult(null);
    setFormError(null);
    setErrors({});
    setShowLink(false);
    setResumable(false);
    setPhase("idle");
  }

  const activePhase = busy ? phase : null;
  const overall = activePhase
    ? PHASE_SPAN[activePhase][0] +
      (PHASE_SPAN[activePhase][1] - PHASE_SPAN[activePhase][0]) * (activePhase === "uploading" ? uploadFraction : 1)
    : 0;
  const canResume = !busy && resumable && formError !== null;
  const folderHint = UPLOAD_FOLDERS.find((f) => f.value === fields.folder)?.hint;
  const rightsHint = RIGHTS_OPTIONS.find((r) => r.value === fields.rights_status)?.hint;

  return (
    <motion.div
      initial={{ opacity: 0, y: 24 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="w-full max-w-2xl"
    >
      <motion.div animate={card} className="form-card overflow-hidden">
        <div className="form-card-band" />
        <div className="px-6 pb-9 pt-8 sm:px-10">
          <AnimatePresence mode="wait" initial={false}>
            {phase === "success" && result ? (
              <UploadSuccess
                key="success"
                asset={result}
                previewUrl={previewUrl}
                video={file ? isVideo(file) : false}
                fileName={file?.name ?? ""}
                onAnother={startAnother}
              />
            ) : (
              <motion.div key="form" exit={{ opacity: 0, scale: 0.98 }} transition={{ duration: 0.2 }}>
                <div className="eyebrow-row mb-3">
                  <span className="eyebrow-dot" /> Pín ìtàn rẹ · Share your story
                </div>
                <h1 className="font-display text-3xl font-medium tracking-tight sm:text-4xl">
                  Add to the <em className="text-forest-2">archive</em>
                </h1>
                <p className="mt-2 max-w-[52ch] text-sm text-ink-soft">
                  Thirty years of Ekiti, told by the people who lived it. Every upload is reviewed by
                  the team before it appears anywhere on the site.
                </p>

                <motion.form
                  onSubmit={handleSubmit}
                  noValidate
                  className="mt-8 flex flex-col gap-7"
                  variants={stagger}
                  initial="hidden"
                  animate="show"
                >
                  <fieldset disabled={busy} className="contents">
                    <motion.section variants={rise} className="form-section">
                      <h2 className="section-heading">
                        <span className="section-num">1</span> Your photo or video
                      </h2>
                      <FileDrop
                        file={file}
                        previewUrl={previewUrl}
                        error={errors.file ?? null}
                        errorTick={errorTick}
                        disabled={busy}
                        onSelect={selectFile}
                      />
                    </motion.section>

                    <motion.section variants={rise} className="form-section">
                      <h2 className="section-heading">
                        <span className="section-num">2</span> What is it?
                      </h2>

                      <div className="field">
                        <label htmlFor="folder" className="field-label">Collection</label>
                        <div className="select-wrap">
                          <select
                            id="folder"
                            value={fields.folder}
                            onChange={(e) => setField("folder", e.target.value)}
                            aria-invalid={errors.folder ? true : undefined}
                            aria-describedby="folder-hint folder-error"
                            className="input"
                            required
                          >
                            <option value="" disabled>Choose a collection…</option>
                            {UPLOAD_FOLDERS.map((f) => (
                              <option key={f.value} value={f.value}>{f.label}</option>
                            ))}
                          </select>
                          <Chevron />
                        </div>
                        <Hint id="folder-hint" text={folderHint} />
                        <FieldError id="folder-error" message={errors.folder ?? null} />
                      </div>

                      <div className="field">
                        <div className="field-label-row">
                          <label htmlFor="description" className="field-label">Description</label>
                          <span className="field-optional">Optional</span>
                        </div>
                        <textarea
                          id="description"
                          value={fields.description}
                          onChange={(e) => setField("description", e.target.value)}
                          className="input"
                          rows={3}
                          placeholder="Who, what, when — e.g. “Market day at Oja Oba, Ado-Ekiti, around 1998”"
                        />
                      </div>

                      <div className="grid gap-5 sm:grid-cols-2">
                        <div className="field">
                          <div className="field-label-row">
                            <label htmlFor="location_lga" className="field-label">Local Government Area</label>
                            <span className="field-optional">Optional</span>
                          </div>
                          <input
                            id="location_lga"
                            list="ekiti-lgas"
                            value={fields.location_lga}
                            onChange={(e) => setField("location_lga", e.target.value)}
                            className="input"
                            placeholder="Start typing, e.g. Ikere"
                            autoComplete="off"
                          />
                          <datalist id="ekiti-lgas">
                            {EKITI_LGAS.map((lga) => (
                              <option key={lga} value={lga} />
                            ))}
                          </datalist>
                        </div>

                        <div className="field">
                          <div className="field-label-row">
                            <label htmlFor="source" className="field-label">Source</label>
                            <span className="field-optional">Optional</span>
                          </div>
                          <input
                            id="source"
                            value={fields.source}
                            onChange={(e) => setField("source", e.target.value)}
                            className="input"
                            placeholder="Family album, newspaper, archive…"
                          />
                        </div>
                      </div>
                    </motion.section>

                    <motion.section variants={rise} className="form-section">
                      <h2 className="section-heading">
                        <span className="section-num">3</span> Credit &amp; rights
                      </h2>

                      <div className="grid gap-5 sm:grid-cols-2">
                        <div className="field">
                          <label htmlFor="contributor" className="field-label">Credit as</label>
                          <input
                            id="contributor"
                            value={fields.contributor}
                            onChange={(e) => setField("contributor", e.target.value)}
                            aria-invalid={errors.contributor ? true : undefined}
                            aria-describedby="contributor-error"
                            className="input"
                            placeholder="Your name or the photographer's"
                            autoComplete="name"
                            required
                          />
                          <FieldError id="contributor-error" message={errors.contributor ?? null} />
                        </div>

                        <div className="field">
                          <label htmlFor="rights_status" className="field-label">Rights</label>
                          <div className="select-wrap">
                            <select
                              id="rights_status"
                              value={fields.rights_status}
                              onChange={(e) => setField("rights_status", e.target.value)}
                              aria-invalid={errors.rights_status ? true : undefined}
                              aria-describedby="rights-hint rights_status-error"
                              className="input"
                              required
                            >
                              <option value="" disabled>Can we share it?</option>
                              {RIGHTS_OPTIONS.map((r) => (
                                <option key={r.value} value={r.value}>{r.label}</option>
                              ))}
                            </select>
                            <Chevron />
                          </div>
                          <Hint id="rights-hint" text={rightsHint} />
                          <FieldError id="rights_status-error" message={errors.rights_status ?? null} />
                        </div>
                      </div>

                      <div>
                        <button
                          type="button"
                          className="link-btn"
                          aria-expanded={showLink}
                          aria-controls="related-field"
                          onClick={() => setShowLink((v) => !v)}
                        >
                          {showLink ? "− " : "+ "}Link it to an existing story or page
                        </button>
                        <AnimatePresence initial={false}>
                          {showLink && (
                            <motion.div
                              id="related-field"
                              initial={{ opacity: 0, height: 0 }}
                              animate={{ opacity: 1, height: "auto" }}
                              exit={{ opacity: 0, height: 0 }}
                              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
                              className="overflow-hidden"
                            >
                              <div className="field pt-3">
                                <div className="field-label-row">
                                  <label htmlFor="related_content_id" className="field-label">Related content ID</label>
                                  <span className="field-optional">Optional</span>
                                </div>
                                <input
                                  id="related_content_id"
                                  value={fields.related_content_id}
                                  onChange={(e) => setField("related_content_id", e.target.value)}
                                  className="input"
                                  placeholder="e.g. timeline-1996-state-creation"
                                />
                                <p className="field-hint">If the team gave you an ID for a timeline event or story, paste it here.</p>
                              </div>
                            </motion.div>
                          )}
                        </AnimatePresence>
                      </div>
                    </motion.section>
                  </fieldset>

                  <motion.div variants={rise} className="flex flex-col gap-4 border-t border-dashed border-line pt-6">
                    <AnimatePresence initial={false}>
                      {formError && !busy && (
                        <motion.div
                          key="error"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="alert alert-error" role="alert">
                            <span aria-hidden="true">●</span>
                            <span>
                              {formError.message}
                              {formError.signInAgain && (
                                <>
                                  {" "}
                                  <Link href="/login?callbackUrl=/upload" className="font-semibold underline">
                                    Sign in again
                                  </Link>
                                </>
                              )}
                            </span>
                          </div>
                        </motion.div>
                      )}
                      {activePhase && (
                        <motion.div
                          key="steps"
                          initial={{ opacity: 0, height: 0 }}
                          animate={{ opacity: 1, height: "auto" }}
                          exit={{ opacity: 0, height: 0 }}
                          className="flex justify-center overflow-hidden"
                        >
                          <UploadSteps phase={activePhase} uploadFraction={uploadFraction} />
                        </motion.div>
                      )}
                    </AnimatePresence>

                    <div className="flex flex-col-reverse items-stretch gap-3 sm:flex-row sm:items-center sm:justify-between">
                      <p className="text-center text-xs text-ink-soft sm:text-left">
                        {phase === "uploading" ? (
                          <button type="button" className="link-btn" onClick={() => abort.current?.abort()}>
                            Cancel upload
                          </button>
                        ) : (
                          "Required: file, collection, credit and rights."
                        )}
                      </p>
                      <motion.button
                        type="submit"
                        disabled={busy}
                        aria-live="polite"
                        whileHover={busy ? undefined : { y: -1 }}
                        whileTap={busy ? undefined : { scale: 0.97 }}
                        className="btn-primary btn-progress min-w-[240px]"
                      >
                        {activePhase && (
                          <motion.span
                            className="btn-progress-fill"
                            initial={{ width: "0%" }}
                            animate={{ width: `${overall * 100}%` }}
                            transition={{ duration: 0.3, ease: "easeOut" }}
                          />
                        )}
                        {activePhase ? (
                          <>
                            <Spinner />
                            {BUTTON_LABEL[activePhase]}
                            {activePhase === "uploading" && (
                              <span className="tabular-nums">{Math.round(uploadFraction * 100)}%</span>
                            )}
                          </>
                        ) : canResume ? (
                          "Try again"
                        ) : (
                          "Submit for review"
                        )}
                      </motion.button>
                    </div>
                  </motion.div>
                </motion.form>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </motion.div>
  );
}

function Chevron() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="m6 9 6 6 6-6" />
    </svg>
  );
}

/** Explains the current dropdown choice; cross-fades when it changes. */
function Hint({ id, text }: { id: string; text: string | undefined }) {
  return (
    <div id={id}>
      <AnimatePresence mode="wait" initial={false}>
        {text && (
          <motion.p
            key={text}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.18 }}
            className="field-hint overflow-hidden"
          >
            {text}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}
