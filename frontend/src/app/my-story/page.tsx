import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "My Ekiti Story — EKITI@30 DIGITAL",
  description: "Personal narratives, memories, and reflections from Ekiti people at home and in the diaspora.",
};

const sampleStories = [
  {
    title: "October 1st, 1996 in Ado",
    author: "Sample Contributor",
    origin: "Ado-Ekiti LGA",
    period: "1996",
    excerpt: "The morning the state declaration came over the radio, families gathered on the streets to celebrate the realization of a decades-long dream...",
    badge: "Sample Preview"
  },
  {
    title: "Echoes from the Confluence",
    author: "Sample Contributor",
    origin: "Ekiti West LGA",
    period: "2004",
    excerpt: "A childhood visit to where cold and warm springs meet without ever losing their distinct temperatures...",
    badge: "Sample Preview"
  },
  {
    title: "The Book in Every Household",
    author: "Sample Contributor",
    origin: "Ikole LGA",
    period: "2015",
    excerpt: "Reflecting on the intellectual culture and scholarship tradition that defined growing up across Ekiti communities...",
    badge: "Sample Preview"
  }
];

export default function MyStoryPage() {
  return (
    <main className="wrap py-12">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-6 pb-8 border-b border-line">
        <div>
          <div className="eyebrow-row">
            <span className="eyebrow-dot"></span> Oral History & Citizen Archive
          </div>
          <h1 className="hero-title mt-2">
            My Ekiti <em>Story</em>
          </h1>
          <p className="hero-sub max-w-xl">
            Firsthand memories, family journeys, and personal records commemorating thirty years of Ekiti State.
          </p>
        </div>
        <a href="#submit" className="btn-primary self-start md:self-auto">
          Share Your Story
        </a>
      </div>

      {/* Notice distinguishing placeholder vs verified data */}
      <div className="mt-6 border border-line rounded-lg p-3 text-xs opacity-75 flex items-center justify-between">
        <span>Displaying layout preview cards. Community verification pipeline connected via Member 8 workflow.</span>
        <span className="status-single">Preview State</span>
      </div>

      <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        {sampleStories.map((story, i) => (
          <article key={i} className="border border-line rounded-xl p-6 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between text-xs mb-3">
                <span className="opacity-75 font-mono">{story.period}</span>
                <span className="status-single text-[10px]">{story.badge}</span>
              </div>
              <h3 className="font-display font-semibold text-lg mb-2">{story.title}</h3>
              <p className="text-sm opacity-80 leading-relaxed">{story.excerpt}</p>
            </div>
            <div className="mt-6 pt-4 border-t border-line flex justify-between text-xs opacity-75">
              <span>{story.author}</span>
              <span>{story.origin}</span>
            </div>
          </article>
        ))}
      </div>
    </main>
  );
}
