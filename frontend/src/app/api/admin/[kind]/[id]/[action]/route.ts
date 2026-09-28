import { forwardToBackend } from "@/lib/backend";
import { isReviewKind } from "@/lib/review";

// Proxies POST /api/admin/{assets|contributors}/{id}/{approve|reject} with
// the admin's token. Every segment is checked so nothing else on the
// backend can be reached through here.
export async function POST(request: Request, ctx: RouteContext<"/api/admin/[kind]/[id]/[action]">) {
  const { kind, id, action } = await ctx.params;
  if (!isReviewKind(kind) || !/^\d+$/.test(id) || (action !== "approve" && action !== "reject")) {
    return Response.json({ detail: "Not found" }, { status: 404 });
  }
  return forwardToBackend(request, `/api/admin/${kind}/${id}/${action}`, { method: "POST", requireRole: "admin" });
}
