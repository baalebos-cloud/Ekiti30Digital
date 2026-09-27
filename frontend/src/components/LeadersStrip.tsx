type Leader = {
  name: string;
  term: string;
};

const leaders: Leader[] = [
  { name: "Mohammed Bawa", term: "1996–1998" },
  { name: "Atanda Yusuf", term: "1998–1999" },
  { name: "Niyi Adebayo", term: "1999–2003" },
  { name: "Ayodele Fayose", term: "2003–2006, 2014–2018" },
  { name: "Segun Oni", term: "2007–2010" },
  { name: "Kayode Fayemi", term: "2010–2014, 2018–2022" },
  { name: "Biodun Oyebanji", term: "2022–present" },
];

function LeaderIcon() {
  return (
    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4">
      <circle cx="12" cy="8" r="3.6" />
      <path d="M4.5 20c1.2-4.4 4.3-6.6 7.5-6.6s6.3 2.2 7.5 6.6" />
    </svg>
  );
}

export default function LeadersStrip() {
  return (
    <section className="leaders" id="leaders">
      <div className="wrap">
        <div className="section-head">
          <h2 className="section-title">The people who led us home</h2>
          <p className="section-desc">
            Every administrator and governor since Ekiti&apos;s creation on 1
            October 1996. Real, verified photos to follow once sourced.
          </p>
        </div>
        <div className="leader-row">
          {leaders.map((leader) => (
            <div className="leader-card" key={leader.name}>
              <div className="leader-photo">
                <LeaderIcon />
              </div>
              <p className="leader-name">{leader.name}</p>
              <p className="leader-term">{leader.term}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
