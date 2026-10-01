/**
 * The homepage's content: proxies the backend's GET /api/homepage and
 * returns a HomepageContent (src/lib/homepage.ts).
 *
 * Items missing a field the homepage needs are dropped rather than rendered
 * half-broken. If the backend can't be reached or errors, this returns 502
 * and the sections show their fallback instead of pretending there's no
 * content.
 */

import { API_URL } from "@/lib/config";
import { HOMEPAGE_CACHE_TAG, PLACEHOLDER_ICONS, type Hero, type HomepageContent } from "@/lib/homepage";

type Item = Record<string, unknown>;

const isText = (v: unknown) => typeof v === "string" && v !== "";
const isIcon = (v: unknown) => (PLACEHOLDER_ICONS as readonly unknown[]).includes(v);
const isImage = (v: unknown) => v === null || isText(v);

function list(value: unknown, isValid: (item: Item) => boolean): Item[] {
  return Array.isArray(value)
    ? value.filter((item): item is Item => typeof item === "object" && item !== null && isValid(item as Item))
    : [];
}

function hero(value: unknown): Hero | null {
  if (typeof value !== "object" || value === null) return null;
  const h = value as Item;
  const cta = (c: unknown) => typeof c === "object" && c !== null && isText((c as Item).label) && isText((c as Item).href);
  if (![h.eyebrow, h.headline, h.subtitle].every(isText) || !cta(h.primaryCta) || !cta(h.secondaryCta)) return null;
  return {
    eyebrow: h.eyebrow,
    headline: h.headline,
    subtitle: h.subtitle,
    primaryCta: h.primaryCta,
    secondaryCta: h.secondaryCta,
    facts: list(h.facts, (f) => isText(f.label) && isText(f.value)),
    images: list(h.images, (i) => isText(i.caption) && isImage(i.imageUrl) && isIcon(i.placeholderIcon)),
  } as Hero;
}

export async function GET() {
  let data: Item;
  try {
    const response = await fetch(`${API_URL}/api/homepage`, {
      // Cached, and dropped the moment an admin saves anything through
      // /api/admin/homepage/* (it revalidates HOMEPAGE_CACHE_TAG), so an edit
      // shows on the next page load. The 60s refresh covers changes made
      // elsewhere (the seed script). Once a fetch has succeeded, Next keeps
      // serving that cached response if a later refresh fails.
      next: { revalidate: 60, tags: [HOMEPAGE_CACHE_TAG] },
      signal: AbortSignal.timeout(8_000),
    });
    if (!response.ok) throw new Error(`Backend returned ${response.status}`);
    data = (await response.json()) as Item;
  } catch {
    return Response.json({ detail: "The content service can't be reached" }, { status: 502 });
  }

  const body: HomepageContent = {
    hero: hero(data.hero),
    leaders: list(data.leaders, (l) => isText(l.name) && isText(l.term) && isImage(l.imageUrl)) as HomepageContent["leaders"],
    landmarks: list(
      data.landmarks,
      (l) => isText(l.name) && isText(l.description) && isImage(l.imageUrl) && isIcon(l.placeholderIcon),
    ) as HomepageContent["landmarks"],
    moments: list(
      data.moments,
      (m) => isText(m.year) && isText(m.label) && typeof m.isAnchor === "boolean" && isImage(m.imageUrl) && isIcon(m.placeholderIcon),
    ) as HomepageContent["moments"],
  };
  return Response.json(body);
}
