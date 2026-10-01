import Hero from "@/components/Hero";
import { HomeSectionNav } from "@/components/HomeSectionNav";
import { HomepageProvider } from "@/components/homepage/HomepageContent";
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
      <main className="home flex-1">
        {/* The hero, leaders, landmarks and moments come from the admin-managed
            homepage content, fetched once for all four. */}
        <HomepageProvider>
          <Hero />
          <HomeSectionNav />
          <LeadersStrip />
          <LandmarksStrip />
          <MomentsSpine />
        </HomepageProvider>
        <FeatureGrid />
      </main>
      <Footer />
    </>
  );
}
