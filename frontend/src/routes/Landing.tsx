import { SiteHeader } from "@/components/layout/SiteHeader";
import { SiteFooter } from "@/components/layout/SiteFooter";
import { Hero } from "@/components/landing/Hero";
import { ClubLogos } from "@/components/landing/ClubLogos";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { InspectionWindow } from "@/components/landing/InspectionWindow";
import { FeatureBento } from "@/components/landing/FeatureBento";
import { Reliability } from "@/components/landing/Reliability";
import { Personas } from "@/components/landing/Personas";
import { Testimonial } from "@/components/landing/Testimonial";
import { FinalCTA } from "@/components/landing/FinalCTA";

export function Landing() {
  return (
    <div className="min-h-dvh bg-bg text-fg">
      <SiteHeader />
      <main>
        <Hero />
        <ClubLogos />
        <HowItWorks />
        <InspectionWindow />
        <FeatureBento />
        <Reliability />
        <Personas />
        <Testimonial />
        <FinalCTA />
      </main>
      <SiteFooter />
    </div>
  );
}
