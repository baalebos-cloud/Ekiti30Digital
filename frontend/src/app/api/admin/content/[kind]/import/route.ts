import { forwardFileUpload } from "@/lib/backend";
import { isContentAdminKind } from "@/lib/contentAdmin";

// Proxies a CSV upload to POST /api/admin/{lgas|timeline}/import with the
// admin's token. ?dry_run=true previews the changes without writing. LGA
// imports may include an optional "images" zip; timeline imports never pass
// one on (the timeline has no images).
export async function POST(request: Request, ctx: RouteContext<"/api/admin/content/[kind]/import">) {
  const { kind } = await ctx.params;
  if (!isContentAdminKind(kind)) return Response.json({ detail: "Not found" }, { status: 404 });
  const dryRun = new URL(request.url).searchParams.get("dry_run") === "true";
  return forwardFileUpload(request, `/api/admin/${kind}/import?dry_run=${dryRun}`, {
    requireRole: "admin",
    optionalFields: kind === "lgas" ? ["images"] : [],
    missingFileMessage: "Choose a CSV file to upload",
  });
}
