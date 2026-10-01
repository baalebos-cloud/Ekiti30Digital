"use client";

/**
 * Add or edit one homepage leader, landmark, moment or hero photo, with its
 * image. Same flow as the LGA editor (content-admin/ContentEditor): save the
 * text first, then upload a staged image, so a failed upload never loses
 * the text and can be retried.
 */

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useEffect, useId, useRef, useState } from "react";

import { AuditLine } from "@/components/content-admin/AuditLine";
import { ImageField } from "@/components/content-admin/ImageField";
import { IconPicker } from "@/components/homepage-admin/IconPicker";
import { LeaderIcon, PlaceholderIcon } from "@/components/homepage/PlaceholderIcon";
import { FieldError } from "@/components/ui/FieldError";
import { Spinner } from "@/components/ui/Spinner";
import type { PlaceholderIconName } from "@/lib/homepage";
import { homepageApi, LIST_CONFIG, type HomepageList, type ListRecord } from "@/lib/homepageAdmin";

type Values = Record<string, string | boolean>;

type Props = {
  list: HomepageList;
  /** The item being edited, or null to add one. */
  record: ListRecord | null;
  onCancel: () => void;
  /** Everything saved; the editor closes. */
  onSaved: (saved: ListRecord, created: boolean) => void;
  /** Saved, but something after it (the image) didn't: the list updates, the editor stays open. */
  onRecordChanged: (saved: ListRecord) => void;
};

function valuesOf(list: HomepageList, record: ListRecord | null): Values {
  const config = LIST_CONFIG[list];
  if (!record) return { ...config.blank };
  const source = record as unknown as Record<string, string | boolean>;
  return Object.fromEntries(config.fields.map((f) => [f.name, source[f.name]]));
}

export function ItemEditor({ list, record, onCancel, onSaved, onRecordChanged }: Props) {
  const config = LIST_CONFIG[list];
  const formId = useId();
  const controls = useAnimationControls();
  const alertRef = useRef<HTMLDivElement>(null);
  const [persisted, setPersisted] = useState<ListRecord | null>(record);
  const [values, setValues] = useState<Values>(() => valuesOf(list, record));
  const original = valuesOf(list, persisted);
  const [stagedImage, setStagedImage] = useState<File | null>(null);
  const [imageProgress, setImageProgress] = useState<number | null>(null);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [failTick, setFailTick] = useState(0);
  const creating = persisted === null;

  useEffect(() => {
    if (failTick && formError) alertRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [failTick, formError]);

  function setField(name: string, value: string | boolean) {
    setValues((v) => ({ ...v, [name]: value }));
    if (errors[name]) {
      setErrors((current) => {
        const next = { ...current };
        delete next[name];
        return next;
      });
    }
    setNotice(null);
  }

  function fail(message: string, fieldErrors: Record<string, string> = {}) {
    setErrors(fieldErrors);
    setFormError(message);
    controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
    const first = Object.keys(fieldErrors)[0];
    if (first) document.getElementById(`${formId}-${first}`)?.focus();
    else setFailTick((t) => t + 1);
  }

  async function save(event: React.FormEvent) {
    event.preventDefault();
    setFormError(null);
    const found: Record<string, string> = {};
    for (const field of config.fields) {
      const value = values[field.name];
      if (typeof value === "string" && !value.trim()) found[field.name] = `${field.label} is required.`;
    }
    if (Object.keys(found).length) return fail("Fix the highlighted fields, then save again.", found);

    const trimmed = (v: string | boolean) => (typeof v === "string" ? v.trim() : v);
    const payload = Object.fromEntries(
      config.fields
        .filter((f) => creating || trimmed(values[f.name]) !== trimmed(original[f.name]))
        .map((f) => [f.name, trimmed(values[f.name])]),
    );
    if (!creating && Object.keys(payload).length === 0 && !stagedImage) {
      setNotice("Nothing has changed yet.");
      return;
    }

    setBusy(true);
    let saved = persisted;
    if (creating || Object.keys(payload).length > 0) {
      const result = persisted ? await homepageApi.update(list, persisted.id, payload) : await homepageApi.create(list, payload);
      if (!result.ok) {
        setBusy(false);
        return fail(result.message);
      }
      saved = result.data;
    }

    if (stagedImage && saved) {
      setImageProgress(0);
      const upload = await homepageApi.uploadImage(list, saved.id, stagedImage, setImageProgress);
      setImageProgress(null);
      if (!upload.ok) {
        setBusy(false);
        onRecordChanged(saved);
        setPersisted(saved);
        return fail(
          `${creating || Object.keys(payload).length > 0 ? `The ${config.noun.one} was saved, but the` : "The"} image didn't upload: ${upload.message} Save again to retry the image.`,
        );
      }
      saved = upload.data;
    }

    setBusy(false);
    if (saved) onSaved(saved, creating);
  }

  async function removeImage() {
    if (!persisted) return;
    setBusy(true);
    setFormError(null);
    const result = await homepageApi.removeImage(list, persisted.id);
    setBusy(false);
    if (!result.ok) return fail(result.message);
    setPersisted(result.data);
    onRecordChanged(result.data);
    setNotice(`Image removed. The ${config.noun.one} shows its placeholder again.`);
  }

  const icon = (values.placeholder_icon as PlaceholderIconName | undefined) ?? "document";
  const placeholder = (
    <span className={`homepage-thumb-placeholder ${list === "moments" && values.is_anchor ? "is-anchor" : ""}`} aria-hidden="true">
      {config.hasPlaceholderIcon ? <PlaceholderIcon name={icon} /> : <LeaderIcon />}
    </span>
  );

  return (
    <motion.div animate={controls} className="form-card overflow-hidden">
      <div className="form-card-band" />
      <form id={formId} onSubmit={save} noValidate className="p-6 sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="eyebrow-row">
              <span className="eyebrow-dot" /> {creating ? `New ${config.noun.one}` : `Editing ${config.noun.one}`}
            </p>
            <h2 className="font-display text-2xl">{persisted ? config.title(persisted) : `Add a ${config.noun.one}`}</h2>
            {persisted && <AuditLine updatedBy={persisted.updated_by} updatedAt={persisted.updated_at} />}
          </div>
          <button type="button" onClick={onCancel} className="link-btn" disabled={busy}>
            ← Back to the list
          </button>
        </div>

        <AnimatePresence initial={false}>
          {(formError || notice) && (
            <motion.div
              key={formError ?? notice}
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mt-5 overflow-hidden"
            >
              <div ref={alertRef} className={`alert ${formError ? "alert-error" : "alert-notice"}`} role={formError ? "alert" : "status"}>
                <span aria-hidden="true">●</span>
                <span>{formError ?? notice}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <fieldset disabled={busy} className="mt-7 flex flex-col gap-7">
          <section className="form-section">
            <h3 className="section-heading">
              <span className="section-num">1</span> Details
            </h3>
            <div className="grid gap-5 sm:grid-cols-2">
              {config.fields.map((field) => {
                const id = `${formId}-${field.name}`;
                const hintId = field.hint ? `${id}-hint` : undefined;
                const error = errors[field.name];
                if (field.kind === "checkbox") {
                  return (
                    <div key={field.name} className="field sm:col-span-2">
                      <label className="flex cursor-pointer items-center gap-2.5 text-[15px] font-semibold">
                        <input
                          id={id}
                          type="checkbox"
                          className="h-4 w-4 accent-[var(--forest)]"
                          checked={Boolean(values[field.name])}
                          aria-describedby={hintId}
                          onChange={(e) => setField(field.name, e.target.checked)}
                        />
                        {field.label}
                      </label>
                      {field.hint && <p id={hintId} className="field-hint">{field.hint}</p>}
                    </div>
                  );
                }
                if (field.kind === "icon") {
                  return (
                    <div key={field.name} className="field sm:col-span-2">
                      <p id={`${id}-label`} className="field-label">
                        {field.label}
                      </p>
                      <IconPicker id={id} value={icon} onChange={(v) => setField(field.name, v)} describedBy={hintId} />
                      {field.hint && <p id={hintId} className="field-hint">{field.hint}</p>}
                    </div>
                  );
                }
                const common = {
                  id,
                  value: String(values[field.name] ?? ""),
                  "aria-invalid": error ? true : undefined,
                  "aria-describedby": [hintId, `${id}-error`].filter(Boolean).join(" "),
                  "aria-required": true,
                  className: "input",
                } as const;
                return (
                  <div key={field.name} className={`field ${field.kind === "textarea" || config.fields.length === 2 ? "sm:col-span-2" : ""}`}>
                    <label htmlFor={id} className="field-label">
                      {field.label}
                    </label>
                    {field.kind === "textarea" ? (
                      <textarea {...common} rows={2} onChange={(e) => setField(field.name, e.target.value)} />
                    ) : (
                      <input {...common} type="text" onChange={(e) => setField(field.name, e.target.value)} />
                    )}
                    {field.hint && <p id={hintId} className="field-hint">{field.hint}</p>}
                    <FieldError id={`${id}-error`} message={error} />
                  </div>
                );
              })}
            </div>
          </section>

          <section className="form-section">
            <h3 className="section-heading">
              <span className="section-num">2</span> {list === "leaders" ? "Portrait" : "Image"}
            </h3>
            <ImageField
              noun={config.noun.one}
              currentUrl={persisted?.image_url ?? null}
              staged={stagedImage}
              onStage={(file) => {
                setStagedImage(file);
                setNotice(null);
              }}
              progress={imageProgress}
              disabled={busy}
              onRemove={removeImage}
              empty={placeholder}
            />
          </section>
        </fieldset>

        <div className="mt-8 flex flex-wrap items-center justify-end gap-3 border-t border-line pt-6">
          <button type="button" onClick={onCancel} className="btn-secondary btn-flex" disabled={busy}>
            Cancel
          </button>
          <motion.button
            type="submit"
            className="btn-primary btn-flex min-w-[180px] justify-center"
            disabled={busy}
            whileHover={busy ? undefined : { y: -1 }}
            whileTap={busy ? undefined : { scale: 0.97 }}
          >
            {busy ? (
              <>
                <Spinner size={14} /> {imageProgress !== null ? "Uploading image…" : "Saving…"}
              </>
            ) : creating ? (
              `Add ${config.noun.one}`
            ) : (
              "Save changes"
            )}
          </motion.button>
        </div>
      </form>
    </motion.div>
  );
}
