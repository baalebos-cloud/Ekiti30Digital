export default function Hero() {
  return (
    <section className="hero">
      <div className="wrap hero-inner">
        <div>
          <div className="eyebrow-row">
            <span className="eyebrow-dot"></span> Marking 30 years of Ekiti
            State, 1996–2026
          </div>
          <h1 className="hero-title">
            Welcome home.
            <br />
            Thirty years of <em>us</em>.
          </h1>
          <p className="hero-sub">
            The leaders who guided us, the hills and springs that raised us,
            the moments we celebrated together — one place to remember where
            we&apos;ve been, and imagine where we&apos;re going.
          </p>
          <div className="hero-actions">
            <a className="btn-primary" href="#moments">
              Walk Through Our Journey
            </a>
            <a className="btn-secondary" href="#">
              Share Your Ekiti Story
            </a>
          </div>
        </div>

        <div className="board">
          <div className="polaroid p1">
            <div className="pin"></div>
            <div className="frame">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M4 19V6a2 2 0 012-2h9l5 5v10a2 2 0 01-2 2H6a2 2 0 01-2-2z" />
              </svg>
            </div>
            <div className="cap">Fajuyi Park, Ado-Ekiti</div>
          </div>
          <div className="polaroid p2">
            <div className="pin"></div>
            <div className="frame">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <circle cx="12" cy="8" r="3.4" />
                <path d="M5 20c1-4 4-6 7-6s6 2 7 6" />
              </svg>
            </div>
            <div className="cap">Governors, 1996–2026</div>
          </div>
          <div className="polaroid p3">
            <div className="pin"></div>
            <div className="frame">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
                <path d="M2 18c3-6 6-9 10-9s7 3 10 9" />
                <circle cx="17" cy="7" r="2.4" />
              </svg>
            </div>
            <div className="cap">Ikogosi Warm Springs</div>
          </div>
        </div>
      </div>
    </section>
  );
}
