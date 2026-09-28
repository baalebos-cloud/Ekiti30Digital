/**
 * Public content feeds: proxies the backend's GET /api/{kind} and returns a
 * ContentResponse (src/lib/content.ts).
 *
 * Expected backend response: { "<list key>": [item, ...] } — e.g.
 * { "events": [...] } for timeline — where each item has at least the
 * REQUIRED_FIELDS for its kind. Items missing them are dropped rather than
 * rendered half-broken, so a stub's placeholder list comes back empty and
 * the page shows its "nothing here yet" state.
 *
 * If the backend can't be reached or errors, this returns 502 and the page
 * shows a retryable error instead of pretending there's no content.
 */

import { API_URL } from "@/lib/config";
import { BACKEND_LIST_KEY, isContentKind, REQUIRED_FIELDS, type ContentKind, type ContentResponse } from "@/lib/content";

function isRenderable(kind: ContentKind, item: unknown): boolean {
  if (typeof item !== "object" || item === null) return false;
  const record = item as Record<string, unknown>;
  return REQUIRED_FIELDS[kind].every((field) => typeof record[field] === "string" && record[field] !== "");
}

export async function GET(_request: Request, ctx: RouteContext<"/api/content/[kind]">) {
  const { kind } = await ctx.params;
  if (!isContentKind(kind)) return Response.json({ detail: "Not found" }, { status: 404 });

  let data: Record<string, unknown>;
  try {
    const response = await fetch(`${API_URL}/api/${kind}`, {
      // Short cache: public, read-only content. (Once a fetch has succeeded,
      // Next keeps serving that cached response if a later refresh fails.)
      next: { revalidate: 60 },
      signal: AbortSignal.timeout(8_000),
    });
    if (!response.ok) throw new Error(`Backend returned ${response.status}`);
    data = (await response.json()) as Record<string, unknown>;
  } catch {
    return Response.json({ detail: "The content service can't be reached" }, { status: 502 });
  }

  const list = data[BACKEND_LIST_KEY[kind]];
  const body: ContentResponse<unknown> = {
    items: Array.isArray(list) ? list.filter((item) => isRenderable(kind, item)) : [],
  };
  return Response.json(body);
}
