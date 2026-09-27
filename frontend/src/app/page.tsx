import Hero from "@/components/Hero";
import LeadersStrip from "@/components/LeadersStrip";
import LandmarksStrip from "@/components/LandmarksStrip";
import MomentsSpine from "@/components/MomentsSpine";
import FeatureGrid from "@/components/FeatureGrid";
import Footer from "@/components/Footer";

// Note: <Nav /> is already rendered globally in layout.tsx — don't add
// a Header component here, it would duplicate the site nav.
export default function Home() {
  return (
    <>
      <main className="flex-1">
        <Hero />
        <LeadersStrip />
        <LandmarksStrip />
        <MomentsSpine />
        <FeatureGrid />
      </main>
      <Footer />
    </>
  );
}
