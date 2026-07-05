import { BrandMark } from "@/components/brand/BrandMark";
import { Button } from "@/components/ui/Button";

const links = [
  { href: "#demo", label: "Demo" },
  { href: "#flujo", label: "Flujo" },
  { href: "#datos", label: "Datos" },
  { href: "#legal", label: "Legal" },
];

export function Nav() {
  return (
    <header className="sticky top-0 z-40 border-b border-border bg-cream/90 backdrop-blur">
      <div className="mx-auto flex h-[72px] max-w-7xl items-center justify-between px-5 sm:px-8">
        <a href="#inicio" className="flex items-center gap-2 font-display text-lg font-bold" aria-label="Compa inicio">
          <BrandMark />
          Compa
        </a>
        <nav className="hidden items-center gap-8 md:flex" aria-label="Navegación principal">
          {links.map((link) => (
            <a className="text-sm font-medium text-muted transition hover:text-ink" href={link.href} key={link.href}>
              {link.label}
            </a>
          ))}
        </nav>
        <Button href="#demo" variant="outline" className="h-9 px-4 text-[13px]">
          Abrir demo
        </Button>
      </div>
    </header>
  );
}
