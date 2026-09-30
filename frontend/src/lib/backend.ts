/**
 * Server-side forwarding to the FastAPI backend.
 *
 * The browser never calls protected backend routes itself: it calls a
 * Next.js route handler, which uses this to attach the signed-in user's
 * token (read from the httpOnly session cookie) and pass the request on.
 */

import { getServerSession } from "next-auth";

import { authOptions, getBackendAuthHeader } from "@/lib/auth";
import { API_URL } from "@/lib/config";

type ForwardOptions = {
  method: "GET" | "POST" | "PATCH" | "DELETE";
  /** Refuse here, before calling the backend, unless the session has this role. */
  requireRole?: "admin";
};

async function checkSession(requireRole?: "admin"): Promise<Response | null> {
  const session = await getServerSession(authOptions);
  if (!session) return Response.json({ detail: "Not signed in" }, { status: 401 });
  if (requireRole && session.user?.role !== requireRole) {
    return Response.json({ detail: "Not allowed" }, { status: 403 });
  }
  return null;
}

/** Relay the backend's status and body unchanged. */
async function relay(upstream: Response): Promise<Response> {
  // A 204 must not carry a body, not even an empty string.
  if (upstream.status === 204) return new Response(null, { status: 204 });
  const headers: Record<string, string> = {
    "Content-Type": upstream.headers.get("content-type") ?? "application/json",
  };
  // Keeps file downloads (e.g. the CSV import templates) downloads.
  const disposition = upstream.headers.get("content-disposition");
  if (disposition) headers["Content-Disposition"] = disposition;
  return new Response(await upstream.text(), { status: upstream.status, headers });
}

async function send(path: string, init: RequestInit, timeoutMs = 30_000): Promise<Response> {
  try {
    return await relay(
      await fetch(`${API_URL}${path}`, { ...init, cache: "no-store", signal: AbortSignal.timeout(timeoutMs) }),
    );
  } catch {
    return Response.json({ detail: "The backend can't be reached" }, { status: 504 });
  }
}

/**
 * Forward the request to `path` on the backend as the signed-in user, and
 * relay the backend's status and body unchanged. POST and PATCH requests
 * forward the incoming JSON body.
 */
export async function forwardToBackend(
  request: Request,
  path: string,
  { method, requireRole }: ForwardOptions,
): Promise<Response> {
  const refused = await checkSession(requireRole);
  if (refused) return refused;

  let body: string | undefined;
  if (method === "POST" || method === "PATCH") {
    try {
      body = JSON.stringify(await request.json());
    } catch {
      return Response.json({ detail: "Request body must be JSON" }, { status: 400 });
    }
  }

  return send(path, {
    method,
    headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...(await getBackendAuthHeader()) },
    body,
  });
}

/**
 * Forward a multipart upload's required `file` field — plus any of
 * `optionalFields` that hold a non-empty file — to `path` as the signed-in
 * user. Nothing else in the form is passed on; fetch sets the boundary.
 */
export async function forwardFileUpload(
  request: Request,
  path: string,
  {
    requireRole,
    optionalFields = [],
    missingFileMessage = "Choose a file to upload",
  }: Pick<ForwardOptions, "requireRole"> & {
    /** Other file fields to pass on when present (e.g. "images"). */
    optionalFields?: string[];
    missingFileMessage?: string;
  },
): Promise<Response> {
  const refused = await checkSession(requireRole);
  if (refused) return refused;

  let incoming: FormData;
  try {
    incoming = await request.formData();
  } catch {
    return Response.json({ detail: "Expected a multipart form with a file" }, { status: 400 });
  }
  const file = incoming.get("file");
  if (!(file instanceof File)) return Response.json({ detail: missingFileMessage }, { status: 400 });

  const form = new FormData();
  form.append("file", file, file.name);
  for (const name of optionalFields) {
    const extra = incoming.get(name);
    if (extra instanceof File && extra.size > 0) form.append(name, extra, extra.name);
  }
  // Uploads can include images the backend passes on to Cloudinary one by
  // one, so allow far longer than a JSON request.
  return send(path, { method: "POST", headers: await getBackendAuthHeader(), body: form }, 300_000);
}

/** POST the incoming JSON body to `path` as the signed-in user. */
export function forwardJsonPost(request: Request, path: string): Promise<Response> {
  return forwardToBackend(request, path, { method: "POST" });
}
