import { BrandMark } from "@/components/brand/BrandMark";

export function Footer() {
  return (
    <footer className="bg-forest-900 px-5 py-10 text-paper/65 sm:px-8">
      <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 text-sm">
        <div className="flex items-center gap-2 font-display text-lg font-bold text-paper">
          <BrandMark />
          Compa
        </div>
        <span>Prototipo frontend, Buildathon UFG 2026.</span>
      </div>
    </footer>
  );
}
