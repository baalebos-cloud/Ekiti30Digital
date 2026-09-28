"use client";

/**
 * Ask Ekiti: a floating button on every page that opens a chat panel.
 *
 * UI shell only — the Ask Ekiti API (retrieval + answer generation) isn't
 * built yet, so a question gets an honest "not connected yet" reply instead
 * of a network call. When the API exists, replace `replyTo` with a call to a
 * Next.js route that forwards to it.
 *
 * Other components open it by dispatching ASK_EKITI_OPEN_EVENT; /ask-ekiti
 * redirects to /?ask=1, which opens it on load.
 */

import { AnimatePresence, motion } from "motion/react";
import { useEffect, useRef, useState } from "react";

export const ASK_EKITI_OPEN_EVENT = "ask-ekiti:open";

type Message = { id: number; from: "you" | "ekiti"; text: string };

const EXAMPLES = [
  "When was Ekiti State created?",
  "What is Ikogosi known for?",
  "Which LGAs border Ado Ekiti?",
];

function replyTo(): string {
  return "Ask Ekiti isn't connected yet. Soon it will answer questions like this one from the platform's verified sources — and show you where each answer comes from.";
}

export function AskEkitiWidget() {
  const [open, setOpen] = useState(false);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
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
  }, [messages]);

  function send(text: string) {
    const question = text.trim();
    if (!question) return;
    const id = (nextId.current += 2);
    setMessages((m) => [...m, { id, from: "you", text: question }, { id: id + 1, from: "ekiti", text: replyTo() }]);
    setDraft("");
    input.current?.focus();
  }

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
                <p className="text-xs opacity-80">Answers from verified sources · coming soon</p>
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

            <div ref={log} className="ask-log" aria-live="polite">
              <div className="ask-bubble is-ekiti">
                Ẹ káàbọ̀! Ask anything about Ekiti — its history, towns, people and places.
              </div>
              {messages.length === 0 && (
                <div className="ask-examples">
                  <span>Try asking</span>
                  {EXAMPLES.map((q) => (
                    <button key={q} type="button" onClick={() => send(q)}>
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
                    transition={{ duration: 0.25, delay: m.from === "ekiti" ? 0.35 : 0 }}
                    className={`ask-bubble ${m.from === "you" ? "is-you" : "is-ekiti"}`}
                  >
                    {m.text}
                  </motion.div>
                ))}
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
              />
              <motion.button
                type="submit"
                className="ask-send"
                aria-label="Send question"
                disabled={!draft.trim()}
                whileTap={{ scale: 0.92 }}
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
        className="ask-fab"
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
