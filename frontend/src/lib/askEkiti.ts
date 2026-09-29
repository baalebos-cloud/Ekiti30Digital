/**
 * Ask Ekiti: the shapes the widget works with. The browser calls
 * /api/ask-ekiti (src/app/api/ask-ekiti/route.ts), which forwards to the
 * backend's POST /api/ask-ekiti and reshapes its reply into these.
 */

/** The backend's own limits on a question (backend/app/api/routes/ask_ekiti.py). */
export const MIN_QUESTION_LENGTH = 3;
export const MAX_QUESTION_LENGTH = 1000;

export type AskEkitiSource = {
  id: string | null;
  title: string;
  /** Only http(s) links; null when the source has none. */
  url: string | null;
};

export type AskEkitiCitation = {
  docId: string;
  category: string | null;
  /** Source tier from the knowledge base, e.g. "A". */
  tier: string | null;
  /** YYYY-MM-DD. */
  lastVerified: string | null;
  sources: AskEkitiSource[];
};

export type AskEkitiResponse = {
  answer: string;
  /** "insufficient": nothing verified matched, and the answer says so. */
  status: "answered" | "insufficient";
  citations: AskEkitiCitation[];
};

export type AskEkitiError = "invalid_question" | "unavailable" | "unreachable" | "network";

export type AskEkitiResult = { ok: true; data: AskEkitiResponse } | { ok: false; error: AskEkitiError };

export async function askEkiti(question: string): Promise<AskEkitiResult> {
  try {
    const response = await fetch("/api/ask-ekiti", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const data: unknown = await response.json().catch(() => null);
    if (response.ok && data && typeof data === "object" && "answer" in data) {
      return { ok: true, data: data as AskEkitiResponse };
    }
    const error = (data as { error?: unknown } | null)?.error;
    return {
      ok: false,
      error: error === "invalid_question" || error === "unreachable" ? error : "unavailable",
    };
  } catch {
    return { ok: false, error: "network" };
  }
}

/** A friendly line for the chat — never a raw error. */
export function askErrorMessage(error: AskEkitiError): string {
  switch (error) {
    case "invalid_question":
      return `That question couldn't be sent. Try asking in a few words (up to ${MAX_QUESTION_LENGTH} characters).`;
    case "network":
      return "I couldn't reach the server — check your connection and try again.";
    default:
      return "I can't answer right now — the answer service isn't responding. Please try again in a moment.";
  }
}
