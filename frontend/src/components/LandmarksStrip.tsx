type Landmark = {
  className: string;
  name: string;
  loc: string;
  icon: React.ReactNode;
};

const landmarks: Landmark[] = [
  {
    className: "l1",
    name: "Ikogosi Warm Springs",
    loc: "Ikogosi-Ekiti · where warm and cold waters meet",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M2 18c3-6 6-9 10-9s7 3 10 9" />
        <circle cx="17" cy="7" r="2.2" />
      </svg>
    ),
  },
  {
    className: "l2",
    name: "Arinta Waterfalls",
    loc: "Ipole-Iloro, Ekiti West",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M12 3l4 6h-3v5l6 7H5l6-7v-5H8l4-6z" />
      </svg>
    ),
  },
  {
    className: "l3",
    name: "Fajuyi Memorial Park",
    loc: "Ado-Ekiti, the state capital",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M4 19V6a2 2 0 012-2h9l5 5v10a2 2 0 01-2 2H6a2 2 0 01-2-2z" />
      </svg>
    ),
  },
  {
    className: "l4",
    name: "Olosunta Hill",
    loc: "Ikere-Ekiti · sacred hill and skyline",
    icon: (
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
        <path d="M3 20l6-11 4 6 3-5 5 10H3z" />
      </svg>
    ),
  },
];

export default function LandmarksStrip() {
  return (
    <section className="landmarks" id="landmarks">
      <div className="wrap">
        <div className="section-head">
          <h2 className="section-title">The land that raised us</h2>
          <p className="section-desc">
            Hills, springs and places every Ekiti child grew up hearing
            about. This list will grow as more places are added.
          </p>
        </div>
        <div className="land-row">
          {landmarks.map((land) => (
            <div className={`land-card ${land.className}`} key={land.name}>
              <div className="land-photo">{land.icon}</div>
              <div className="land-meta">
                <p className="name">{land.name}</p>
                <p className="loc">{land.loc}</p>
              </div>
            </div>
          ))}
          <div className="land-more">
            + more places
            <br />
            coming soon
          </div>
        </div>
      </div>
    </section>
  );
}
