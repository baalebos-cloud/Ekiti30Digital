/**
 * Upload conventions shared by the upload form and its API routes.
 *
 * Mirrors backend/app/services/cloudinary_convention.py. The backend stays
 * the source of truth: POST /api/uploads/init returns the live format list
 * and size limit, and the form re-checks the file against those before it
 * reaches Cloudinary. These copies only let the form reject a bad file
 * before creating a pending asset at all.
 */

export const UPLOAD_FOLDERS = [
  { value: "EKITI30/Historical", label: "Historical", hint: "Archival photos, documents, early days" },
  { value: "EKITI30/LGAs", label: "Local Government Areas", hint: "Towns, landmarks, life across the 16 LGAs" },
  { value: "EKITI30/Culture_Tourism", label: "Culture & Tourism", hint: "Festivals, crafts, destinations" },
  { value: "EKITI30/Community_Stories", label: "Community Stories", hint: "People, families, everyday moments" },
  { value: "EKITI30/Ekiti_2056", label: "Ekiti 2056", hint: "Visions for the next thirty years" },
] as const;

// The backend accepts any non-empty string for now; the form limits it to
// these so the data stays clean until the backend enforces a list.
export const RIGHTS_OPTIONS = [
  { value: "owned", label: "I own it", hint: "I took this photo or video myself" },
  { value: "permission_granted", label: "I have permission", hint: "The owner has agreed to it being shared" },
  { value: "public_domain", label: "Public domain", hint: "Free of copyright, e.g. very old or government works" },
] as const;

// From 02_LGAs/ekiti_lgas.csv. Suggestions only — location_lga is free text.
export const EKITI_LGAS = [
  "Ado Ekiti", "Efon", "Ekiti East", "Ekiti South-West", "Ekiti West", "Emure",
  "Aiyekire", "Ido/Osi", "Ijero", "Ikere", "Ikole", "Ilejemeje",
  "Irepodun/Ifelodun", "Ise/Orun", "Moba", "Oye",
] as const;

export const ALLOWED_FORMATS = ["jpg", "png", "webp", "mp4"] as const;
export const MAX_UPLOAD_BYTES = 10 * 1024 * 1024;

export const FILE_ACCEPT = ".jpg,.jpeg,.png,.webp,.mp4,image/jpeg,image/png,image/webp,video/mp4";

export type InitResponse = {
  asset_id: number;
  cloud_name: string;
  upload_preset: string;
  folder: string;
  max_file_bytes: number;
  allowed_formats: string[];
};

export type AssetRecord = {
  id: number;
  public_id: string | null;
  cloudinary_url: string | null;
  folder: string;
  contributor: string;
  source: string | null;
  location_lga: string | null;
  description: string | null;
  rights_status: string;
  related_content_id: string | null;
  status: "pending" | "approved" | "rejected";
  rejection_reason: string | null;
  reviewed_by: string | null;
  reviewed_at: string | null;
  created_at: string;
  updated_at: string;
};

/** The file's format as Cloudinary names it ("jpeg" → "jpg"), or null. */
export function fileFormat(file: File): string | null {
  const ext = file.name.split(".").pop()?.toLowerCase();
  if (!ext || ext === file.name.toLowerCase()) return null;
  return ext === "jpeg" ? "jpg" : ext;
}

export function isVideo(file: File): boolean {
  return fileFormat(file) === "mp4";
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** A human-readable reason the file can't be uploaded, or null if it's fine. */
export function checkFile(
  file: File,
  formats: readonly string[] = ALLOWED_FORMATS,
  maxBytes: number = MAX_UPLOAD_BYTES,
): string | null {
  const format = fileFormat(file);
  if (!format || !formats.includes(format)) {
    return `That file type isn't supported. Please choose a ${listFormats(formats)} file.`;
  }
  if (file.size > maxBytes) {
    return `That file is ${formatBytes(file.size)} — the limit is ${formatBytes(maxBytes)}. Try a smaller or compressed version.`;
  }
  if (file.size === 0) return "That file is empty. Please choose another.";
  return null;
}

export function listFormats(formats: readonly string[] = ALLOWED_FORMATS): string {
  const upper = formats.map((f) => f.toUpperCase());
  return upper.length > 1 ? `${upper.slice(0, -1).join(", ")} or ${upper.at(-1)}` : upper.join("");
}

export function folderLabel(value: string): string {
  return UPLOAD_FOLDERS.find((f) => f.value === value)?.label ?? value;
}
