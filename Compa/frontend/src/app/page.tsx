import { ArchitectureFlow } from "@/components/sections/ArchitectureFlow";
import { DataSection } from "@/components/sections/DataSection";
import { DemoWorkspace } from "@/components/sections/DemoWorkspace";
import { FinalCta } from "@/components/sections/FinalCta";
import { Hero } from "@/components/sections/Hero";
import { LegalSection } from "@/components/sections/LegalSection";
import { ProofStrip } from "@/components/sections/ProofStrip";
import { Canopy } from "@/components/layout/Canopy";
import { Footer } from "@/components/layout/Footer";
import { Nav } from "@/components/layout/Nav";

export default function Home() {
  return (
    <>
      <Canopy />
      <Nav />
      <main>
        <Hero />
        <ProofStrip />
        <DemoWorkspace />
        <ArchitectureFlow />
        <DataSection />
        <LegalSection />
        <FinalCta />
      </main>
      <Footer />
    </>
  );
}
