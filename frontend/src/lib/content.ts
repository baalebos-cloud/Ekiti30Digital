/**
 * The four public content feeds and the shape their pages expect.
 *
 * Each page fetches /api/content/{kind} (src/app/api/content/[kind]/route.ts),
 * which calls the backend's GET /api/{kind} and returns ContentResponse.
 * The backend endpoints are still stubs that return empty lists, so every
 * page shows its empty state for now. When they start returning items in
 * the shapes below (see src/data/*.ts for the field definitions), the pages
 * show them with no frontend change.
 */

export const CONTENT_KINDS = ["timeline", "lgas", "stories", "vision2056"] as const;
export type ContentKind = (typeof CONTENT_KINDS)[number];

export function isContentKind(value: string): value is ContentKind {
  return (CONTENT_KINDS as readonly string[]).includes(value);
}

/** An empty `items` means the backend has nothing to show yet. */
export type ContentResponse<T> = {
  items: T[];
};

/** Backend list key for each feed, e.g. { "events": [...] } for timeline. */
export const BACKEND_LIST_KEY: Record<ContentKind, string> = {
  timeline: "events",
  lgas: "lgas",
  stories: "stories",
  vision2056: "visions",
};

/** Fields an item must have (as strings) for its page to render it. */
export const REQUIRED_FIELDS: Record<ContentKind, string[]> = {
  timeline: ["id", "date", "title", "description", "category", "status"],
  lgas: ["slug", "name", "headquarters"],
  stories: ["id", "title", "sharedBy", "lga", "text"],
  vision2056: ["id", "headline", "sharedBy", "category", "vision"],
};
