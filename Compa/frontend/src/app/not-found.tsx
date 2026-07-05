import Link from "next/link";
import type { Metadata } from "next";
import { BrandMark } from "@/components/brand/BrandMark";
import { Button } from "@/components/ui/Button";

export const metadata: Metadata = {
  title: "Pagina no encontrada",
};

export default function NotFound() {
  return (
    <div className="flex min-h-[70dvh] items-center justify-center px-5">
      <div className="max-w-md text-center">
        <div className="mb-6 flex justify-center">
          <BrandMark className="h-16 w-16 opacity-40" />
        </div>
        <h1 className="font-display text-5xl font-bold leading-none text-ink">404</h1>
        <p className="mt-4 text-base leading-7 text-muted">
          Esta pagina no existe o fue movida. Volve al inicio para seguir explorando Compa.
        </p>
        <div className="mt-8 flex items-center justify-center gap-4">
          <Button href="/" variant="primary">
            Ir al inicio
          </Button>
          <Button href="/demo" variant="outline">
            Abrir demo
          </Button>
        </div>
      </div>
    </div>
  );
}
