type Moment = {
  year: string;
  label: string;
  isAnchor?: boolean;
  icon: React.ReactNode;
};

const moments: Moment[] = [
  {
    year: "1996",
    label: "Ekiti State is created from Ondo State",
    isAnchor: true,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 2l2.9 6 6.6.6-5 4.4 1.6 6.4L12 16l-5.9 3.4 1.5-6.4-5-4.4 6.6-.6z" />
      </svg>
    ),
  },
  {
    year: "1999",
    label: "First elected civilian governor takes office",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M4 21V10l8-6 8 6v11M9 21v-6h6v6" />
      </svg>
    ),
  },
  {
    year: "2010s",
    label: "Growth in roads, schools and healthcare access",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M4 4.5A2.5 2.5 0 016.5 2H20v17H6.5A2.5 2.5 0 004 16.5v-12z" />
      </svg>
    ),
  },
  {
    year: "2022",
    label: "A new administration continues the journey",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 21s-7-4.6-7-10a7 7 0 0114 0c0 5.4-7 10-7 10z" />
        <circle cx="12" cy="11" r="2.2" />
      </svg>
    ),
  },
  {
    year: "2026",
    label: "Ekiti turns 30 — and we're building this, together",
    isAnchor: true,
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M4 21c1.5-5 4-7 8-7s6.5 2 8 7M8 11a4 4 0 118 0c0 2-2 3-2 5H10c0-2-2-3-2-5z" />
      </svg>
    ),
  },
];

export default function MomentsSpine() {
  return (
    <section className="moments" id="moments">
      <div className="wrap">
        <div className="section-head">
          <h2 className="section-title">Moments that shaped us</h2>
          <p className="section-desc">
            From creation to celebration — a journey, not just a timeline.
          </p>
        </div>
        <div className="spine">
          <div className="spine-line"></div>
          {moments.map((m) => (
            <div className={`m-item ${m.isAnchor ? "is-anchor" : ""}`} key={m.year}>
              <div className="m-photo">{m.icon}</div>
              <p className="m-year">{m.year}</p>
              <p className="m-label">{m.label}</p>
            </div>
          ))}
          <div className="m-more">
            <div className="m-more-circle">+ more</div>
            <p className="m-label">More moments being added</p>
          </div>
        </div>
      </div>
    </section>
  );
}
