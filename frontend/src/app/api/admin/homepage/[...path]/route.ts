import { revalidateTag } from "next/cache";

import { forwardFileUpload, forwardToBackend } from "@/lib/backend";
import { HOMEPAGE_CACHE_TAG } from "@/lib/homepage";
import { HOMEPAGE_LISTS } from "@/lib/homepageAdmin";

// Proxies the admin homepage routes (backend app/api/routes/homepage_admin.py)
// with the admin's token. Only these paths and methods pass; anything else is
// a 404 here, so nothing else on the backend can be reached through this.
//
//   hero                         GET, PATCH
//   {list}                       GET, POST
//   {list}/reorder               POST
//   {list}/{id}                  PATCH, DELETE
//   {list}/{id}/image            POST (multipart), DELETE
//
// where {list} is leaders, landmarks, moments or hero/images.

type Method = "GET" | "POST" | "PATCH" | "DELETE";
type Target = { path: string; methods: Method[]; upload?: boolean };

const LIST_PATHS = new Set<string>(HOMEPAGE_LISTS);
const ID = /^[1-9][0-9]{0,9}$/;

function target(segments: string[]): Target | null {
  if (segments.length === 1 && segments[0] === "hero") return { path: "hero", methods: ["GET", "PATCH"] };

  // "hero/images" is the one two-segment list name.
  const listLength = segments[0] === "hero" && segments[1] === "images" ? 2 : 1;
  const list = segments.slice(0, listLength).join("/");
  if (!LIST_PATHS.has(list)) return null;
  const [first, second, ...extra] = segments.slice(listLength);
  if (extra.length) return null;

  if (first === undefined) return { path: list, methods: ["GET", "POST"] };
  if (first === "reorder" && second === undefined) return { path: `${list}/reorder`, methods: ["POST"] };
  if (!ID.test(first)) return null;
  if (second === undefined) return { path: `${list}/${first}`, methods: ["PATCH", "DELETE"] };
  if (second === "image") return { path: `${list}/${first}/image`, methods: ["POST", "DELETE"], upload: true };
  return null;
}

async function handle(request: Request, ctx: RouteContext<"/api/admin/homepage/[...path]">, method: Method) {
  const { path } = await ctx.params;
  const found = target(path);
  if (!found || !found.methods.includes(method)) return Response.json({ detail: "Not found" }, { status: 404 });
  const backendPath = `/api/admin/homepage/${found.path}`;
  const response =
    found.upload && method === "POST"
      ? await forwardFileUpload(request, backendPath, { requireRole: "admin", missingFileMessage: "Choose an image to upload" })
      : await forwardToBackend(request, backendPath, { method, requireRole: "admin" });
  // A saved change: the public homepage's next load fetches fresh content
  // rather than the cached copy (see src/app/api/homepage/route.ts).
  if (method !== "GET" && response.ok) revalidateTag(HOMEPAGE_CACHE_TAG, { expire: 0 });
  return response;
}

export const GET = (request: Request, ctx: RouteContext<"/api/admin/homepage/[...path]">) => handle(request, ctx, "GET");
export const POST = (request: Request, ctx: RouteContext<"/api/admin/homepage/[...path]">) => handle(request, ctx, "POST");
export const PATCH = (request: Request, ctx: RouteContext<"/api/admin/homepage/[...path]">) => handle(request, ctx, "PATCH");
export const DELETE = (request: Request, ctx: RouteContext<"/api/admin/homepage/[...path]">) => handle(request, ctx, "DELETE");
