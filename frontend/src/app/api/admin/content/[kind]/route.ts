import { forwardToBackend } from "@/lib/backend";
import { isContentAdminKind } from "@/lib/contentAdmin";

// Proxies GET (list) and POST (create) on /api/admin/{lgas|timeline} with the
// admin's token.
export async function GET(request: Request, ctx: RouteContext<"/api/admin/content/[kind]">) {
  const { kind } = await ctx.params;
  if (!isContentAdminKind(kind)) return Response.json({ detail: "Not found" }, { status: 404 });
  return forwardToBackend(request, `/api/admin/${kind}`, { method: "GET", requireRole: "admin" });
}

export async function POST(request: Request, ctx: RouteContext<"/api/admin/content/[kind]">) {
  const { kind } = await ctx.params;
  if (!isContentAdminKind(kind)) return Response.json({ detail: "Not found" }, { status: 404 });
  return forwardToBackend(request, `/api/admin/${kind}`, { method: "POST", requireRole: "admin" });
}
