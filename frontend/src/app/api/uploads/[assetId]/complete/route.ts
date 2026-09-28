import { forwardJsonPost } from "@/lib/backend";

// Proxies POST /api/uploads/{asset_id}/complete with the signed-in user's token.
export async function POST(request: Request, ctx: RouteContext<"/api/uploads/[assetId]/complete">) {
  const { assetId } = await ctx.params;
  // Digits only, so the id can't smuggle extra path segments into the
  // backend URL.
  if (!/^\d+$/.test(assetId)) {
    return Response.json({ detail: "Asset not found" }, { status: 404 });
  }
  return forwardJsonPost(request, `/api/uploads/${assetId}/complete`);
}
