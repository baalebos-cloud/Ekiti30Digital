import type { Metadata } from "next";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { SignupForm } from "@/components/SignupForm";
import { authOptions } from "@/lib/auth";

export const metadata: Metadata = {
  title: "Create an account — EKITI@30 DIGITAL",
  robots: { index: false },
};

export default async function SignupPage() {
  // Already signed in: nothing to sign up for.
  if (await getServerSession(authOptions)) redirect("/upload");

  return (
    <main className="adire-bg flex flex-1 items-center justify-center px-5 py-16">
      <SignupForm />
    </main>
  );
}
