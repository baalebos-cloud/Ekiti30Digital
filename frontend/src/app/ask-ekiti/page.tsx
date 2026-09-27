import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ask Ekiti — EKITI@30 DIGITAL",
  description: "Verified answers about Ekiti history, governance, culture, and institutions.",
};

const sampleQueries = [
  "Who was the first military administrator of Ekiti State?",
  "What was the resolution of the Kiriji War?",
  "List the mineral resources located across the 16 LGAs.",
  "Which tertiary institutions were established between 1996 and 2026?"
];

export default function AskEkitiPage() {
  return (
    <main className="wrap py-12 max-w-3xl mx-auto">
      <div className="text-center">
        <div className="eyebrow-row justify-center">
          <span className="eyebrow-dot"></span> Knowledge Base & Citations
        </div>
        <h1 className="hero-title mt-2">
          Ask <em>Ekiti</em>
        </h1>
        <p className="hero-sub max-w-lg mx-auto">
          A knowledge assistant referencing research notes, historical archives,
          and government source documents curated by the team.
        </p>
      </div>

      {/* Suggested prompts */}
      <div className="mt-8 grid grid-cols-1 sm:grid-cols-2 gap-3">
        {sampleQueries.map((query, i) => (
          <button key={i} className="text-left text-xs p-3 rounded-lg border border-line hover:border-foreground transition">
            {query}
          </button>
        ))}
      </div>

      {/* Console Input */}
      <div className="mt-8 border border-line rounded-xl p-2 flex items-center gap-3">
        <input
          type="text"
          placeholder="Ask a question about Ekiti's 30-year history..."
          className="flex-1 bg-transparent px-3 py-2 text-sm outline-none placeholder:opacity-50"
        />
        <button className="btn-primary text-xs px-4 py-2">
          Inquire
        </button>
      </div>

      <div className="mt-4 flex items-center justify-between text-[11px] opacity-75">
        <span>Curated from Member 3 & 4 archives</span>
        <span className="status-verified">Citations Required</span>
      </div>
    </main>
  );
}