"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useState } from "react";

import { Spinner } from "@/components/ui/Spinner";
import { SuccessCheck } from "@/components/ui/SuccessCheck";
import {
  contentApi,
  NOUN,
  templateUrl,
  type ContentAdminKind,
  type ImageImportResult,
  type ImportSummary,
} from "@/lib/contentAdmin";
import { formatBytes } from "@/lib/uploads";

type Files = { csv: File; zip: File | null };

type Stage =
  | { step: "choose" }
  | { step: "previewing"; files: Files }
  | { step: "preview"; files: Files; summary: ImportSummary }
  | { step: "importing"; files: Files; summary: ImportSummary }
  | { step: "done"; summary: ImportSummary };

type Props = {
  kind: ContentAdminKind;
  onClose: () => void;
  /** Called after a real import, so the list can reload. */
  onImported: (summary: ImportSummary) => void;
};

const SOURCE_FILE: Record<ContentAdminKind, string> = {
  lgas: "02_LGAs/ekiti_lgas.csv",
  timeline: "03_Timeline/EKITI30_Timeline_Events_1996-2026.csv",
};

const MAX_CSV_BYTES = 2 * 1024 * 1024;
const MAX_ZIP_BYTES = 200 * 1024 * 1024;

export function CsvImport({ kind, onClose, onImported }: Props) {
  const controls = useAnimationControls();
  const [stage, setStage] = useState<Stage>({ step: "choose" });
  const [csv, setCsv] = useState<File | null>(null);
  const [zip, setZip] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Images come only from a zip, and only LGAs have them.
  const withImages = kind === "lgas";

  function fail(message: string) {
    setError(message);
    controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
  }

  function pickCsv(file: File | null) {
    setError(null);
    if (!file) return;
    if (!/\.csv$/i.test(file.name)) return fail("Choose a .csv file.");
    if (file.size > MAX_CSV_BYTES) return fail("The CSV must be at most 2 MB.");
    setCsv(file);
  }

  function pickZip(file: File | null) {
    setError(null);
    if (!file) return;
    if (!/\.zip$/i.test(file.name)) return fail("Choose a .zip file of images.");
    if (file.size > MAX_ZIP_BYTES) return fail("The images zip must be at most 200 MB.");
    setZip(file);
  }

  async function preview() {
    if (!csv) return;
    setError(null);
    const files = { csv, zip: withImages ? zip : null };
    setStage({ step: "previewing", files });
    const result = await contentApi.importCsv(kind, files.csv, true, files.zip);
    if (!result.ok) {
      setStage({ step: "choose" });
      return fail(result.message);
    }
    setStage({ step: "preview", files, summary: result.data });
  }

  async function confirm() {
    if (stage.step !== "preview") return;
    setError(null);
    setStage({ ...stage, step: "importing" });
    const result = await contentApi.importCsv(kind, stage.files.csv, false, stage.files.zip);
    if (!result.ok) {
      setStage({ ...stage, step: "preview" });
      return fail(result.message);
    }
    setStage({ step: "done", summary: result.data });
    onImported(result.data);
  }

  function startOver() {
    setCsv(null);
    setZip(null);
    setStage({ step: "choose" });
  }

  const busy = stage.step === "previewing" || stage.step === "importing";

  return (
    <motion.div animate={controls} className="form-card overflow-hidden">
      <div className="form-card-band" />
      <div className="p-6 sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="eyebrow-row">
              <span className="eyebrow-dot" /> Import CSV
            </p>
            <h2 className="font-display text-2xl">Update {NOUN[kind].many} from a spreadsheet</h2>
            <p className="mt-1 max-w-[62ch] text-sm text-ink-soft">
              Same columns as <code className="text-xs">{SOURCE_FILE[kind]}</code>. Rows are matched by{" "}
              {kind === "lgas" ? "LGA name" : "event ID"}: new ones are added, changed ones updated, and anything not in
              the file is left alone. You&apos;ll see what will change before anything is saved.
            </p>
          </div>
          <div className="flex flex-col items-end gap-2">
            <button type="button" onClick={onClose} className="link-btn" disabled={busy}>
              ← Back to the list
            </button>
            <a href={templateUrl(kind)} download className="link-btn flex items-center gap-1.5">
              <DownloadIcon /> Download CSV template
            </a>
          </div>
        </div>

        <AnimatePresence initial={false}>
          {error && (
            <motion.div
              key={error}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-5 overflow-hidden"
            >
              <div className="alert alert-error" role="alert">
                <span aria-hidden="true">●</span>
                <span>{error}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait" initial={false}>
          <motion.div
            key={stage.step === "importing" ? "preview" : stage.step === "previewing" ? "choose" : stage.step}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -6 }}
            transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
            className="mt-6"
          >
            {(stage.step === "choose" || stage.step === "previewing") && (
              <div className="flex flex-col gap-4">
                <div className={`grid gap-4 ${withImages ? "sm:grid-cols-2" : ""}`}>
                  <FilePicker
                    label="CSV file"
                    hint="UTF-8, up to 2 MB"
                    accept=".csv,text/csv"
                    file={csv}
                    disabled={busy}
                    onPick={pickCsv}
                    onClear={() => setCsv(null)}
                  />
                  {withImages && (
                    <FilePicker
                      label="Images (zip)"
                      optional
                      hint="Name each image after its LGA's slug, e.g. ado-ekiti.jpg. JPG, PNG or WebP, up to 10 MB each."
                      accept=".zip,application/zip"
                      file={zip}
                      disabled={busy}
                      onPick={pickZip}
                      onClear={() => setZip(null)}
                    />
                  )}
                </div>
                <div className="flex justify-end">
                  <motion.button
                    type="button"
                    className="btn-primary btn-flex btn-sm min-w-[160px] justify-center"
                    disabled={!csv || busy}
                    whileHover={!csv || busy ? undefined : { y: -1 }}
                    whileTap={!csv || busy ? undefined : { scale: 0.97 }}
                    onClick={preview}
                  >
                    {stage.step === "previewing" ? (
                      <>
                        <Spinner size={14} /> Checking…
                      </>
                    ) : (
                      "Preview import"
                    )}
                  </motion.button>
                </div>
              </div>
            )}

            {(stage.step === "preview" || stage.step === "importing") && (
              <Preview
                kind={kind}
                files={stage.files}
                summary={stage.summary}
                importing={stage.step === "importing"}
                onConfirm={confirm}
                onChooseAgain={() => setStage({ step: "choose" })}
              />
            )}

            {stage.step === "done" && (
              <div className="flex flex-col gap-5">
                <div className="flex flex-col items-center gap-3 py-4 text-center">
                  <SuccessCheck />
                  <p className="font-display text-xl">Import complete</p>
                  <p className="text-sm text-ink-soft">
                    {countLine(stage.summary)}. Every changed row now shows you as its last editor.
                  </p>
                </div>
                <Results kind={kind} summary={stage.summary} />
                <div className="flex justify-center gap-2 border-t border-line pt-5">
                  <button type="button" className="btn-secondary btn-flex btn-sm" onClick={startOver}>
                    Import another file
                  </button>
                  <button type="button" className="btn-primary btn-flex btn-sm" onClick={onClose}>
                    Back to the list
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>
      </div>
    </motion.div>
  );
}

function countLine(s: ImportSummary): string {
  const parts = [`${s.created.length} added`, `${s.updated.length} updated`, `${s.unchanged.length} unchanged`, `${s.skipped.length} skipped`];
  if (s.images?.length) parts.push(`${s.images.filter((i) => i.status === "attached").length} of ${s.images.length} images attached`);
  return parts.join(", ");
}

function FilePicker({
  label,
  hint,
  accept,
  file,
  optional,
  disabled,
  onPick,
  onClear,
}: {
  label: string;
  hint: string;
  accept: string;
  file: File | null;
  optional?: boolean;
  disabled: boolean;
  onPick: (file: File | null) => void;
  onClear: () => void;
}) {
  const [dragging, setDragging] = useState(false);
  return (
    <div className="field">
      <div className="field-label-row">
        <span className="field-label">{label}</span>
        {optional && <span className="field-optional">Optional</span>}
      </div>
      <label
        className={`dropzone ${dragging ? "is-dragging" : ""} ${disabled ? "is-disabled" : ""} ${file ? "has-file" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          if (!disabled) onPick(e.dataTransfer.files?.[0] ?? null);
        }}
      >
        <input
          type="file"
          accept={accept}
          className="sr-only"
          disabled={disabled}
          aria-label={label}
          onChange={(e) => {
            onPick(e.target.files?.[0] ?? null);
            e.target.value = "";
          }}
        />
        <span className="dropzone-icon" aria-hidden="true">
          {file ? <FileIcon /> : <UploadIcon />}
        </span>
        <span className="dropzone-title">{file ? file.name : "Choose a file, or drop it here"}</span>
        <span className="text-xs text-ink-soft">{file ? formatBytes(file.size) : hint}</span>
      </label>
      {file && !disabled && (
        <button type="button" className="link-btn self-start" onClick={onClear}>
          Remove
        </button>
      )}
    </div>
  );
}

function Preview({
  kind,
  files,
  summary,
  importing,
  onConfirm,
  onChooseAgain,
}: {
  kind: ContentAdminKind;
  files: Files;
  summary: ImportSummary;
  importing: boolean;
  onConfirm: () => void;
  onChooseAgain: () => void;
}) {
  const rowChanges = summary.created.length + summary.updated.length;
  const imageChanges = summary.images?.filter((i) => i.status === "would_attach").length ?? 0;
  const changes = rowChanges + imageChanges;

  return (
    <div className="flex flex-col gap-5">
      <p className="text-sm">
        <span className="font-semibold">{files.csv.name}</span>
        {files.zip && <span className="font-semibold"> + {files.zip.name}</span>}
        <span className="text-ink-soft"> · nothing saved yet</span>
      </p>

      <Results kind={kind} summary={summary} />

      {summary.updated.length > 0 && (
        <p className="text-xs text-ink-soft">
          Updated rows take the file&apos;s values for every column, replacing any edits made here since. Check the list above before you confirm.
        </p>
      )}

      <div className="flex flex-wrap items-center justify-end gap-3 border-t border-line pt-5">
        {importing && imageChanges > 0 && (
          <p className="mr-auto text-xs text-ink-soft">Uploading {imageChanges} image{imageChanges === 1 ? "" : "s"} — this can take a minute.</p>
        )}
        <button type="button" className="btn-secondary btn-flex btn-sm" onClick={onChooseAgain} disabled={importing}>
          Choose different files
        </button>
        <motion.button
          type="button"
          className="btn-primary btn-flex btn-sm min-w-[160px] justify-center"
          disabled={importing || changes === 0}
          whileHover={importing || changes === 0 ? undefined : { y: -1 }}
          whileTap={importing || changes === 0 ? undefined : { scale: 0.97 }}
          onClick={onConfirm}
        >
          {importing ? (
            <>
              <Spinner size={14} /> Importing…
            </>
          ) : changes === 0 ? (
            "Nothing to import"
          ) : (
            `Import ${changes} ${changes === 1 ? "change" : "changes"}`
          )}
        </motion.button>
      </div>
    </div>
  );
}

/** Row counts with the rows behind them, and (LGAs) what happens to each image. */
function Results({ kind, summary }: { kind: ContentAdminKind; summary: ImportSummary }) {
  const dry = summary.dry_run;
  const tiles = [
    { label: dry ? "Will be added" : "Added", keys: summary.created, tone: "forest" },
    { label: dry ? "Will be updated" : "Updated", keys: summary.updated, tone: "teal" },
    { label: "Unchanged", keys: summary.unchanged, tone: "muted" },
    { label: "Skipped", keys: summary.skipped.map((s) => s.key ?? `line ${s.line}`), tone: "rust" },
  ] as const;
  const images = summary.images ?? [];

  return (
    <div className="flex flex-col gap-4">
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        {tiles.map((tile, i) => (
          <motion.div
            key={tile.label}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.06, duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
            className="rounded-[var(--radius-s)] border border-line bg-bg-raised p-4"
          >
            <p className="font-display text-3xl tabular-nums" style={{ color: tile.tone === "muted" ? "var(--ink-soft)" : `var(--${tile.tone})` }}>
              {tile.keys.length}
            </p>
            <p className="text-xs font-semibold text-ink-soft">{tile.label}</p>
          </motion.div>
        ))}
      </div>

      {tiles.slice(0, 2).map(
        (tile) =>
          tile.keys.length > 0 && (
            <details key={tile.label} className="text-sm" open={tile.keys.length <= 6}>
              <summary className="cursor-pointer font-semibold">
                {tile.label}: {tile.keys.length} {tile.keys.length === 1 ? NOUN[kind].one : NOUN[kind].many}
              </summary>
              <p className="mt-2 break-words font-mono text-xs text-ink-soft">{tile.keys.join(", ")}</p>
            </details>
          ),
      )}

      {summary.skipped.length > 0 && (
        <div className="alert alert-notice flex-col" role="status">
          <p className="font-semibold">{dry ? "These rows will be skipped" : "These rows were skipped"} — fix them in the file and import again:</p>
          <ul className="mt-1 flex flex-col gap-1 text-sm">
            {summary.skipped.map((s) => (
              <li key={s.line}>
                Line {s.line}
                {s.key ? ` (${s.key})` : ""}: {s.reason}
              </li>
            ))}
          </ul>
        </div>
      )}

      {images.length > 0 && <ImageResults images={images} />}
    </div>
  );
}

const IMAGE_STATUS: Record<ImageImportResult["status"], { label: string; className: string }> = {
  attached: { label: "Attached", className: "label-pill" },
  would_attach: { label: "Will attach", className: "label-pill" },
  skipped: { label: "Skipped", className: "label-pill is-muted" },
  failed: { label: "Failed", className: "label-pill is-danger" },
};

function ImageResults({ images }: { images: ImageImportResult[] }) {
  const used = images.filter((i) => i.status === "attached" || i.status === "would_attach").length;
  return (
    <div className="flex flex-col gap-2">
      <p className="text-sm font-semibold">
        Images: {used} of {images.length} matched to an LGA in this CSV
      </p>
      <ul className="import-image-list">
        {images.map((image, i) => (
          <motion.li
            key={image.filename}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: Math.min(i, 12) * 0.03, duration: 0.2 }}
          >
            <span className="min-w-0 truncate font-mono text-xs">{image.filename}</span>
            <span className="text-xs text-ink-soft">{image.slug ? `→ ${image.slug}` : "→ no LGA"}</span>
            <span className={IMAGE_STATUS[image.status].className}>{IMAGE_STATUS[image.status].label}</span>
            {image.reason && <span className="import-image-reason">{image.reason}</span>}
          </motion.li>
        ))}
      </ul>
    </div>
  );
}

function UploadIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 16V4m0 0l-4 4m4-4l4 4" />
      <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" />
    </svg>
  );
}

function FileIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M14 3H7a2 2 0 00-2 2v14a2 2 0 002 2h10a2 2 0 002-2V8z" />
      <path d="M14 3v5h5M9.5 14.5l2 2 3.5-4" />
    </svg>
  );
}

function DownloadIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M12 4v12m0 0l-4-4m4 4l4-4" />
      <path d="M4 20h16" />
    </svg>
  );
}
