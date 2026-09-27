"use client";

import { AnimatePresence, motion } from "motion/react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";

import { SignOutButton } from "@/components/SignOutButton";

export type Viewer = { role: "admin" | "contributor" } | null;

type NavItem = { href: string; label: string; cta?: boolean };

const sections: NavItem[] = [
  { href: "/timeline", label: "Timeline" },
  { href: "/explore", label: "Explore" },
  { href: "/my-ekiti-story", label: "My Story" },
  { href: "/ekiti-2056", label: "Ekiti 2056" },
];

/**
 * Account links by who's looking. Logged-out visitors are pointed at signup
 * ("Contribute") rather than /upload, which would only bounce them to login.
 */
function accountItems(viewer: Viewer): NavItem[] {
  if (!viewer) {
    return [
      { href: "/login", label: "Sign in" },
      { href: "/signup", label: "Contribute", cta: true },
    ];
  }
  const upload = { href: "/upload", label: "Upload", cta: true };
  return viewer.role === "admin" ? [{ href: "/admin", label: "Review desk" }, upload] : [upload];
}

/**
 * The site links, with an underline that slides to the current page. Below
 * 820px they fold into a menu opened by a toggle button.
 */
export function NavLinks({ viewer }: { viewer: Viewer }) {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const [closedAt, setClosedAt] = useState(pathname);

  // Close the mobile menu after navigating.
  if (closedAt !== pathname) {
    setClosedAt(pathname);
    setMenuOpen(false);
  }

  useEffect(() => {
    if (!menuOpen) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setMenuOpen(false);
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  const account = accountItems(viewer);

  const renderLink = (item: NavItem, layoutId: string) => {
    const current = pathname === item.href || pathname.startsWith(`${item.href}/`);
    return (
      <li key={item.href}>
        <Link
          href={item.href}
          aria-current={current ? "page" : undefined}
          className={`nav-link ${current ? "is-current" : ""} ${item.cta ? "is-cta" : ""}`}
        >
          {item.label}
          {current && (
            <motion.span
              layoutId={layoutId}
              className="nav-underline"
              transition={{ type: "spring", stiffness: 420, damping: 34 }}
            />
          )}
        </Link>
      </li>
    );
  };

  const renderItems = (layoutId: string) => (
    <>
      {sections.map((item) => renderLink(item, layoutId))}
      <li className="nav-divider" aria-hidden="true" />
      {account.map((item) => renderLink(item, layoutId))}
      {viewer && (
        <li>
          <SignOutButton variant="nav" />
        </li>
      )}
    </>
  );

  return (
    <>
      <ul className="nav-links">{renderItems("nav-current")}</ul>

      <button
        type="button"
        className="nav-toggle"
        aria-expanded={menuOpen}
        aria-controls="nav-menu"
        aria-label={menuOpen ? "Close menu" : "Open menu"}
        onClick={() => setMenuOpen((open) => !open)}
      >
        <svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
          <motion.path initial={false} animate={{ d: menuOpen ? "M6 6l12 12" : "M4 7h16" }} transition={{ duration: 0.2 }} />
          <motion.path initial={false} animate={{ opacity: menuOpen ? 0 : 1 }} d="M4 12h16" transition={{ duration: 0.15 }} />
          <motion.path initial={false} animate={{ d: menuOpen ? "M6 18L18 6" : "M4 17h16" }} transition={{ duration: 0.2 }} />
        </svg>
      </button>

      <AnimatePresence>
        {menuOpen && (
          <motion.ul
            id="nav-menu"
            className="nav-menu"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2, ease: [0.22, 1, 0.36, 1] }}
          >
            {renderItems("nav-menu-current")}
          </motion.ul>
        )}
      </AnimatePresence>
    </>
  );
}
