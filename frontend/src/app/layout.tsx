import type { Metadata } from "next";
import { Fraunces, Work_Sans } from "next/font/google";
import { Nav } from "@/components/Nav";
import "./globals.css";

// Font pairing per 17_Design/design-tokens.md: Fraunces for display/headings,
// Work Sans for body/UI. Weights mirror the Google Fonts import used in
// 17_Design/homepage-preview.html.
// Both are variable fonts — load the default variable weight range rather
// than an explicit weight/style array. (Turbopack in this Next.js version
// fails to resolve next/font/google requests with multiple weight/style
// entries: "next/font/google queries have exactly one entry".)
const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
});

const workSans = Work_Sans({
  variable: "--font-work-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "EKITI@30 DIGITAL",
  description: "Our Story. Our People. Our Future.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="en"
      className={`${fraunces.variable} ${workSans.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-bg text-ink">
        <Nav />
        <div className="flex flex-1 flex-col">{children}</div>
      </body>
    </html>
  );
}
