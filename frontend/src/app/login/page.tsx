import type { Metadata } from "next";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { LoginForm } from "@/components/LoginForm";
import { authOptions } from "@/lib/auth";
import { postLoginPath } from "@/lib/postLogin";

export const metadata: Metadata = {
  title: "Sign in — EKITI@30 DIGITAL",
  robots: { index: false },
};

// Only same-site paths are allowed as a post-login destination, so a crafted
// ?callbackUrl= can't bounce a freshly signed-in admin to another site.
function safeCallback(value: string | string[] | undefined): string {
  const path = Array.isArray(value) ? value[0] : value;
  if (!path || !path.startsWith("/") || path.startsWith("//") || path.startsWith("/\\")) {
    return "/admin";
  }
  return path;
}

export default async function LoginPage({ searchParams }: PageProps<"/login">) {
  const callbackUrl = safeCallback((await searchParams).callbackUrl);

  const session = await getServerSession(authOptions);
  if (session) redirect(postLoginPath(session.user?.role, callbackUrl));

  return (
    <main className="adire-bg flex flex-1 items-center justify-center px-5 py-16">
      <LoginForm callbackUrl={callbackUrl} />
    </main>
  );
}
