import Link from "next/link";

const COLUMNS = [
  {
    title: "Explore",
    links: [
      { href: "/timeline", label: "30-year timeline" },
      { href: "/explore", label: "The 16 LGAs" },
      { href: "/ekiti-2056", label: "Ekiti 2056" },
    ],
  },
  {
    title: "Contribute",
    links: [
      { href: "/my-ekiti-story", label: "My Ekiti Story" },
      { href: "/signup", label: "Create an account" },
      { href: "/login", label: "Sign in" },
    ],
  },
];

export default function Footer() {
  return (
    <footer className="site-footer">
      <div className="wrap site-footer-grid">
        <div>
          <div className="wordmark">
            EKITI<span className="num">@30</span> DIGITAL
          </div>
          <p className="site-footer-tagline">Our Story. Our People. Our Future.</p>
          <p className="site-footer-note">
            Every entry is traceable to a source. Citizen stories and visions are shown as personal
            accounts, not verified history.
          </p>
        </div>
        {COLUMNS.map((col) => (
          <div key={col.title}>
            <h2 className="site-footer-title">{col.title}</h2>
            <ul>
              {col.links.map((l) => (
                <li key={l.href}>
                  <Link href={l.href}>{l.label}</Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="wrap site-footer-base">
        <span>Marking 30 years of Ekiti State, 1996–2026</span>
        <span>ekiti30digital@gmail.com</span>
      </div>
    </footer>
  );
}
