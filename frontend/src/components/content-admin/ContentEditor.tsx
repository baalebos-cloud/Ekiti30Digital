"use client";

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { useEffect, useId, useRef, useState } from "react";

import { AuditLine } from "@/components/content-admin/AuditLine";
import { FieldError } from "@/components/ui/FieldError";
import { Spinner } from "@/components/ui/Spinner";
import {
  contentApi,
  FIELD_GROUPS,
  NOUN,
  recordKey,
  recordTitle,
  type ContentAdminKind,
  type ContentRecord,
  type FieldDef,
} from "@/lib/contentAdmin";

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.06 } } };
const rise = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } },
} as const;

type Props = {
  kind: ContentAdminKind;
  /** The record being edited, or null to create a new one. */
  record: ContentRecord | null;
  onCancel: () => void;
  /** Called with the saved record (its key may have changed on an LGA rename). */
  onSaved: (saved: ContentRecord, previousKey: string | null) => void;
};

function initialValues(kind: ContentAdminKind, record: ContentRecord | null): Record<string, string> {
  const values: Record<string, string> = {};
  for (const group of FIELD_GROUPS[kind]) {
    for (const field of group.fields) {
      const value = record?.[field.name];
      values[field.name] = value === null || value === undefined ? "" : String(value);
    }
  }
  if (!record && kind === "lgas") values.verification_status = "Pending";
  return values;
}

export function ContentEditor({ kind, record, onCancel, onSaved }: Props) {
  const formId = useId();
  const controls = useAnimationControls();
  const alertRef = useRef<HTMLDivElement>(null);
  const original = initialValues(kind, record);
  const [values, setValues] = useState(original);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  // Bumped on every failure so the banner is brought into view each time,
  // even when the message is the same as last time.
  const [failTick, setFailTick] = useState(0);

  useEffect(() => {
    // Save sits at the bottom of a long form; bring the message to the admin.
    if (failTick && formError) alertRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }, [failTick, formError]);
  const creating = record === null;
  const fields = FIELD_GROUPS[kind].flatMap((g) => g.fields);

  function setField(name: string, value: string) {
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

  function fail(message: string | null, fieldErrors: Record<string, string> = {}) {
    setErrors(fieldErrors);
    setFormError(message);
    controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
    const first = Object.keys(fieldErrors)[0];
    // A field error: focusing the field scrolls to it. Otherwise the effect
    // above scrolls to the banner.
    if (first) document.getElementById(`${formId}-${first}`)?.focus();
    else setFailTick((t) => t + 1);
  }

  /** Client-side checks the backend would also make, for faster feedback. */
  function validate(): Record<string, string> {
    const found: Record<string, string> = {};
    for (const field of fields) {
      if (!creating && field.createOnly) continue;
      const value = values[field.name].trim();
      if (field.required && !value) found[field.name] = `${field.label} is required.`;
      else if (field.kind === "number" && value && !Number.isFinite(Number(value))) {
        found[field.name] = `${field.label} must be a number.`;
      }
    }
    return found;
  }

  function toPayloadValue(field: FieldDef, raw: string): string | number | null {
    const value = raw.trim();
    if (!value) return null;
    return field.kind === "number" ? Number(value) : value;
  }

  async function save(event: React.FormEvent) {
    event.preventDefault();
    setFormError(null);
    const found = validate();
    if (Object.keys(found).length) return fail("Fix the highlighted fields, then save again.", found);

    let payload: Record<string, unknown> = {};
    if (creating) {
      for (const field of fields) {
        const value = toPayloadValue(field, values[field.name]);
        if (value !== null) payload[field.name] = value;
      }
    } else {
      // Only what changed, so an edit never overwrites fields it didn't touch.
      payload = Object.fromEntries(
        fields
          .filter((f) => !f.createOnly && values[f.name].trim() !== original[f.name].trim())
          .map((f) => [f.name, toPayloadValue(f, values[f.name])]),
      );
      if (Object.keys(payload).length === 0) {
        setNotice("Nothing has changed yet.");
        return;
      }
    }

    setBusy(true);
    const result = creating
      ? await contentApi.create(kind, payload)
      : await contentApi.update(kind, recordKey(kind, record), payload);
    setBusy(false);
    if (!result.ok) return fail(result.message);
    onSaved(result.data, creating ? null : recordKey(kind, record));
  }

  return (
    <motion.div animate={controls} className="form-card overflow-hidden">
      <div className="form-card-band" />
      <form id={formId} onSubmit={save} noValidate className="p-6 sm:p-8">
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <p className="eyebrow-row">
              <span className="eyebrow-dot" /> {creating ? `New ${NOUN[kind].one}` : `Editing ${NOUN[kind].one}`}
            </p>
            <h2 className="font-display text-2xl">{creating ? `Add ${kind === "lgas" ? "an LGA" : "a timeline event"}` : recordTitle(kind, record)}</h2>
            {record && <AuditLine updatedBy={record.updated_by} updatedAt={record.updated_at} />}
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

        <motion.div className="mt-7 flex flex-col gap-7" variants={stagger} initial="hidden" animate="show">
          <fieldset disabled={busy} className="contents">
            {FIELD_GROUPS[kind].map((group, index) => (
              <motion.section key={group.title} variants={rise} className="form-section">
                <h3 className="section-heading">
                  <span className="section-num">{index + 1}</span> {group.title}
                </h3>
                <div className="grid gap-5 sm:grid-cols-2">
                  {group.fields.map((field) => (
                    <Field
                      key={field.name}
                      id={`${formId}-${field.name}`}
                      field={field}
                      value={values[field.name]}
                      error={errors[field.name]}
                      readOnly={!creating && Boolean(field.createOnly)}
                      onChange={(value) => setField(field.name, value)}
                    />
                  ))}
                </div>
              </motion.section>
            ))}
          </fieldset>
        </motion.div>

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
                <Spinner size={14} /> Saving…
              </>
            ) : creating ? (
              `Add ${NOUN[kind].one}`
            ) : (
              "Save changes"
            )}
          </motion.button>
        </div>
      </form>
    </motion.div>
  );
}

function Field({
  id,
  field,
  value,
  error,
  readOnly,
  onChange,
}: {
  id: string;
  field: FieldDef;
  value: string;
  error?: string;
  readOnly: boolean;
  onChange: (value: string) => void;
}) {
  if (readOnly) {
    // Not a disabled input: plain text, so it doesn't look editable. The
    // edit request never includes it (see save()).
    return (
      <div className={`field ${field.kind === "textarea" ? "sm:col-span-2" : ""}`}>
        <p className="field-label" id={`${id}-label`}>
          {field.label}
        </p>
        <p aria-labelledby={`${id}-label`} className="py-1 text-[15px] font-semibold">
          {value || "—"}
        </p>
        <p className="field-hint flex items-center gap-1.5">
          <LockIcon />
          {field.lockedHint ?? "Can't be changed here."}
        </p>
      </div>
    );
  }

  const describedBy = [field.hint && `${id}-hint`, `${id}-error`].filter(Boolean).join(" ");
  const common = {
    id,
    value,
    "aria-invalid": error ? true : undefined,
    "aria-describedby": describedBy,
    "aria-required": field.required || undefined,
    className: "input",
  } as const;

  return (
    <div className={`field ${field.kind === "textarea" ? "sm:col-span-2" : ""}`}>
      <div className="field-label-row">
        <label htmlFor={id} className="field-label">
          {field.label}
        </label>
        {!field.required && <span className="field-optional">Optional</span>}
      </div>
      {field.kind === "textarea" ? (
        <textarea {...common} rows={3} onChange={(e) => onChange(e.target.value)} />
      ) : field.kind === "select" ? (
        <div className="select-wrap">
          <select {...common} onChange={(e) => onChange(e.target.value)}>
            <option value="" disabled>
              Choose…
            </option>
            {field.options?.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
          <Chevron />
        </div>
      ) : (
        <>
          <input
            {...common}
            type="text"
            inputMode={field.kind === "number" ? "decimal" : undefined}
            list={field.suggestions ? `${id}-suggestions` : undefined}
            onChange={(e) => onChange(e.target.value)}
          />
          {field.suggestions && (
            <datalist id={`${id}-suggestions`}>
              {field.suggestions.map((s) => (
                <option key={s} value={s} />
              ))}
            </datalist>
          )}
        </>
      )}
      {field.hint && (
        <p id={`${id}-hint`} className="field-hint">
          {field.hint}
        </p>
      )}
      <FieldError id={`${id}-error`} message={error} />
    </div>
  );
}

function LockIcon() {
  return (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <rect x="5" y="11" width="14" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}

function Chevron() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M6 9l6 6 6-6" />
    </svg>
  );
}
