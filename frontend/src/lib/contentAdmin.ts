/**
 * Admin content editing (the "Manage content" tab on /admin): LGAs and
 * timeline events.
 *
 * The browser calls /api/admin/content/{kind}/..., which forwards to the
 * backend's /api/admin/{lgas|timeline}/... with the admin's token. Records
 * use the stored column names (as in the source CSVs), not the public
 * camelCase feed shapes. updated_by / updated_at are set by the backend
 * from the verified token; nothing here sends them.
 */

export const CONTENT_ADMIN_KINDS = ["lgas", "timeline"] as const;
export type ContentAdminKind = (typeof CONTENT_ADMIN_KINDS)[number];

export function isContentAdminKind(value: string): value is ContentAdminKind {
  return (CONTENT_ADMIN_KINDS as readonly string[]).includes(value);
}

/** Keys as the backend makes them: LGA slugs, timeline ids like "EK-001". */
export function isValidKey(kind: ContentAdminKind, key: string): boolean {
  return kind === "lgas" ? /^[a-z0-9-]{1,120}$/.test(key) : /^[A-Za-z0-9_.-]{1,64}$/.test(key);
}

type Audit = { created_at: string; updated_at: string; updated_by: string | null };

/** Mirrors backend LgaAdminOut. */
export type LgaRecord = Audit & {
  slug: string;
  lga_name: string;
  headquarters: string;
  latitude: number;
  longitude: number;
  last_checked: string;
  verification_status: string;
  [field: string]: string | number | null;
};

/** Mirrors backend TimelineAdminOut. */
export type TimelineRecord = Audit & {
  id: string;
  date_display: string;
  date_start: string;
  event_title: string;
  category: string;
  verification_status: string;
  [field: string]: string | number | null;
};

export type ContentRecord = LgaRecord | TimelineRecord;

export type RecordFor<K extends ContentAdminKind> = K extends "lgas" ? LgaRecord : TimelineRecord;

export function recordKey(kind: ContentAdminKind, record: ContentRecord): string {
  return kind === "lgas" ? (record as LgaRecord).slug : (record as TimelineRecord).id;
}

export function recordTitle(kind: ContentAdminKind, record: ContentRecord): string {
  return kind === "lgas" ? (record as LgaRecord).lga_name : (record as TimelineRecord).event_title;
}

// --- Form fields ---

export type FieldDef = {
  name: string;
  label: string;
  required?: boolean;
  kind?: "text" | "number" | "textarea" | "select";
  options?: readonly string[];
  /** Suggestions offered while typing (free text still allowed). */
  suggestions?: readonly string[];
  hint?: string;
  /** Only settable when creating; shown as read-only text when editing. */
  createOnly?: boolean;
  /** Why a createOnly field can't be edited, shown under its value. */
  lockedHint?: string;
};

const STATUS_LOCKED_HINT =
  "Changed only by CSV import (the research team's channel), not by editing here.";

export type FieldGroup = { title: string; fields: FieldDef[] };

export const TIMELINE_STATUSES = ["Verified", "Single source", "Needs primary source", "Conflicting sources"] as const;

const TIMELINE_CATEGORIES = [
  "Government", "Education", "Health", "Infrastructure", "Tourism",
  "Technology", "Agriculture", "Sports", "Culture", "Other",
] as const;

const sourceFields = (n: number): FieldDef[] => [
  { name: `source_${n}_name`, label: `Source ${n} — name` },
  { name: `source_${n}_type`, label: `Source ${n} — type`, hint: n === 1 ? "e.g. Official government source" : undefined },
  { name: `source_${n}_link`, label: `Source ${n} — link` },
];

export const FIELD_GROUPS: Record<ContentAdminKind, FieldGroup[]> = {
  lgas: [
    {
      title: "The LGA",
      fields: [
        { name: "lga_name", label: "LGA name", required: true, hint: "Changing the name changes the page address (slug)." },
        { name: "headquarters", label: "Headquarters", required: true },
        { name: "latitude", label: "Latitude", required: true, kind: "number", hint: "Decimal degrees, e.g. 7.621111" },
        { name: "longitude", label: "Longitude", required: true, kind: "number", hint: "Decimal degrees, e.g. 5.221389" },
        { name: "coordinate_type", label: "Coordinate type", suggestions: ["Headquarters town centre"] },
      ],
    },
    {
      title: "Places",
      fields: [
        { name: "major_towns_communities", label: "Major towns and communities", kind: "textarea", hint: "Separate with semicolons." },
        { name: "notable_places", label: "Notable places", kind: "textarea", hint: "Separate with semicolons. \"To be researched\" shows as none." },
        { name: "important_institutions", label: "Important institutions", kind: "textarea", hint: "Separate with semicolons." },
      ],
    },
    { title: "Sources", fields: [...sourceFields(1), ...sourceFields(2), ...sourceFields(3), { name: "source_date", label: "Source date", hint: "Free text, e.g. \"Not specified\"" }] },
    {
      title: "Verification",
      fields: [
        {
          name: "verification_status",
          label: "Verification status",
          required: true,
          createOnly: true,
          lockedHint: STATUS_LOCKED_HINT,
          suggestions: ["Pending", "Verified"],
          hint: "Shown on the public page as it's written here.",
        },
        { name: "last_checked", label: "Last checked", required: true, hint: "YYYY-MM-DD" },
        { name: "limitations", label: "Limitations", kind: "textarea" },
        { name: "owner", label: "Owner" },
      ],
    },
  ],
  timeline: [
    {
      title: "The event",
      fields: [
        {
          name: "id",
          label: "Event ID",
          required: true,
          createOnly: true,
          lockedHint: "The event's permanent ID; it can't be changed.",
          hint: "Stable and never renumbered, e.g. EK-051.",
        },
        { name: "event_title", label: "Title", required: true },
        { name: "description", label: "Description", required: true, kind: "textarea", hint: "Only what the cited source supports." },
        { name: "category", label: "Category", required: true, suggestions: TIMELINE_CATEGORIES },
      ],
    },
    {
      title: "Dates",
      fields: [
        { name: "date_display", label: "Date as shown", required: true, hint: "e.g. \"7 Oct 1996 – Aug 1998\"" },
        { name: "date_start", label: "Start date", required: true, hint: "YYYY, YYYY-MM or YYYY-MM-DD. Used for sorting." },
        { name: "date_end", label: "End date", hint: "Same format, for ranges. Leave blank for a single date." },
        { name: "date_precision", label: "Precision", suggestions: ["day", "month", "year", "range", "approximate"] },
        { name: "date_basis", label: "Date basis", suggestions: ["confirmed", "stated_by_source", "inferred", "derived", "approximate", "disputed"] },
      ],
    },
    {
      title: "Source",
      fields: [
        { name: "source", label: "Source", required: true },
        { name: "source_link", label: "Source link" },
        { name: "source_type", label: "Source type", suggestions: ["Government website", "Institutional website", "News outlet", "Reference (Wikipedia)", "Official gazette", "International organisation", "INEC record"] },
        { name: "evidence_type", label: "Evidence type", suggestions: ["official_record", "official_statement", "institutional_statement", "news_report", "reference_work", "traditional_account"] },
        { name: "additional_sources", label: "Additional sources", kind: "textarea", hint: "URLs separated by \" | \"." },
      ],
    },
    {
      title: "Verification and notes",
      fields: [
        {
          name: "verification_status",
          label: "Verification status",
          required: true,
          createOnly: true,
          lockedHint: STATUS_LOCKED_HINT,
          kind: "select",
          options: TIMELINE_STATUSES,
          hint: "Single source is shown as attributed; the last two are never shown as settled.",
        },
        { name: "claim_source_map", label: "Which source supports what", kind: "textarea" },
        { name: "unconfirmed_details", label: "Unconfirmed details", kind: "textarea", hint: "Left out of the description." },
        { name: "claims_and_disputes", label: "Claims and disputes", kind: "textarea" },
        { name: "notes_limitations", label: "Notes and limitations", kind: "textarea" },
      ],
    },
  ],
};

export const NOUN: Record<ContentAdminKind, { one: string; many: string }> = {
  lgas: { one: "LGA", many: "LGAs" },
  timeline: { one: "event", many: "timeline events" },
};

// --- Requests ---

export type ImportSummary = {
  dry_run: boolean;
  created: string[];
  updated: string[];
  unchanged: string[];
  skipped: { line: number; key: string | null; reason: string }[];
};

export type Result<T> = { ok: true; data: T } | { ok: false; status: number | null; message: string };

/** Human message for a failed request, preferring the backend's own detail. */
export function contentErrorMessage(status: number | null, detail?: unknown): string {
  if (status === null) return "Couldn't reach the server. Check your connection and try again.";
  if (status === 401) return "Your session has expired. Sign in again to keep editing.";
  if (status === 403) return "Your account isn't allowed to edit content.";
  if (typeof detail === "string" && (status === 409 || status === 422 || status === 413 || status === 400)) {
    return detail.endsWith(".") ? detail : `${detail}.`;
  }
  // FastAPI's own validation errors: [{loc, msg}, ...].
  if (status === 422 && Array.isArray(detail) && detail.length > 0) {
    const first = detail[0] as { loc?: unknown[]; msg?: string };
    const field = Array.isArray(first.loc) ? String(first.loc[first.loc.length - 1]) : "";
    return `${field ? `${field.replaceAll("_", " ")}: ` : ""}${first.msg ?? "invalid value"}.`;
  }
  if (status === 404) return "This item no longer exists — someone may have deleted it.";
  if (status === 502 || status === 503 || status === 504) return "The content service isn't responding right now. Try again in a moment.";
  return "Something went wrong on the server. Please try again.";
}

async function request<T>(url: string, init?: RequestInit): Promise<Result<T>> {
  try {
    const response = await fetch(url, { cache: "no-store", ...init });
    if (response.status === 204) return { ok: true, data: undefined as T };
    const data: unknown = await response.json().catch(() => null);
    if (response.ok) return { ok: true, data: data as T };
    return {
      ok: false,
      status: response.status,
      message: contentErrorMessage(response.status, (data as { detail?: unknown } | null)?.detail),
    };
  } catch {
    return { ok: false, status: null, message: contentErrorMessage(null) };
  }
}

const base = (kind: ContentAdminKind) => `/api/admin/content/${kind}`;
const json = (method: string, body: unknown): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export const contentApi = {
  list: <K extends ContentAdminKind>(kind: K) => request<RecordFor<K>[]>(base(kind)),
  create: (kind: ContentAdminKind, values: Record<string, unknown>) => request<ContentRecord>(base(kind), json("POST", values)),
  update: (kind: ContentAdminKind, key: string, changes: Record<string, unknown>) =>
    request<ContentRecord>(`${base(kind)}/${encodeURIComponent(key)}`, json("PATCH", changes)),
  remove: (kind: ContentAdminKind, key: string) =>
    request<void>(`${base(kind)}/${encodeURIComponent(key)}`, { method: "DELETE" }),
  importCsv: (kind: ContentAdminKind, file: File, dryRun: boolean) => {
    const form = new FormData();
    form.append("file", file);
    return request<ImportSummary>(`${base(kind)}/import?dry_run=${dryRun}`, { method: "POST", body: form });
  },
};
