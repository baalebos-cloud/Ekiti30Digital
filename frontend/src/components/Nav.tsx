import { getServerSession } from "next-auth";
import Link from "next/link";

import { NavLinks, type Viewer } from "@/components/NavLinks";
import { authOptions } from "@/lib/auth";

export async function Nav() {
  // Read on the server so the right account links are there on first paint.
  const session = await getServerSession(authOptions);
  const role = session?.user?.role;
  const viewer: Viewer = session ? { role: role === "admin" ? "admin" : "contributor" } : null;

  return (
    <header className="site-header">
      <nav className="wrap site-nav">
        <Link href="/" className="site-brand">
          EKITI<span className="num">@30</span> DIGITAL
        </Link>
        <NavLinks viewer={viewer} />
      </nav>
    </header>
  );
}
