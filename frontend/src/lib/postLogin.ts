/**
 * Where to send someone after they sign in.
 *
 * Admins always land in the admin area: most sign-ins start from a public
 * "Upload"/"Share" link (callbackUrl=/upload), and an admin signing in from
 * there still expects the review desk. Contributors can't use /admin, so
 * they go to the upload form instead of an admin callback.
 *
 * `callbackUrl` must already be a safe same-site path.
 */
export function postLoginPath(role: string | undefined, callbackUrl: string): string {
  const isAdminPath = callbackUrl === "/admin" || callbackUrl.startsWith("/admin/") || callbackUrl.startsWith("/admin?");
  if (role === "admin") return isAdminPath ? callbackUrl : "/admin";
  return isAdminPath ? "/upload" : callbackUrl;
}
