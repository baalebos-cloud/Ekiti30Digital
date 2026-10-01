
"use client";

/**
 * Ask Ekiti: a floating button on every page that opens a chat panel.
 *
 * Questions go to /api/ask-ekiti (src/app/api/ask-ekiti/route.ts), which
 * forwards to the backend. Answers are sourced facts from the verified
 * knowledge base, shown with their sources; when nothing verified matches,
 * the backend says so ("insufficient") and that's shown as an honest
 * "not yet", not an error. English only for now: Yoruba answers await human
 * review on the backend.
 *
 * Other components open it by dispatching ASK_EKITI_OPEN_EVENT; /ask-ekiti
 * redirects to /?ask=1, which opens it on load.
 */

import { AnimatePresence, motion, useReducedMotion } from "motion/react";
import { useEffect, useRef, useState } from "react";

import {
  askEkiti,
  askErrorMessage,
  MAX_QUESTION_LENGTH,
  MIN_QUESTION_LENGTH,
  type AskEkitiCitation,
} from "@/lib/askEkiti";

export const ASK_EKITI_OPEN_EVENT = "ask-ekiti:open";

type Message =
  | { id: number; from: "you"; text: string }
  | { id: number; from: "ekiti"; kind: "answered"; text: string; citations: AskEkitiCitation[] }
  | { id: number; from: "ekiti"; kind: "insufficient"; text: string; reason?: string }
  /** `retry` is the question to ask again, or null if asking again won't help. */
  | { id: number; from: "ekiti"; kind: "error"; text: string; retry: string | null };

/** A Message before it has an id (Omit applied to each member of the union). */
type NewMessage = Message extends infer M ? (M extends Message ? Omit<M, "id"> : never) : never;

const EXAMPLES = [
  "When was Ekiti State created?",
  "How many LGAs does Ekiti State have?",
  "What is the headquarters of Ikere LGA?",
];

export function AskEkitiWidget() {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [language, setLanguage] = useState<"en" | "yo">("en");
  const [messages, setMessages] = useState<Message[]>([]);
  const [pending, setPending] = useState(false);
  const fab = useRef<HTMLButtonElement>(null);
  const input = useRef<HTMLTextAreaElement>(null);
  const log = useRef<HTMLDivElement>(null);
  const nextId = useRef(0);

  // Open from elsewhere (nav button) or from /?ask=1.
  useEffect(() => {
    const openPanel = () => setOpen(true);
    window.addEventListener(ASK_EKITI_OPEN_EVENT, openPanel);
    const params = new URLSearchParams(window.location.search);
    if (params.get("ask") === "1") {
      params.delete("ask");
      const rest = params.toString();
      window.history.replaceState(null, "", `${window.location.pathname}${rest ? `?${rest}` : ""}`);
      openPanel();
    }
    return () => window.removeEventListener(ASK_EKITI_OPEN_EVENT, openPanel);
  }, []);

  useEffect(() => {
    if (!open) return;
    input.current?.focus();
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        setOpen(false);
        fab.current?.focus();
      }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open]);

  useEffect(() => {
    log.current?.scrollTo({ top: log.current.scrollHeight, behavior: "smooth" });
  }, [messages, pending]);

  function add(message: NewMessage) {
    setMessages((m) => [...m, { ...message, id: (nextId.current += 1) } as Message]);
  }

  /**
   * Ask the backend. A new question is added as a bubble; a retry instead
   * replaces the error it came from, so failures don't pile up.
   */
  async function ask(question: string, retryOf?: number) {
    if (pending) return;
    if (retryOf === undefined) add({ from: "you", text: question });
    else setMessages((m) => m.filter((msg) => msg.id !== retryOf));
    setPending(true);
    const result = await askEkiti(question, language);
    setPending(false);
    if (!result.ok) {
      add({
        from: "ekiti",
        kind: "error",
        text: askErrorMessage(result.error),
        retry: result.error === "invalid_question" ? null : question,
      });
    } else if (result.data.status === "insufficient") {
      add({ from: "ekiti", kind: "insufficient", text: result.data.answer, reason: result.data.reason });
    } else {
      add({ from: "ekiti", kind: "answered", text: result.data.answer, citations: result.data.citations });
    }
  }

  function send(text: string) {
    const question = text.trim();
    if (question.length < MIN_QUESTION_LENGTH || pending) return;
    setDraft("");
    input.current?.focus();
    ask(question);
  }

  const canSend = draft.trim().length >= MIN_QUESTION_LENGTH && !pending;

  return (
    <>
      <AnimatePresence>
        {open && (
          <motion.div
            key="panel"
            role="dialog"
            aria-labelledby="ask-ekiti-title"
            className="ask-panel"
            initial={{ opacity: 0, scale: 0.9, y: 16 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.94, y: 12 }}
            transition={{ type: "spring", stiffness: 380, damping: 30 }}
          >
            <div className="ask-header">
              <div>
                <p id="ask-ekiti-title" className="font-display text-xl">
                  Ask <em>Ekiti</em>
                </p>
                <p className="text-xs opacity-80">Answers only from verified sources — and says so when it can&apos;t</p>
              </div>
              <button
                type="button"
                className="ask-close"
                aria-label="Close Ask Ekiti"
                onClick={() => {
                  setOpen(false);
                  fab.current?.focus();
                }}
              >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                  <path d="M6 6l12 12M18 6 6 18" />
                </svg>
              </button>
            </div>

            <label className="px-4 py-2 text-sm">
              Language / Èdè
              <select aria-label="Answer language" value={language} disabled={pending}
                onChange={(event) => setLanguage(event.target.value as "en" | "yo")}
                className="ml-2 rounded border px-2 py-1">
                <option value="en">English</option>
                <option value="yo">Yorùbá (subject to language review)</option>
              </select>
            </label>
            <div ref={log} className="ask-log" aria-live="polite">
              <div className="ask-bubble is-ekiti">
                Ẹ káàbọ̀! Ask anything about Ekiti — its history, towns, people and places.
              </div>
              {messages.length === 0 && (
                <div className="ask-examples">
                  <span>Try asking</span>
                  {EXAMPLES.map((q) => (
                    <button key={q} type="button" onClick={() => send(q)} disabled={pending}>
                      {q}
                    </button>
                  ))}
                </div>
              )}
              <AnimatePresence initial={false}>
                {messages.map((m) => (
                  <motion.div
                    key={m.id}
                    initial={{ opacity: 0, y: 8, scale: 0.97 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    transition={{ duration: 0.25 }}
                    className={`ask-bubble ${bubbleClass(m)}`}
                  >
                    {m.from === "ekiti" && m.kind === "insufficient" && (!m.reason || m.reason === "no_verified_match") && <span className="ask-bubble-tag">Not in the verified sources yet</span>}
                    <p className="whitespace-pre-line">{m.text}</p>
                    {m.from === "ekiti" && m.kind === "answered" && m.citations.length > 0 && (
                      <Sources citations={m.citations} />
                    )}
                    {m.from === "ekiti" && m.kind === "error" && m.retry && (
                      <button type="button" className="ask-retry" disabled={pending} onClick={() => ask(m.retry!, m.id)}>
                        Try again
                      </button>
                    )}
                  </motion.div>
                ))}
                {pending && <Thinking key="thinking" />}
              </AnimatePresence>
            </div>

            <form
              className="ask-form"
              onSubmit={(e) => {
                e.preventDefault();
                send(draft);
              }}
            >
              <label htmlFor="ask-input" className="sr-only">Your question</label>
              <textarea
                ref={input}
                id="ask-input"
                rows={1}
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send(draft);
                  }
                }}
                className="input ask-input"
                placeholder="Ask about Ekiti…"
                maxLength={MAX_QUESTION_LENGTH}
              />
              <motion.button
                type="submit"
                className="ask-send"
                aria-label="Send question"
                disabled={!canSend}
                whileTap={canSend ? { scale: 0.92 } : undefined}
              >
                <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M5 12h13M13 6l6 6-6 6" />
                </svg>
              </motion.button>
            </form>
          </motion.div>
        )}
      </AnimatePresence>

      <motion.button
        ref={fab}
        type="button"
        // is-idle: the soft pulse ring (globals.css) only while the panel is closed.
        className={`ask-fab ${open ? "" : "is-idle"}`}
        aria-label={open ? "Close Ask Ekiti" : "Open Ask Ekiti"}
        aria-expanded={open}
        onClick={() => setOpen((o) => !o)}
        whileHover={{ y: -2 }}
        whileTap={{ scale: 0.94 }}
        initial={{ scale: 0, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 320, damping: 20, delay: 0.4 }}
      >
        <AnimatePresence mode="wait" initial={false}>
          <motion.span
            key={open ? "close" : "ask"}
            initial={{ rotate: -90, opacity: 0 }}
            animate={{ rotate: 0, opacity: 1 }}
            exit={{ rotate: 90, opacity: 0 }}
            transition={{ duration: 0.18 }}
            className="flex"
          >
            {open ? (
              <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round">
                <path d="M6 6l12 12M18 6 6 18" />
              </svg>
            ) : (
              <svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round">
                <path d="M4 5h16v11H9l-5 4z" />
                <path d="M10 9.2c0-1.1.9-1.8 2-1.8s2 .7 2 1.7c0 1.3-2 1.3-2 2.6" />
                <circle cx="12" cy="13.6" r="0.4" fill="currentColor" />
              </svg>
            )}
          </motion.span>
        </AnimatePresence>
        {!open && <span className="ask-fab-label">Ask Ekiti</span>}
      </motion.button>
    </>
  );
}

function bubbleClass(m: Message): string {
  if (m.from === "you") return "is-you";
  if (m.kind === "insufficient") return "is-ekiti is-soft";
  if (m.kind === "error") return "is-ekiti is-error";
  return "is-ekiti";
}

/**
 * "Ekiti is thinking…" with three bouncing dots (still, if motion is reduced).
 * No exit animation on purpose: the reply takes its place at once, and its
 * removal never waits on an animation frame.
 */
function Thinking() {
  const still = useReducedMotion();
  return (
    <motion.div
      initial={{ opacity: 0, y: 8, scale: 0.97 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.25 }}
      className="ask-bubble is-ekiti ask-thinking"
      role="status"
    >
      <span className="ask-dots" aria-hidden="true">
        {[0, 1, 2].map((i) => (
          <motion.span
            key={i}
            animate={still ? undefined : { y: [0, -4, 0], opacity: [0.35, 1, 0.35] }}
            transition={still ? undefined : { duration: 1, repeat: Infinity, delay: i * 0.16, ease: "easeInOut" }}
          />
        ))}
      </span>
      <span>Ekiti is thinking…</span>
    </motion.div>
  );
}

function formatVerified(value: string | null): string | null {
  if (!value) return null;
  const date = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" });
}

/** The sources behind an answer: numbered to match each fact, linked where it has a link. */
function Sources({ citations }: { citations: AskEkitiCitation[] }) {
  const sources = citations.flatMap((citation, citationIndex) =>
    citation.sources.map((source) => ({ ...source, citationNumber: citationIndex + 1,
      tier: citation.tier, verified: formatVerified(citation.lastVerified) })),
  );

  return (
    <div className="ask-sources">
      <p className="ask-sources-label">Sources</p>
      <ol>
        {sources.map((source, i) => (
          <motion.li
            key={`${source.url ?? source.title}-${i}`}
            initial={{ opacity: 0, y: 4 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 + i * 0.05, duration: 0.2 }}
          >
            {source.url ? (
              <a href={source.url} target="_blank" rel="noopener noreferrer" className="ask-source">
                <span className="ask-source-num">{source.citationNumber}</span>
                <span className="ask-source-title">{source.title}</span>
                <span aria-hidden="true">↗</span>
              </a>
            ) : (
              <span className="ask-source">
                <span className="ask-source-num">{source.citationNumber}</span>
                <span className="ask-source-title">{source.title}</span>
              </span>
            )}
            {(source.tier || source.verified) && (
              <span className="ask-source-meta">
                {[source.tier && `Tier ${source.tier}`, source.verified && `verified ${source.verified}`].filter(Boolean).join(" · ")}
              </span>
            )}
          </motion.li>
        ))}
      </ol>
    </div>
  );
}
