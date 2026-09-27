export default function FeatureGrid() {
  return (
    <section id="features">
      <div className="wrap">
        <div className="section-head">
          <h2 className="section-title">Six ways into Ekiti&apos;s story</h2>
          <p className="section-desc">
            Every feature draws from the same verified knowledge base — one
            source of truth, many ways to explore it.
          </p>
        </div>
        <div className="bento">
          <div className="card c-timeline">
            <div>
              <div className="card-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6">
                  <path d="M3 12h18M3 12l5-5M3 12l5 5" />
                </svg>
              </div>
              <div className="card-tag">Flagship</div>
              <h3>30-Year Timeline</h3>
              <p>
                A verified record of events and developments from 1996 to
                2026, sourced and dated.
              </p>
            </div>
          </div>

          <div className="card c-ask">
            <div>
              <div className="card-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="var(--rust)" strokeWidth="1.6">
                  <circle cx="12" cy="12" r="9" />
                  <path d="M9 9.5c0-1.7 1.3-2.8 3-2.8s3 1 3 2.5c0 2-3 2-3 4" />
                  <circle cx="12" cy="16.5" r="0.6" fill="var(--rust)" />
                </svg>
              </div>
              <div className="card-tag">AI-powered</div>
              <h3>Ask Ekiti</h3>
              <p>
                A knowledge assistant that answers questions about Ekiti from
                a curated, verified source base.
              </p>
            </div>
          </div>

          <div className="card c-explore">
            <div className="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="var(--forest-2)" strokeWidth="1.6">
                <path d="M9 20l-6-2V4l6 2 6-2 6 2v14l-6-2-6 2z" />
                <path d="M9 6v14M15 4v14" />
              </svg>
            </div>
            <div>
              <h3>Explore Ekiti</h3>
              <p>An interactive map of all 16 LGAs, landmarks and tourism sites.</p>
            </div>
          </div>

          <div className="card c-story">
            <div className="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="var(--rust)" strokeWidth="1.6">
                <path d="M4 19V6a2 2 0 012-2h9l5 5v10a2 2 0 01-2 2H6a2 2 0 01-2-2z" />
                <path d="M8 12h8M8 16h5" />
              </svg>
            </div>
            <div>
              <h3>My Ekiti Story</h3>
              <p>Personal experiences and stories, shared by the people who lived them.</p>
            </div>
          </div>

          <div className="card c-2056">
            <div className="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="var(--forest)" strokeWidth="1.6">
                <path d="M12 3v3M12 18v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M3 12h3M18 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1" />
                <circle cx="12" cy="12" r="4" />
              </svg>
            </div>
            <div>
              <h3>Ekiti 2056</h3>
              <p>Citizens&apos; ideas and visions for the next thirty years.</p>
            </div>
          </div>

          <div className="card c-kb">
            <div className="card-icon" style={{ marginBottom: 0 }}>
              <svg viewBox="0 0 24 24" fill="none" stroke="var(--forest-2)" strokeWidth="1.6">
                <path d="M4 4.5A2.5 2.5 0 016.5 2H20v17H6.5A2.5 2.5 0 004 16.5v-12z" />
                <path d="M4 16.5A2.5 2.5 0 016.5 19H20" />
              </svg>
            </div>
            <div>
              <h3>The Ekiti Knowledge Base</h3>
              <p>
                History, government, education, agriculture, health, tourism,
                culture and statistics — every entry traceable to a
                verifiable source.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
