/**
 * Admin editing of the homepage content, through the proxy at
 * /api/admin/homepage/* (src/app/api/admin/homepage/[...path]/route.ts).
 *
 * Records are the backend's admin shapes (snake_case, as stored), like the
 * LGA/timeline editor in src/lib/contentAdmin.ts. The public shapes the
 * homepage renders are in src/lib/homepage.ts.
 */

import { adminRequest, json, uploadImage, type Result } from "@/lib/contentAdmin";
import type { PlaceholderIconName } from "@/lib/homepage";

export const HOMEPAGE_LISTS = ["leaders", "landmarks", "moments", "hero/images"] as const;
export type HomepageList = (typeof HOMEPAGE_LISTS)[number];

type Audit = { id: number; created_at: string; updated_at: string; updated_by: string | null };
type Ordered = Audit & { position: number; image_url: string | null };

export type LeaderRecord = Ordered & { name: string; term: string };
export type LandmarkRecord = Ordered & { name: string; description: string; placeholder_icon: PlaceholderIconName };
export type MomentRecord = Ordered & { year: string; label: string; is_anchor: boolean; placeholder_icon: PlaceholderIconName };
export type HeroImageRecord = Ordered & { caption: string; placeholder_icon: PlaceholderIconName };
export type ListRecord = LeaderRecord | LandmarkRecord | MomentRecord | HeroImageRecord;

export type HeroFact = { label: string; value: string };
export type HeroRecord = Audit & {
  eyebrow: string;
  headline: string;
  subtitle: string;
  primary_cta_label: string;
  primary_cta_href: string;
  secondary_cta_label: string;
  secondary_cta_href: string;
  facts: HeroFact[];
};
export type HeroValues = Omit<HeroRecord, keyof Audit>;

export type ItemField = {
  name: string;
  label: string;
  kind: "text" | "textarea" | "icon" | "checkbox";
  hint?: string;
};

export type ListConfig = {
  label: string;
  noun: { one: string; many: string };
  fields: ItemField[];
  /** Leaders always show the person icon when they have no portrait. */
  hasPlaceholderIcon: boolean;
  /** Most items allowed, if capped (the hero board has three slots). */
  max?: number;
  title: (record: ListRecord) => string;
  subtitle: (record: ListRecord) => string;
  /** What a new item starts with. */
  blank: Record<string, string | boolean>;
};

const iconField: ItemField = {
  name: "placeholder_icon",
  label: "Placeholder icon",
  kind: "icon",
  hint: "Shown until an image is uploaded, and again if it's removed.",
};

export const LIST_CONFIG: Record<HomepageList, ListConfig> = {
  leaders: {
    label: "Leaders",
    noun: { one: "leader", many: "leaders" },
    fields: [
      { name: "name", label: "Name", kind: "text" },
      { name: "term", label: "Term", kind: "text", hint: "As it should read, e.g. 2003–2006, 2014–2018 or 2022–present." },
    ],
    hasPlaceholderIcon: false,
    title: (r) => (r as LeaderRecord).name,
    subtitle: (r) => (r as LeaderRecord).term,
    blank: { name: "", term: "" },
  },
  landmarks: {
    label: "Landmarks",
    noun: { one: "landmark", many: "landmarks" },
    fields: [
      { name: "name", label: "Name", kind: "text" },
      { name: "description", label: "Line under the name", kind: "text", hint: "Where it is, and a few words about it." },
      iconField,
    ],
    hasPlaceholderIcon: true,
    title: (r) => (r as LandmarkRecord).name,
    subtitle: (r) => (r as LandmarkRecord).description,
    blank: { name: "", description: "", placeholder_icon: "pin" },
  },
  moments: {
    label: "Moments",
    noun: { one: "moment", many: "moments" },
    fields: [
      { name: "year", label: "Year", kind: "text", hint: "A year or a span, e.g. 1996 or 2010s." },
      { name: "label", label: "What happened", kind: "textarea" },
      { name: "is_anchor", label: "Anchor moment", kind: "checkbox", hint: "Anchors get the gold circle, as the state's creation and its 30th do." },
      iconField,
    ],
    hasPlaceholderIcon: true,
    title: (r) => (r as MomentRecord).year,
    subtitle: (r) => (r as MomentRecord).label,
    blank: { year: "", label: "", is_anchor: false, placeholder_icon: "star" },
  },
  "hero/images": {
    label: "Hero photos",
    noun: { one: "hero photo", many: "hero photos" },
    fields: [{ name: "caption", label: "Caption", kind: "text", hint: "Written under the photo, e.g. Fajuyi Park, Ado-Ekiti." }, iconField],
    hasPlaceholderIcon: true,
    max: 3,
    title: (r) => (r as HeroImageRecord).caption,
    subtitle: () => "",
    blank: { caption: "", placeholder_icon: "document" },
  },
};

const base = "/api/admin/homepage";
const itemUrl = (list: HomepageList, id: number) => `${base}/${list}/${id}`;

export const homepageApi = {
  list: <T extends ListRecord>(list: HomepageList) => adminRequest<T[]>(`${base}/${list}`),
  create: (list: HomepageList, values: Record<string, unknown>) => adminRequest<ListRecord>(`${base}/${list}`, json("POST", values)),
  update: (list: HomepageList, id: number, changes: Record<string, unknown>) =>
    adminRequest<ListRecord>(itemUrl(list, id), json("PATCH", changes)),
  remove: (list: HomepageList, id: number) => adminRequest<void>(itemUrl(list, id), { method: "DELETE" }),
  reorder: (list: HomepageList, ids: number[]) => adminRequest<ListRecord[]>(`${base}/${list}/reorder`, json("POST", { ids })),
  removeImage: (list: HomepageList, id: number) => adminRequest<ListRecord>(`${itemUrl(list, id)}/image`, { method: "DELETE" }),
  uploadImage: (list: HomepageList, id: number, file: File, onProgress: (fraction: number) => void): Promise<Result<ListRecord>> =>
    uploadImage<ListRecord>(`${itemUrl(list, id)}/image`, file, onProgress),
  getHero: () => adminRequest<HeroRecord>(`${base}/hero`),
  updateHero: (changes: Partial<HeroValues>) => adminRequest<HeroRecord>(`${base}/hero`, json("PATCH", changes)),
};

/** The same checks the backend makes on the headline, for instant feedback. */
export function headlineProblem(headline: string): string | null {
  if (!headline.trim()) return "The headline is required.";
  if (/[<>]/.test(headline)) return "The headline can't contain HTML. Use a new line for a break and *text* for emphasis.";
  if ((headline.match(/\*/g) ?? []).length % 2) return "Every *emphasis* needs an opening and a closing *.";
  if (headline.includes("**")) return "*Emphasis* can't be empty.";
  return null;
}

/** A button link: a page on this site, a section, or an https:// URL (the backend's rule). */
export function hrefProblem(href: string): string | null {
  const value = href.trim();
  if (!value) return "The link is required.";
  if ((value.startsWith("/") || value.startsWith("#") || value.startsWith("https://")) && !value.startsWith("//")) return null;
  return 'A link must start with "/", "#" or "https://".';
}
