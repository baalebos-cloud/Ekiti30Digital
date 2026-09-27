import Link from "next/link";

const sections = [
  { href: "/timeline", label: "Timeline" },
  { href: "/explore", label: "Explore" },
  { href: "/my-story", label: "My Story" },
  { href: "/ask-ekiti", label: "Ask Ekiti" },
  { href: "/ekiti-2056", label: "Ekiti 2056" },
];

export function Nav() {
  return (
    <header className="border-b border-line">
      <nav className="mx-auto flex max-w-3xl flex-wrap items-center gap-x-6 gap-y-2 px-6 py-4">
        <Link href="/" className="font-display font-semibold">
          EKITI@30 DIGITAL
        </Link>
        <ul className="flex flex-wrap gap-x-6 gap-y-2 text-sm">
          {sections.map((section) => (
            <li key={section.href}>
              <Link href={section.href} className="hover:underline">
                {section.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>
    </header>
  );
}
