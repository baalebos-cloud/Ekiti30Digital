import type { Metadata } from "next";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { ReviewDesk } from "@/components/review/ReviewDesk";
import { authOptions } from "@/lib/auth";

export const metadata: Metadata = {
  title: "Review desk — EKITI@30 DIGITAL",
  robots: { index: false },
};

export default async function AdminPage() {
  const session = await getServerSession(authOptions);
  if (!session) redirect("/login?callbackUrl=/admin");
  // Contributors can sign in too, but the review desk is admin-only.
  if (session.user?.role !== "admin") redirect("/upload");

  return (
    <main className="wrap w-full flex-1 py-12">
      <div className="flex flex-wrap items-end justify-between gap-4 border-b border-line pb-6">
        <div>
          <div className="eyebrow-row">
            <span className="eyebrow-dot" /> Signed in as {session.user?.email}
          </div>
          <h1 className="hero-title" style={{ fontSize: "clamp(28px, 3.6vw, 40px)" }}>
            Review <em>desk</em>
          </h1>
          <p className="max-w-[56ch] text-sm text-ink-soft">
            Nothing reaches the public site or signs in until it&apos;s approved here. Take a look,
            then approve — or reject with a short reason. Use Manage content to edit LGAs, the
            timeline and the homepage.
          </p>
        </div>
      </div>
      <ReviewDesk />
    </main>
  );
}
