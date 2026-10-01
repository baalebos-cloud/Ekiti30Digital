/**
 * The homepage's content: the hero, leaders, landmarks and moments.
 *
 * Admins edit it in the review desk (Manage content -> Homepage); the
 * homepage sections fetch it from /api/homepage (src/app/api/homepage/route.ts),
 * which proxies the backend's GET /api/homepage. Section headings and
 * descriptions aren't content: they stay in the components.
 */

export const PLACEHOLDER_ICONS = [
  "document",
  "person",
  "springs",
  "waterfall",
  "hill",
  "star",
  "house",
  "book",
  "pin",
  "celebration",
] as const;
export type PlaceholderIconName = (typeof PLACEHOLDER_ICONS)[number];

export const ICON_LABELS: Record<PlaceholderIconName, string> = {
  document: "Document",
  person: "Person",
  springs: "Springs",
  waterfall: "Waterfall",
  hill: "Hill",
  star: "Star",
  house: "House",
  book: "Book",
  pin: "Map pin",
  celebration: "Celebration",
};

/** Next's cache tag for the proxied GET /api/homepage; admin writes revalidate it. */
export const HOMEPAGE_CACHE_TAG = "homepage";

export const MAX_HERO_IMAGES = 3;
export const MAX_HERO_FACTS = 6;

export type HeroImage = { id: number; caption: string; imageUrl: string | null; placeholderIcon: PlaceholderIconName };
export type Hero = {
  eyebrow: string;
  headline: string;
  subtitle: string;
  primaryCta: { label: string; href: string };
  secondaryCta: { label: string; href: string };
  facts: { label: string; value: string }[];
  images: HeroImage[];
};
export type Leader = { id: number; name: string; term: string; imageUrl: string | null };
export type Landmark = { id: number; name: string; description: string; imageUrl: string | null; placeholderIcon: PlaceholderIconName };
export type Moment = {
  id: number;
  year: string;
  label: string;
  isAnchor: boolean;
  imageUrl: string | null;
  placeholderIcon: PlaceholderIconName;
};

/** GET /api/homepage. `hero` is null until an admin (or the seed) sets it up. */
export type HomepageContent = {
  hero: Hero | null;
  leaders: Leader[];
  landmarks: Landmark[];
  moments: Moment[];
};

export type HeadlinePart = { text: string; emphasis: boolean };

/**
 * The headline's minimal markup, as lines of plain and *emphasised* text.
 * Never HTML: the parts are rendered as React text, so markup can't inject
 * anything. "Welcome home.\nThirty years of *us*." ->
 * [[Welcome home.], [Thirty years of , us(em), .]]
 */
export function parseHeadline(headline: string): HeadlinePart[][] {
  return headline.split("\n").map((line) =>
    line
      .split("*")
      .map((text, i) => ({ text, emphasis: i % 2 === 1 }))
      .filter((part) => part.text !== ""),
  );
}

/** Cards cycle through the four landmark colours by position (l1..l4). */
export function landmarkTone(index: number): string {
  return `l${(index % 4) + 1}`;
}
