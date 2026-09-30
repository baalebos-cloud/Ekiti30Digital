import { forwardFileUpload } from "@/lib/backend";
import { isValidKey } from "@/lib/contentAdmin";

// Proxies an image upload to POST /api/admin/lgas/{slug}/image with the
// admin's token. LGAs only: the timeline has no images, so any other kind is
// a 404 here rather than a request the backend would reject.
export async function POST(request: Request, ctx: RouteContext<"/api/admin/content/[kind]/[key]/image">) {
  const { kind, key } = await ctx.params;
  if (kind !== "lgas" || !isValidKey("lgas", key)) return Response.json({ detail: "Not found" }, { status: 404 });
  return forwardFileUpload(request, `/api/admin/lgas/${encodeURIComponent(key)}/image`, {
    requireRole: "admin",
    missingFileMessage: "Choose an image to upload",
  });
}
