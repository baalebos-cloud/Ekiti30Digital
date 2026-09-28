import type { Metadata } from "next";
import { getServerSession } from "next-auth";
import { redirect } from "next/navigation";

import { UploadForm } from "@/components/upload/UploadForm";
import { authOptions } from "@/lib/auth";
import { UPLOAD_FOLDERS } from "@/lib/uploads";

export const metadata: Metadata = {
  title: "Share a photo or video — EKITI@30 DIGITAL",
  robots: { index: false },
};

export default async function UploadPage({ searchParams }: PageProps<"/upload">) {
  // ?folder= pre-selects a collection (e.g. from the My Ekiti Story page);
  // anything that isn't an allowed folder is ignored.
  const requested = (await searchParams).folder;
  const folder = UPLOAD_FOLDERS.find((f) => f.value === requested)?.value;

  if (!(await getServerSession(authOptions))) {
    const back = folder ? `/upload?folder=${folder}` : "/upload";
    redirect(`/login?callbackUrl=${encodeURIComponent(back)}`);
  }

  return (
    <main className="adire-bg flex flex-1 items-start justify-center px-4 py-12 sm:px-5 sm:py-16">
      <UploadForm initialFolder={folder} />
    </main>
  );
}
