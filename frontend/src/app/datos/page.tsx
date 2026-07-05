import type { Metadata } from "next";
import { Badge } from "@/components/ui/Badge";

export const metadata: Metadata = {
  title: "Datos y transparencia",
  description:
    "Compa usa datos de COMPRASAL, RUPES y fuentes sinteticas. Cada decision es auditable y trazable.",
};

const sources = [
  {
    title: "COMPRASAL cacheado",
    desc: "Oportunidades con fuente oficial y fecha de cierre. URLs trazables a la plataforma original.",
    badge: "oficial",
  },
  {
    title: "RUPES publico",
    desc: "Base futura para competidores y proveedores inscritos en el registro unico de proveedores del Estado.",
    badge: "futuro",
  },
  {
    title: "Fallback sintetico",
    desc: "Datos de demo generados desde NVIDIA Nemotron-Personas-El-Salvador cuando Supabase no esta disponible.",
    badge: "demo",
  },
];

const principles = [
  {
    title: "Fuentes trazables",
    desc: "Cada oportunidad incluye su URL fuente en COMPRASAL. Los datos sinteticos estan marcados como tales.",
  },
  {
    title: "Fallback resiliente",
    desc: "Si Supabase no responde, el sistema usa datos pre-cacheados. La demo nunca se rompe por una falla de red.",
  },
  {
    title: "Privacidad por diseno",
    desc: "Los datos personales de productores son sinteticos. En produccion se requerira consentimiento explicito.",
  },
  {
    title: "Auditable",
    desc: "Cada decision y pregunta generada por IA queda registrada en Supabase con trazabilidad completa.",
  },
];

export default function DatosPage() {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-5 pt-12 sm:px-8 sm:pt-16">
      <div className="mb-12">
        <div className="eyebrow">Bolsa de empresas</div>
        <h1 className="max-w-3xl font-display text-4xl font-bold leading-tight tracking-[-0.02em] text-ink sm:text-5xl">
          Compa tambien muestra quien mas vende al Estado.
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-muted">
          El productor puede ver proveedores del mismo rubro, su capacidad y comportamiento simulado
          para cotizar insumos. En produccion esta capa se alimenta de RUPES y sanciones publicas.
        </p>
      </div>

      {/* Data Sources */}
      <div className="mb-16 grid gap-4 sm:grid-cols-3">
        {sources.map((src) => (
          <div key={src.title} className="card-lift rounded-[18px] border border-border bg-paper p-6">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-display text-lg font-bold text-ink">{src.title}</h3>
              <Badge variant={src.badge === "oficial" ? "green" : src.badge === "futuro" ? "neutral" : "pink"}>
                {src.badge}
              </Badge>
            </div>
            <p className="text-sm leading-6 text-muted">{src.desc}</p>
          </div>
        ))}
      </div>

      {/* Principles */}
      <div className="pb-28">
        <div className="mb-8">
          <div className="eyebrow">Principios de datos</div>
          <h2 className="font-display text-3xl font-bold text-ink">Transparencia desde el diseno</h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-muted">
            Compa esta construido sobre el principio de que cada recomendacion debe poder
            rastrearse hasta su fuente original. Nada es una caja negra.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {principles.map((p) => (
            <div key={p.title} className="rounded-[18px] border border-border bg-cream p-5">
              <h3 className="font-display text-lg font-bold text-ink">{p.title}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{p.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
