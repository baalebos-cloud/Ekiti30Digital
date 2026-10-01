"use client";

/**
 * The hero's text: eyebrow, headline, subtitle, the two buttons and the facts
 * row. One record (PATCH /api/admin/homepage/hero); only changed fields are
 * sent. Before the hero exists (not seeded yet) the first save sends them all.
 */

import { AnimatePresence, motion, useAnimationControls } from "motion/react";
import { Fragment, useCallback, useEffect, useId, useState } from "react";

import { AuditLine } from "@/components/content-admin/AuditLine";
import { ErrorState, LoadingState } from "@/components/review/SectionStates";
import { FieldError } from "@/components/ui/FieldError";
import { Spinner } from "@/components/ui/Spinner";
import { MAX_HERO_FACTS, parseHeadline } from "@/lib/homepage";
import { headlineProblem, homepageApi, hrefProblem, type HeroRecord, type HeroValues } from "@/lib/homepageAdmin";

type LoadState =
  | { status: "loading" }
  | { status: "error"; message: string; signInAgain: boolean }
  | { status: "ready"; hero: HeroRecord | null };

const BLANK: HeroValues = {
  eyebrow: "",
  headline: "",
  subtitle: "",
  primary_cta_label: "",
  primary_cta_href: "",
  secondary_cta_label: "",
  secondary_cta_href: "",
  facts: [{ label: "", value: "" }],
};

const TEXT_FIELDS: { name: Exclude<keyof HeroValues, "facts">; label: string; hint?: string; multiline?: boolean }[] = [
  { name: "eyebrow", label: "Eyebrow", hint: "The small line above the headline." },
  { name: "headline", label: "Headline", hint: "Start a new line for a line break. Put *stars* around a word to emphasise it.", multiline: true },
  { name: "subtitle", label: "Subtitle", multiline: true },
];

const CTA_FIELDS = [
  { prefix: "primary", title: "Main button" },
  { prefix: "secondary", title: "Second button" },
] as const;

function valuesOf(hero: HeroRecord | null): HeroValues {
  const source = hero ?? BLANK;
  return {
    eyebrow: source.eyebrow,
    headline: source.headline,
    subtitle: source.subtitle,
    primary_cta_label: source.primary_cta_label,
    primary_cta_href: source.primary_cta_href,
    secondary_cta_label: source.secondary_cta_label,
    secondary_cta_href: source.secondary_cta_href,
    facts: source.facts.map((f) => ({ ...f })),
  };
}

/** Trimmed, as the backend stores it (the headline line by line). */
function tidy(values: HeroValues): HeroValues {
  return {
    eyebrow: values.eyebrow.trim(),
    headline: values.headline.split("\n").map((line) => line.trim()).join("\n").trim(),
    subtitle: values.subtitle.trim(),
    primary_cta_label: values.primary_cta_label.trim(),
    primary_cta_href: values.primary_cta_href.trim(),
    secondary_cta_label: values.secondary_cta_label.trim(),
    secondary_cta_href: values.secondary_cta_href.trim(),
    facts: values.facts.map((f) => ({ label: f.label.trim(), value: f.value.trim() })),
  };
}

export function HeroEditor({ onToast }: { onToast: (message: string) => void }) {
  const [state, setState] = useState<LoadState>({ status: "loading" });

  const load = useCallback(async (): Promise<LoadState> => {
    const result = await homepageApi.getHero();
    if (result.ok) return { status: "ready", hero: result.data };
    if (result.status === 404) return { status: "ready", hero: null };
    return { status: "error", message: result.message, signInAgain: result.status === 401 };
  }, []);

  useEffect(() => {
    let cancelled = false;
    load().then((next) => {
      if (!cancelled) setState(next);
    });
    return () => {
      cancelled = true;
    };
  }, [load]);

  if (state.status === "loading") return <LoadingState variant="rows" />;
  if (state.status === "error") {
    return (
      <ErrorState
        message={state.message}
        signInAgain={state.signInAgain}
        onRetry={async () => {
          setState({ status: "loading" });
          setState(await load());
        }}
      />
    );
  }
  return <HeroForm key={state.hero?.updated_at ?? "new"} hero={state.hero} onSaved={(hero) => setState({ status: "ready", hero })} onToast={onToast} />;
}

function HeroForm({ hero, onSaved, onToast }: { hero: HeroRecord | null; onSaved: (hero: HeroRecord) => void; onToast: (message: string) => void }) {
  const formId = useId();
  const controls = useAnimationControls();
  const original = valuesOf(hero);
  const [values, setValues] = useState<HeroValues>(() => valuesOf(hero));
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const creating = hero === null;

  function set<K extends keyof HeroValues>(name: K, value: HeroValues[K]) {
    setValues((v) => ({ ...v, [name]: value }));
    setErrors({});
    setNotice(null);
  }

  function setFact(index: number, part: "label" | "value", value: string) {
    set(
      "facts",
      values.facts.map((f, i) => (i === index ? { ...f, [part]: value } : f)),
    );
  }

  function validate(): Record<string, string> {
    const found: Record<string, string> = {};
    for (const field of [...TEXT_FIELDS.map((f) => f.name), "primary_cta_label", "secondary_cta_label"] as const) {
      if (!values[field].trim()) found[field] = "This is required.";
    }
    const headline = headlineProblem(values.headline);
    if (headline) found.headline = headline;
    for (const field of ["primary_cta_href", "secondary_cta_href"] as const) {
      const problem = hrefProblem(values[field]);
      if (problem) found[field] = problem;
    }
    values.facts.forEach((f, i) => {
      if (!f.label.trim() || !f.value.trim()) found[`fact-${i}`] = "Each fact needs a label and a value.";
    });
    if (values.facts.length === 0) found.facts = "Keep at least one fact.";
    return found;
  }

  async function save(event: React.FormEvent) {
    event.preventDefault();
    setFormError(null);
    const found = validate();
    if (Object.keys(found).length) {
      setErrors(found);
      setFormError("Fix the highlighted fields, then save again.");
      controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
      return;
    }

    const trimmed = tidy(values);
    const changes = creating
      ? trimmed
      : Object.fromEntries(
          (Object.keys(trimmed) as (keyof HeroValues)[])
            .filter((k) => JSON.stringify(trimmed[k]) !== JSON.stringify(original[k]))
            .map((k) => [k, trimmed[k]]),
        );
    if (Object.keys(changes).length === 0) {
      setNotice("Nothing has changed yet.");
      return;
    }

    setBusy(true);
    const result = await homepageApi.updateHero(changes);
    setBusy(false);
    if (!result.ok) {
      setFormError(result.message);
      controls.start({ x: [0, -8, 7, -5, 3, 0], transition: { duration: 0.4 } });
      return;
    }
    onToast(creating ? "Hero set up" : "Saved · Hero text");
    onSaved(result.data);
  }

  function undo() {
    setValues(valuesOf(hero));
    setErrors({});
    setFormError(null);
    setNotice(null);
  }

  const fieldProps = (name: string) => ({
    id: `${formId}-${name}`,
    "aria-invalid": errors[name] ? true : undefined,
    "aria-describedby": `${formId}-${name}-error`,
    className: "input",
  });

  return (
    <motion.div animate={controls} className="form-card overflow-hidden">
      <div className="form-card-band" />
      <form onSubmit={save} noValidate className="p-6 sm:p-8">
        <div>
          <p className="eyebrow-row">
            <span className="eyebrow-dot" /> Homepage hero
          </p>
          <h2 className="font-display text-2xl">{creating ? "Set up the hero" : "The hero's text"}</h2>
          {hero ? (
            <AuditLine updatedBy={hero.updated_by} updatedAt={hero.updated_at} />
          ) : (
            <p className="text-xs text-ink-soft">The hero hasn&apos;t been set up yet, so every field is needed.</p>
          )}
        </div>

        <AnimatePresence initial={false}>
          {(formError || notice) && (
            <motion.div key={formError ?? notice} initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }} className="mt-5 overflow-hidden">
              <div className={`alert ${formError ? "alert-error" : "alert-notice"}`} role={formError ? "alert" : "status"}>
                <span aria-hidden="true">●</span>
                <span>{formError ?? notice}</span>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <fieldset disabled={busy} className="mt-7 flex flex-col gap-7">
          <section className="form-section">
            <h3 className="section-heading">
              <span className="section-num">1</span> Words
            </h3>
            <div className="grid gap-5">
              {TEXT_FIELDS.map((field) => (
                <div className="field" key={field.name}>
                  <label htmlFor={`${formId}-${field.name}`} className="field-label">
                    {field.label}
                  </label>
                  {field.multiline ? (
                    <textarea {...fieldProps(field.name)} rows={field.name === "headline" ? 2 : 3} value={values[field.name]} onChange={(e) => set(field.name, e.target.value)} />
                  ) : (
                    <input {...fieldProps(field.name)} type="text" value={values[field.name]} onChange={(e) => set(field.name, e.target.value)} />
                  )}
                  {field.hint && <p className="field-hint">{field.hint}</p>}
                  {field.name === "headline" && !headlineProblem(values.headline) && (
                    <div className="hero-preview" aria-label="Headline preview">
                      <span className="text-[11px] font-semibold uppercase tracking-wider text-ink-soft">Preview</span>
                      <p className="hero-preview-title">
                        {parseHeadline(values.headline).map((parts, i) => (
                          <Fragment key={i}>
                            {i > 0 && <br />}
                            {parts.map((part, j) => (part.emphasis ? <em key={j}>{part.text}</em> : <Fragment key={j}>{part.text}</Fragment>))}
                          </Fragment>
                        ))}
                      </p>
                    </div>
                  )}
                  <FieldError id={`${formId}-${field.name}-error`} message={errors[field.name]} />
                </div>
              ))}
            </div>
          </section>

          <section className="form-section">
            <h3 className="section-heading">
              <span className="section-num">2</span> Buttons
            </h3>
            <div className="grid gap-5 sm:grid-cols-2">
              {CTA_FIELDS.map(({ prefix, title }) => (
                <div key={prefix} className="flex flex-col gap-3">
                  <p className="text-sm font-semibold">{title}</p>
                  {(["label", "href"] as const).map((part) => {
                    const name = `${prefix}_cta_${part}` as const;
                    return (
                      <div className="field" key={name}>
                        <label htmlFor={`${formId}-${name}`} className="field-label">
                          {part === "label" ? "Text" : "Link"}
                        </label>
                        <input {...fieldProps(name)} type="text" value={values[name]} onChange={(e) => set(name, e.target.value)} />
                        {part === "href" && <p className="field-hint">A page (/my-ekiti-story), a section (#moments) or an https:// link.</p>}
                        <FieldError id={`${formId}-${name}-error`} message={errors[name]} />
                      </div>
                    );
                  })}
                </div>
              ))}
            </div>
          </section>

          <section className="form-section">
            <h3 className="section-heading">
              <span className="section-num">3</span> Facts
            </h3>
            <p className="-mt-2 mb-4 text-sm text-ink-soft">The row of figures under the buttons. Up to {MAX_HERO_FACTS}.</p>
            <ol className="flex flex-col gap-3">
                {values.facts.map((fact, i) => (
                  <li key={i}>
                    <div className="flex flex-wrap items-end gap-3">
                      <div className="field min-w-[160px] flex-1">
                        <label htmlFor={`${formId}-fact-${i}-label`} className="field-label">
                          Label
                        </label>
                        <input id={`${formId}-fact-${i}-label`} className="input" aria-invalid={errors[`fact-${i}`] ? true : undefined} value={fact.label} onChange={(e) => setFact(i, "label", e.target.value)} />
                      </div>
                      <div className="field min-w-[120px] flex-1">
                        <label htmlFor={`${formId}-fact-${i}-value`} className="field-label">
                          Value
                        </label>
                        <input id={`${formId}-fact-${i}-value`} className="input" aria-invalid={errors[`fact-${i}`] ? true : undefined} value={fact.value} onChange={(e) => setFact(i, "value", e.target.value)} />
                      </div>
                      <button
                        type="button"
                        className="link-btn is-danger mb-2.5"
                        disabled={values.facts.length === 1}
                        onClick={() => set("facts", values.facts.filter((_, j) => j !== i))}
                        aria-label={`Remove fact ${fact.label || i + 1}`}
                      >
                        Remove
                      </button>
                    </div>
                    <FieldError id={`${formId}-fact-${i}-error`} message={errors[`fact-${i}`]} />
                  </li>
                ))}
            </ol>
            {values.facts.length < MAX_HERO_FACTS && (
              <button type="button" className="link-btn mt-3" onClick={() => set("facts", [...values.facts, { label: "", value: "" }])}>
                + Add a fact
              </button>
            )}
          </section>
        </fieldset>

        <div className="mt-8 flex flex-wrap items-center justify-end gap-3 border-t border-line pt-6">
          {!creating && (
            <button type="button" className="btn-secondary btn-flex" disabled={busy} onClick={undo}>
              Undo changes
            </button>
          )}
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
              "Set up the hero"
            ) : (
              "Save changes"
            )}
          </motion.button>
        </div>
      </form>
    </motion.div>
  );
}
