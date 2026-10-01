/**
 * Ask Ekiti: proxies a question to the backend's public POST /api/ask-ekiti
 * and returns an AskEkitiResponse (src/lib/askEkiti.ts).
 *
 * The selected language is forwarded; the backend enforces language review.
 * Citations are re-checked before they reach the page: only http(s) links
 * survive, since knowledge-base text ends up as clickable links.
 *
 * Failures come back as { error } with a status the widget can explain:
 * 400 for a question the backend won't accept, 503 when the answer service
 * is unavailable (the backend's own 503, e.g. retrieval down), 502 for an
 * unexpected backend reply, 504 when the backend can't be reached. The
 * backend's detail text is logged here, never shown in the chat.
 */

import {
  MAX_QUESTION_LENGTH,
  MIN_QUESTION_LENGTH,
  type AskEkitiCitation,
  type AskEkitiResponse,
  type AskEkitiSource,
} from "@/lib/askEkiti";
import { API_URL } from "@/lib/config";

// First question after a backend restart loads the embedding model, which
// can take a while; later ones are quick.
const TIMEOUT_MS = 45_000;

function fail(status: number, error: string) {
  return Response.json({ error }, { status });
}

function strings(value: unknown): string[] {
  return Array.isArray(value) ? value.map((v) => (typeof v === "string" ? v.trim() : "")) : [];
}

function safeUrl(value: unknown): string | null {
  if (typeof value !== "string") return null;
  try {
    const url = new URL(value.trim());
    return url.protocol === "https:" || url.protocol === "http:" ? url.href : null;
  } catch {
    return null;
  }
}

/** One backend citation -> the fields the widget shows, links made safe. */
function toCitation(raw: unknown): AskEkitiCitation | null {
  if (typeof raw !== "object" || raw === null) return null;
  const c = raw as Record<string, unknown>;
  const ids = strings(c.source_ids);
  const titles = strings(c.source_titles);
  const urls = strings(c.source_urls);
  const count = Math.max(ids.length, titles.length, urls.length);
  const sources: AskEkitiSource[] = [];
  for (let i = 0; i < count; i++) {
    const title = titles[i] || ids[i];
    if (!title) continue;
    sources.push({ id: ids[i] || null, title, url: safeUrl(urls[i]) });
  }
  if (sources.length === 0) {
    const fallback = safeUrl(c.source_url);
    if (!fallback) return null;
    sources.push({ id: null, title: new URL(fallback).hostname, url: fallback });
  }
  return {
    docId: typeof c.doc_id === "string" ? c.doc_id : "",
    category: typeof c.category === "string" ? c.category : null,
    tier: typeof c.tier === "string" ? c.tier : null,
    lastVerified: typeof c.last_verified === "string" ? c.last_verified : null,
    sources,
  };
}

export async function POST(request: Request) {
  let question: string;
  let language: "en" | "yo" = "en";
  try {
    const body = (await request.json()) as { question?: unknown; language?: unknown };
    if (body.language !== undefined && body.language !== "en" && body.language !== "yo") return fail(400, "invalid_question");
    language = body.language === "yo" ? "yo" : "en";
    question = typeof body.question === "string" ? body.question.trim() : "";
  } catch {
    return fail(400, "invalid_question");
  }
  if (question.length < MIN_QUESTION_LENGTH || question.length > MAX_QUESTION_LENGTH) {
    return fail(400, "invalid_question");
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${API_URL}/api/ask-ekiti`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, category: null, language }),
      cache: "no-store",
      signal: AbortSignal.timeout(TIMEOUT_MS),
    });
  } catch {
    return fail(504, "unreachable");
  }

  const data = (await upstream.json().catch(() => null)) as Record<string, unknown> | null;
  if (!upstream.ok) {
    console.warn(`[ask-ekiti] backend returned ${upstream.status}:`, data?.detail ?? "(no detail)");
    if (upstream.status === 503 && data?.detail === "Yoruba responses await human review") return fail(503, "language_review");
    if (upstream.status === 422) return fail(400, "invalid_question");
    return fail(upstream.status === 503 ? 503 : 502, "unavailable");
  }

  const status = data?.answer_status;
  if (typeof data?.answer !== "string" || (status !== "answered" && status !== "insufficient")) {
    console.warn("[ask-ekiti] unexpected backend reply shape");
    return fail(502, "unavailable");
  }

  const body: AskEkitiResponse = {
    answer: data.answer,
    reason: typeof data.reason === "string" ? data.reason : undefined,
    status,
    citations: Array.isArray(data.citations)
      ? data.citations.map(toCitation).filter((c): c is AskEkitiCitation => c !== null)
      : [],
  };
  return Response.json(body);
}
