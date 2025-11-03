import { Navigation } from "@/components/navigation";
import { HeroSection } from "@/components/hero-section";
import { HowItWorksSection } from "@/components/how-it-works-section";
import { FeaturesSection } from "@/components/features-section";
import { UseCasesSection } from "@/components/use-cases-section";
import { CTASection } from "@/components/cta-section";
import { Footer } from "@/components/footer";

export default function Home() {
  return (
    <main className="min-h-screen">
      <Navigation />
      <HeroSection />
      <HowItWorksSection />
      <FeaturesSection />
      <UseCasesSection />
      <CTASection />
      <Footer />
    </main>
  );
}
