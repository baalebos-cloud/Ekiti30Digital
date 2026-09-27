import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Ekiti 2056 — EKITI@30 DIGITAL",
  description: "Citizen ideas, policy blueprints, and aspirations for the next 30 years.",
};

const pillars = [
  { name: "Knowledge Economy & Tech", status: "Open for Proposals" },
  { name: "Agritech & Food Security", status: "Open for Proposals" },
  { name: "Eco-Tourism & Heritage", status: "Open for Proposals" },
  { name: "Infrastructure & Energy", status: "Open for Proposals" },
];

export default function Ekiti2056Page() {
  return (
    <main className="wrap py-12">
      <div className="eyebrow-row">
        <span className="eyebrow-dot"></span> Blueprint for 2026–2056
      </div>
      <h1 className="hero-title mt-2">
        Ekiti <em>2056</em>
      </h1>
      <p className="hero-sub max-w-2xl">
        Thirty years of statehood form the bedrock for our next thirty years.
        What is your blueprint for Ekiti at 60? Submit your vision across our core strategic pillars.
      </p>

      {/* Strategic Pillars */}
      <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
        {pillars.map((pillar) => (
          <div key={pillar.name} className="border border-line rounded-xl p-4">
            <h4 className="font-display font-semibold text-sm">{pillar.name}</h4>
            <span className="text-[11px] status-single mt-2 inline-block">{pillar.status}</span>
          </div>
        ))}
      </div>

      {/* Callout Action */}
      <div className="mt-12 border border-line rounded-xl p-8 flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <h3 className="font-display font-bold text-xl">Submit your vision for Ekiti 2056</h3>
          <p className="text-sm opacity-75 mt-1">
            Proposals and visions will be compiled and verified through Member 8 citizen engagement pipeline.
          </p>
        </div>
        <button className="btn-primary whitespace-nowrap">
          Submit Proposal
        </button>
      </div>
    </main>
  );
}
