/**
 * Browser-side steps of an upload: init and complete go through our own
 * Next.js routes (src/app/api/uploads/), the file itself goes straight to
 * Cloudinary. Every failure becomes an UploadError with a message that's
 * safe to show as-is.
 */

import { isVideo, type AssetRecord, type InitResponse } from "@/lib/uploads";

type Step = "init" | "upload" | "complete";

export class UploadError extends Error {
  constructor(
    message: string,
    /** False when retrying can resume the same asset rather than start over. */
    readonly startOver: boolean,
    readonly signInAgain = false,
  ) {
    super(message);
  }
}

export type CloudinaryResult = { public_id: string; secure_url: string };

function detailOf(body: unknown): string | null {
  const detail = (body as { detail?: unknown } | null)?.detail;
  return typeof detail === "string" ? detail : null;
}

function errorFor(step: Step, status: number, body: unknown): UploadError {
  const detail = detailOf(body);
  if (status === 401) {
    return new UploadError("Your sign-in has expired. Sign in again, then resubmit.", true, true);
  }
  if (status === 403) {
    return new UploadError("Your account isn't allowed to upload yet.", true);
  }
  if (status === 503) {
    return new UploadError(
      "Uploads aren't switched on yet on this server. Please try again later.",
      step === "init",
    );
  }
  if (status === 502 || status === 504) {
    return new UploadError(
      step === "complete"
        ? "Your file uploaded, but we couldn't confirm it just now. Press “Try again” — you won't need to re-upload."
        : "We couldn't reach the upload service. Check your connection and try again.",
      step === "init",
    );
  }
  if (step === "complete") {
    if (status === 409) {
      return new UploadError("This upload has already been recorded — there's nothing more to do.", true);
    }
    if (status === 404) {
      return new UploadError("We lost track of this upload. Please submit it again.", true);
    }
    if (status === 422) {
      return new UploadError(
        `The upload couldn't be verified${detail ? ` (${detail})` : ""}. Please try again.`,
        true,
      );
    }
  }
  if (status === 422) {
    return new UploadError(detail ?? "Some details weren't accepted. Check the form and try again.", true);
  }
  return new UploadError("Something went wrong on our side. Please try again.", step === "init");
}

async function postJson<T>(url: string, body: unknown, step: Step): Promise<T> {
  let response: Response;
  try {
    response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new UploadError(
      "Couldn't reach the server. Check your connection and try again.",
      step === "init",
    );
  }
  const json: unknown = await response.json().catch(() => null);
  if (!response.ok) throw errorFor(step, response.status, json);
  return json as T;
}

export function initUpload(fields: Record<string, string | null>): Promise<InitResponse> {
  return postJson<InitResponse>("/api/uploads/init", fields, "init");
}

export function completeUpload(assetId: number, result: CloudinaryResult): Promise<AssetRecord> {
  return postJson<AssetRecord>(
    `/api/uploads/${assetId}/complete`,
    { public_id: result.public_id, secure_url: result.secure_url },
    "complete",
  );
}

/**
 * Unsigned direct upload to Cloudinary. Uses XHR rather than fetch because
 * only XHR reports upload progress.
 */
export function uploadToCloudinary(
  file: File,
  init: InitResponse,
  onProgress: (fraction: number) => void,
  signal: AbortSignal,
): Promise<CloudinaryResult> {
  const resourceType = isVideo(file) ? "video" : "image";
  const url = `https://api.cloudinary.com/v1_1/${encodeURIComponent(init.cloud_name)}/${resourceType}/upload`;

  const data = new FormData();
  data.append("file", file);
  data.append("upload_preset", init.upload_preset);
  data.append("folder", init.folder);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", url);
    xhr.responseType = "json";

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) onProgress(event.loaded / event.total);
    };
    xhr.onload = () => {
      const body = xhr.response as Partial<CloudinaryResult> & { error?: { message?: string } } | null;
      if (xhr.status >= 200 && xhr.status < 300 && body?.public_id && body.secure_url) {
        onProgress(1);
        resolve({ public_id: body.public_id, secure_url: body.secure_url });
        return;
      }
      const reason = body?.error?.message;
      reject(
        new UploadError(
          `Cloudinary didn't accept the file${reason ? ` (${reason})` : ""}. Please try again.`,
          false,
        ),
      );
    };
    xhr.onerror = () =>
      reject(new UploadError("The upload was interrupted. Check your connection and try again.", false));
    xhr.onabort = () => reject(new UploadError("Upload cancelled.", false));

    signal.addEventListener("abort", () => xhr.abort(), { once: true });
    xhr.send(data);
  });
}
