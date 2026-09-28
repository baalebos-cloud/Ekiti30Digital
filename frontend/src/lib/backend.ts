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
  method: "GET" | "POST";
  /** Refuse here, before calling the backend, unless the session has this role. */
  requireRole?: "admin";
};

/**
 * Forward the request to `path` on the backend as the signed-in user, and
 * relay the backend's status and body unchanged. POST requests forward the
 * incoming JSON body.
 */

export async function forwardToBackend(
  request: Request,
  path: string,
  { method, requireRole }: ForwardOptions,
): Promise<Response> {
  const session = await getServerSession(authOptions);
  if (!session) return Response.json({ detail: "Not signed in" }, { status: 401 });
  if (requireRole && session.user?.role !== requireRole) {
    return Response.json({ detail: "Not allowed" }, { status: 403 });
  }

  let body: string | undefined;
  if (method === "POST") {
    try {
      body = JSON.stringify(await request.json());
    } catch {
      return Response.json({ detail: "Request body must be JSON" }, { status: 400 });
    }
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${API_URL}${path}`, {
      method,
      headers: { ...(body ? { "Content-Type": "application/json" } : {}), ...(await getBackendAuthHeader()) },
      body,
      cache: "no-store",
      signal: AbortSignal.timeout(30_000),
    });
  } catch {
    return Response.json({ detail: "The backend can't be reached" }, { status: 504 });
  }

  return new Response(await upstream.text(), {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") ?? "application/json" },
  });
}

/** POST the incoming JSON body to `path` as the signed-in user. */
export function forwardJsonPost(request: Request, path: string): Promise<Response> {
  return forwardToBackend(request, path, { method: "POST" });
}
