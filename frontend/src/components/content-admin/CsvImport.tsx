"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useState } from "react";

import { Spinner } from "@/components/ui/Spinner";
import { SuccessCheck } from "@/components/ui/SuccessCheck";
import { contentApi, NOUN, type ContentAdminKind, type ImportSummary } from "@/lib/contentAdmin";
import { formatBytes } from "@/lib/uploads";

type Stage =
  | { step: "choose" }
  | { step: "previewing"; file: File }
  | { step: "preview"; file: File; summary: ImportSummary }
  | { step: "importing"; file: File; summary: ImportSummary }
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

export function CsvImport({ kind, onClose, onImported }: Props) {
  const controls = useAnimationControls();
  const [stage, setStage] = useState<Stage>({ step: "choose" });
  const [error, setError] = useState<string | null>(null);
  const [dragging, setDragging] = useState(false);

  function fail(message: string) {
    setError(message);
    controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
  }

  async function preview(file: File) {
    setError(null);
    if (!/\.csv$/i.test(file.name)) return fail("Choose a .csv file.");
    setStage({ step: "previewing", file });
    const result = await contentApi.importCsv(kind, file, true);
    if (!result.ok) {
      setStage({ step: "choose" });
      return fail(result.message);
    }
    setStage({ step: "preview", file, summary: result.data });
  }

  async function confirm() {
    if (stage.step !== "preview") return;
    setError(null);
    setStage({ ...stage, step: "importing" });
    const result = await contentApi.importCsv(kind, stage.file, false);
    if (!result.ok) {
      setStage({ ...stage, step: "preview" });
      return fail(result.message);
    }
    setStage({ step: "done", summary: result.data });
    onImported(result.data);
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
            <p className="mt-1 max-w-[60ch] text-sm text-ink-soft">
              Same columns as <code className="text-xs">{SOURCE_FILE[kind]}</code>. Rows are matched by{" "}
              {kind === "lgas" ? "LGA name" : "event ID"}: new ones are added, changed ones updated, and anything not in
              the file is left alone. You&apos;ll see what will change before anything is saved.
            </p>
          </div>
          <button type="button" onClick={onClose} className="link-btn" disabled={busy}>
            ← Back to the list
          </button>
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
              <label
                className={`dropzone ${dragging ? "is-dragging" : ""} ${busy ? "is-disabled" : ""}`}
                onDragOver={(e) => {
                  e.preventDefault();
                  if (!busy) setDragging(true);
                }}
                onDragLeave={() => setDragging(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setDragging(false);
                  const file = e.dataTransfer.files?.[0];
                  if (file && !busy) preview(file);
                }}
              >
                <input
                  type="file"
                  accept=".csv,text/csv"
                  className="sr-only"
                  disabled={busy}
                  onChange={(e) => {
                    const file = e.target.files?.[0];
                    if (file) preview(file);
                    e.target.value = "";
                  }}
                />
                <span className="dropzone-icon" aria-hidden="true">
                  {stage.step === "previewing" ? <Spinner size={22} /> : <UploadIcon />}
                </span>
                <span className="dropzone-title">
                  {stage.step === "previewing" ? `Checking ${stage.file.name}…` : "Choose a CSV file, or drop it here"}
                </span>
                <span className="text-xs text-ink-soft">UTF-8, up to 2 MB</span>
              </label>
            )}

            {(stage.step === "preview" || stage.step === "importing") && (
              <Preview
                kind={kind}
                file={stage.file}
                summary={stage.summary}
                importing={stage.step === "importing"}
                onConfirm={confirm}
                onChooseAgain={() => setStage({ step: "choose" })}
              />
            )}

            {stage.step === "done" && (
              <div className="flex flex-col items-center gap-3 py-6 text-center">
                <SuccessCheck />
                <p className="font-display text-xl">Import complete</p>
                <p className="text-sm text-ink-soft">
                  {countLine(stage.summary)}. Every changed row now shows you as its last editor.
                </p>
                <div className="mt-2 flex gap-2">
                  <button type="button" className="btn-secondary btn-flex btn-sm" onClick={() => setStage({ step: "choose" })}>
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
  return [
    `${s.created.length} added`,
    `${s.updated.length} updated`,
    `${s.unchanged.length} unchanged`,
    `${s.skipped.length} skipped`,
  ].join(", ");
}

function Preview({
  kind,
  file,
  summary,
  importing,
  onConfirm,
  onChooseAgain,
}: {
  kind: ContentAdminKind;
  file: File;
  summary: ImportSummary;
  importing: boolean;
  onConfirm: () => void;
  onChooseAgain: () => void;
}) {
  const changes = summary.created.length + summary.updated.length;
  const tiles = [
    { label: "Will be added", value: summary.created.length, keys: summary.created, tone: "forest" },
    { label: "Will be updated", value: summary.updated.length, keys: summary.updated, tone: "teal" },
    { label: "Unchanged", value: summary.unchanged.length, keys: [], tone: "muted" },
    { label: "Skipped", value: summary.skipped.length, keys: [], tone: "rust" },
  ] as const;

  return (
    <div className="flex flex-col gap-5">
      <p className="text-sm">
        <span className="font-semibold">{file.name}</span> <span className="text-ink-soft">· {formatBytes(file.size)} · nothing saved yet</span>
      </p>

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
              {tile.value}
            </p>
            <p className="text-xs font-semibold text-ink-soft">{tile.label}</p>
          </motion.div>
        ))}
      </div>

      {tiles.slice(0, 2).map(
        (tile) =>
          tile.keys.length > 0 && (
            <details key={tile.label} className="text-sm">
              <summary className="cursor-pointer font-semibold">
                {tile.label}: {tile.keys.length} {tile.keys.length === 1 ? NOUN[kind].one : NOUN[kind].many}
              </summary>
              <p className="mt-2 break-words font-mono text-xs text-ink-soft">{tile.keys.join(", ")}</p>
            </details>
          ),
      )}

      {summary.skipped.length > 0 && (
        <div className="alert alert-notice flex-col" role="status">
          <p className="font-semibold">These rows will be skipped — fix them in the file and import again:</p>
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

      {summary.updated.length > 0 && (
        <p className="text-xs text-ink-soft">
          Updated rows take the file&apos;s values for every column, replacing any edits made here since. Check the list above before you confirm.
        </p>
      )}

      <div className="flex flex-wrap items-center justify-end gap-3 border-t border-line pt-5">
        <button type="button" className="btn-secondary btn-flex btn-sm" onClick={onChooseAgain} disabled={importing}>
          Choose a different file
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

function UploadIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 16V4m0 0l-4 4m4-4l4 4" />
      <path d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2" />
    </svg>
  );
}
