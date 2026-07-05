import type { Metadata } from "next";
import Link from "next/link";
import { BrandMark } from "@/components/brand/BrandMark";
import { productores } from "@/lib/demo-data";
import { formatCurrency } from "@/lib/formatters";

export const metadata: Metadata = {
  title: "Compa | Asesor de compras publicas para MYPE",
  description:
    "Compa detecta oportunidades de COMPRASAL, las explica por voz y reta decisiones de productores salvadorenos antes de ofertar.",
};

const quickLinks = [
  {
    href: "/demo",
    title: "Demo interactiva",
    desc: "Selecciona un productor y mira como Compa detecta oportunidades en vivo.",
    accent: "bg-red",
    stat: "4 productores",
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 5.5h2.5V8H4V5.5zm4.5 0H11V8H8.5V5.5zm4.5 0h2.5V8H13V5.5zM4 10.5h2.5V13H4v-2.5zm4.5 0H11V13H8.5v-2.5zm4.5 0h2.5V13H13v-2.5z" fill="currentColor" /></svg>
    ),
  },
  {
    href: "/como-funciona",
    title: "Como funciona",
    desc: "n8n orquesta, ElevenLabs llama, OpenAI cuestiona. Conoce la arquitectura.",
    accent: "bg-green",
    stat: "4 tecnologias",
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="6" cy="6" r="2" fill="currentColor" /><circle cx="14" cy="6" r="2" fill="currentColor" /><circle cx="6" cy="14" r="2" fill="currentColor" /><circle cx="14" cy="14" r="2" fill="currentColor" /></svg>
    ),
  },
  {
    href: "/datos",
    title: "Datos y fuentes",
    desc: "COMPRASAL, RUPES, datos sinteticos. Todo trazable, nada es caja negra.",
    accent: "bg-pink-deep",
    stat: "3 fuentes",
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 3L4 7v6l6 4 6-4V7l-6-4z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" /><path d="M10 10v7" stroke="currentColor" strokeWidth="1.5" /><path d="M4 7l6 3 6-3" stroke="currentColor" strokeWidth="1.5" /></svg>
    ),
  },
  {
    href: "/legal",
    title: "Marco legal",
    desc: "Asistencia, no representacion. Conoce las reglas que guian cada recomendacion.",
    accent: "bg-ink",
    stat: "4 normativas",
    icon: (
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M7 3h6v2H7V3zm-2 2h10v1H5V5zm0 2h10v10H5V7zm2 2v6h1.5v-6H7zm3 0v6h1.5v-6H10z" fill="currentColor" /></svg>
    ),
  },
];

export default function Home() {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-5 pt-16 sm:px-8 sm:pt-24">
      {/* Welcome Row */}
      <div className="mb-16 grid gap-8 lg:grid-cols-[1fr_380px] lg:items-end">
        <div>
          <div className="eyebrow">Bienvenido a Compa</div>
          <h1 className="max-w-4xl font-display text-[44px] font-bold leading-[1.06] tracking-[-0.02em] text-ink sm:text-6xl lg:text-[72px]">
            El socio que llama antes de que una{" "}
            <span className="text-red">MYPE pierda</span> una oportunidad.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-muted">
            Compa detecta contratos publicos compatibles, los explica en espanol claro y hace las
            preguntas incomodas antes de decidir si conviene participar.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link
              href="/demo"
              className="pressable inline-flex h-12 items-center gap-2 rounded-full bg-red px-7 text-sm font-semibold text-paper shadow-red-soft transition hover:bg-red-dark"
            >
              Probar demo
              <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 8h10M9 4l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
            </Link>
            <Link
              href="/como-funciona"
              className="pressable inline-flex h-12 items-center rounded-full border border-border px-7 text-sm font-semibold text-ink transition hover:border-red hover:text-red"
            >
              Como funciona
            </Link>
          </div>
        </div>

        {/* Live demo card */}
        <div className="double-bezel">
          <div className="p-6">
            <div className="mb-5 flex items-center gap-3">
              <span className="flex h-3 w-3 items-center justify-center rounded-full bg-red shadow-[0_0_0_4px_rgba(193,39,45,.18)]">
                <span className="signal-bar block h-2 w-2 rounded-full bg-red" />
              </span>
              <span className="text-xs font-bold uppercase tracking-wider text-muted">Demo en vivo</span>
            </div>
            <div className="flex items-center gap-3 mb-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-cream">
                <BrandMark className="h-5 w-5" />
              </div>
              <div>
                <strong className="block font-display text-base">{productores[0].nombre}</strong>
                <span className="text-xs text-muted">{productores[0].nombreNegocio}</span>
              </div>
            </div>
            <div className="grid grid-cols-3 gap-3 rounded-xl bg-cream p-4">
              {[
                ["Rubro", productores[0].rubro],
                ["Ubicacion", productores[0].ubicacion],
                ["Capacidad", productores[0].capacidad],
              ].map(([label, value]) => (
                <div key={label}>
                  <span className="micro-label">{label}</span>
                  <span className="mt-1 block text-sm font-semibold">{value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bento Grid */}
      <div className="grid grid-cols-1 gap-4 pb-28 sm:grid-cols-2 lg:grid-cols-4 lg:grid-rows-[180px_180px]">
        {quickLinks.map((link, i) => {
          const spans = [
            "lg:col-span-2 lg:row-span-1",
            "lg:col-span-1 lg:row-span-2",
            "lg:col-span-1 lg:row-span-1",
            "lg:col-span-2 lg:row-span-1",
          ];
          return (
            <Link
              key={link.href}
              href={link.href}
              className={`card-lift group relative overflow-hidden rounded-[20px] border border-border bg-paper p-6 ${spans[i]}`}
            >
              <div className={`mb-4 flex h-9 w-9 items-center justify-center rounded-xl ${link.accent} text-paper`}>
                {link.icon}
              </div>
              <h3 className="font-display text-xl font-bold text-ink">{link.title}</h3>
              <p className="mt-2 max-w-sm text-sm leading-6 text-muted">{link.desc}</p>
              <span className="mt-5 inline-flex items-center gap-1.5 rounded-full bg-cream px-3 py-1.5 text-xs font-bold text-muted">
                {link.stat}
                <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M4 2l4 4-4 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" /></svg>
              </span>
              <div className={`absolute -bottom-6 -right-6 h-24 w-24 rounded-full opacity-[.06] transition group-hover:scale-150 group-hover:opacity-[.10] ${link.accent}`} />
            </Link>
          );
        })}
      </div>
    </div>
  );
}
