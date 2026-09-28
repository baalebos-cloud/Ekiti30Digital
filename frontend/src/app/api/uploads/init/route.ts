import { forwardJsonPost } from "@/lib/backend";

// Proxies POST /api/uploads/init with the signed-in user's token.
export async function POST(request: Request) {
  return forwardJsonPost(request, "/api/uploads/init");
}
