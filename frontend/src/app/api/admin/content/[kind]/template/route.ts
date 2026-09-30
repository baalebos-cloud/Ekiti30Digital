import { forwardToBackend } from "@/lib/backend";
import { isContentAdminKind } from "@/lib/contentAdmin";

// Proxies GET /api/admin/{lgas|timeline}/template.csv: a CSV import template
// (the columns plus one example row), relayed as a file download.
export async function GET(request: Request, ctx: RouteContext<"/api/admin/content/[kind]/template">) {
  const { kind } = await ctx.params;
  if (!isContentAdminKind(kind)) return Response.json({ detail: "Not found" }, { status: 404 });
  return forwardToBackend(request, `/api/admin/${kind}/template.csv`, { method: "GET", requireRole: "admin" });
}
