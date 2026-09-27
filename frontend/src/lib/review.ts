/**
 * Shared types and helpers for the admin review desk (/admin): pending media
 * uploads and pending contributor signups.
 */

export const REVIEW_KINDS = ["assets", "contributors"] as const;
export type ReviewKind = (typeof REVIEW_KINDS)[number];

export function isReviewKind(value: string): value is ReviewKind {
  return (REVIEW_KINDS as readonly string[]).includes(value);
}

/** Mirrors backend ContributorOut. */
export type PendingContributor = {
  id: number;
  name: string;
  email: string;
  status: string;
  created_at: string;
};

/** Backend timestamps are naive UTC ("2026-09-26T13:16:20.136"); read them as UTC. */
export function parseBackendDate(value: string): Date {
  return new Date(/[zZ]|[+-]\d\d:\d\d$/.test(value) ? value : `${value}Z`);
}

export function formatDate(value: string): string {
  return parseBackendDate(value).toLocaleString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/** Human message for a failed review request, by status. */
export function reviewErrorMessage(status: number | null, detail?: unknown): string {
  if (status === null) return "Couldn't reach the server. Check your connection and try again.";
  if (status === 401) return "Your session has expired. Sign in again to keep reviewing.";
  if (status === 403) return "Your account isn't allowed to review submissions.";
  if (status === 404) return "This item no longer exists — it may have been removed.";
  if (status === 409) {
    return typeof detail === "string" ? `${detail} — someone may have reviewed it already.` : "This item was already reviewed.";
  }
  if (status === 422) return "The request wasn't accepted. Check the rejection reason and try again.";
  if (status === 502 || status === 503 || status === 504) {
    return "The review service isn't responding right now. Try again in a moment.";
  }
  return "Something went wrong on the server. Please try again.";
}
