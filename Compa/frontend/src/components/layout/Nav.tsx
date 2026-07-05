"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { BrandMark } from "@/components/brand/BrandMark";
import { Button } from "@/components/ui/Button";

interface NavLink {
  href: string;
  label: string;
}

const links: NavLink[] = [
  { href: "/demo", label: "Demo" },
  { href: "/como-funciona", label: "Como funciona" },
  { href: "/datos", label: "Datos" },
  { href: "/legal", label: "Legal" },
];

export function Nav() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (menuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  const isActive = (href: string) => {
    if (href === "/") return pathname === "/";
    return pathname.startsWith(href);
  };

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-cream/90 backdrop-blur">
      <div className="mx-auto flex h-[72px] max-w-[1400px] items-center justify-between px-5 sm:px-8">
        <Link
          href="/"
          className="flex items-center gap-2 font-display text-lg font-bold text-ink transition hover:opacity-80"
          aria-label="Compa inicio"
        >
          <BrandMark />
          Compa
        </Link>

        <nav className="hidden items-center gap-1 md:flex" aria-label="Navegacion principal">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`nav-pill relative z-10 rounded-full px-4 py-2 text-sm font-medium transition-colors duration-200 ${
                isActive(link.href)
                  ? "active text-red"
                  : "text-muted hover:text-ink"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-3">
          <Button href="/demo" variant="primary" className="h-9 px-4 text-[13px]">
            Abrir demo
          </Button>

          <button
            type="button"
            className="pressable flex h-9 w-9 items-center justify-center rounded-full border border-border md:hidden"
            onClick={() => setMenuOpen(!menuOpen)}
            aria-label={menuOpen ? "Cerrar menu" : "Abrir menu"}
            aria-expanded={menuOpen}
          >
            <span className="relative h-4 w-4">
              <span
                className={`absolute left-0 top-0 h-[1.5px] w-4 rounded-full bg-ink transition-transform duration-200 ${
                  menuOpen ? "translate-y-[6px] rotate-45" : ""
                }`}
              />
              <span
                className={`absolute left-0 top-[6px] h-[1.5px] w-4 rounded-full bg-ink transition-opacity duration-150 ${
                  menuOpen ? "opacity-0" : ""
                }`}
              />
              <span
                className={`absolute left-0 top-[12px] h-[1.5px] w-4 rounded-full bg-ink transition-transform duration-200 ${
                  menuOpen ? "-translate-y-[6px] -rotate-45" : ""
                }`}
              />
            </span>
          </button>
        </div>
      </div>

      {menuOpen && (
        <div
          className="fixed inset-0 top-[72px] z-30 bg-cream/98 backdrop-blur md:hidden"
          style={{
            opacity: 0,
            animation: "menu-enter 240ms cubic-bezier(.23, 1, .32, 1) forwards",
          }}
        >
          <nav className="flex flex-col gap-2 px-5 pt-6 stagger-children" aria-label="Navegacion movil">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`rounded-xl px-5 py-4 text-lg font-medium transition-colors duration-200 ${
                  isActive(link.href)
                    ? "bg-red/10 text-red"
                    : "text-ink hover:bg-surface"
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>
        </div>
      )}
    </header>
  );
}
