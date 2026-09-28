"use client";

import { ReviewActions } from "@/components/review/ReviewActions";
import { formatDate, parseBackendDate, type PendingContributor } from "@/lib/review";

type Props = {
  contributor: PendingContributor;
  onReview: (action: "approve" | "reject", reason?: string) => Promise<string | null>;
};

// First letter of the first and last words, ignoring parenthesised words
// such as "(test)" and punctuation.
function initials(name: string): string {
  const letters = name
    .trim()
    .split(/\s+/)
    .filter((word) => !word.startsWith("("))
    .map((word) => word.match(/\p{L}/u)?.[0])
    .filter((letter): letter is string => Boolean(letter));
  return ((letters[0] ?? "") + (letters.length > 1 ? letters.at(-1)! : "")).toUpperCase() || "?";
}

const relative = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

function timeAgo(value: string): string {
  const minutes = Math.round((parseBackendDate(value).getTime() - Date.now()) / 60_000);
  if (Math.abs(minutes) < 60) return relative.format(minutes, "minute");
  const hours = Math.round(minutes / 60);
  if (Math.abs(hours) < 24) return relative.format(hours, "hour");
  return relative.format(Math.round(hours / 24), "day");
}

/** One pending signup: who they are, when they signed up, and the review controls. */
export function ContributorReviewRow({ contributor, onReview }: Props) {
  return (
    <article className="review-row">
      <div className="review-row-info">
        <span className="review-avatar" aria-hidden="true">{initials(contributor.name)}</span>
        <div className="min-w-0">
          <p className="truncate font-display text-lg font-medium">{contributor.name}</p>
          <p className="truncate text-sm text-ink-soft">
            <a href={`mailto:${contributor.email}`} className="hover:text-forest hover:underline">
              {contributor.email}
            </a>
          </p>
          <p className="mt-0.5 text-xs text-ink-soft">
            Signed up {formatDate(contributor.created_at)}{" "}
            <span className="opacity-70">({timeAgo(contributor.created_at)})</span>
          </p>
        </div>
      </div>
      <div className="review-row-actions">
        <ReviewActions
          noun="signup"
          reasonExamples="e.g. Couldn't confirm who this is, looks like a duplicate account"
          onReview={onReview}
        />
      </div>
    </article>
  );
}
