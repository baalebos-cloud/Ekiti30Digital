import { forwardToBackend } from "@/lib/backend";
import { isContentAdminKind, isValidKey } from "@/lib/contentAdmin";

// Proxies PATCH (edit) and DELETE on /api/admin/{lgas|timeline}/{key} with the
// admin's token. The key is checked so nothing else on the backend can be
// reached through here.
async function target(ctx: RouteContext<"/api/admin/content/[kind]/[key]">): Promise<string | null> {
  const { kind, key } = await ctx.params;
  if (!isContentAdminKind(kind) || !isValidKey(kind, key)) return null;
  return `/api/admin/${kind}/${encodeURIComponent(key)}`;
}

export async function PATCH(request: Request, ctx: RouteContext<"/api/admin/content/[kind]/[key]">) {
  const path = await target(ctx);
  if (!path) return Response.json({ detail: "Not found" }, { status: 404 });
  return forwardToBackend(request, path, { method: "PATCH", requireRole: "admin" });
}

export async function DELETE(request: Request, ctx: RouteContext<"/api/admin/content/[kind]/[key]">) {
  const path = await target(ctx);
  if (!path) return Response.json({ detail: "Not found" }, { status: 404 });
  return forwardToBackend(request, path, { method: "DELETE", requireRole: "admin" });
}
