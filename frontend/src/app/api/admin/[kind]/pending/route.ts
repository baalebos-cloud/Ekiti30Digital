import { forwardToBackend } from "@/lib/backend";
import { isReviewKind } from "@/lib/review";

// Proxies GET /api/admin/{assets|contributors}/pending with the admin's token.
export async function GET(request: Request, ctx: RouteContext<"/api/admin/[kind]/pending">) {
  const { kind } = await ctx.params;
  if (!isReviewKind(kind)) return Response.json({ detail: "Not found" }, { status: 404 });
  return forwardToBackend(request, `/api/admin/${kind}/pending`, { method: "GET", requireRole: "admin" });
}
