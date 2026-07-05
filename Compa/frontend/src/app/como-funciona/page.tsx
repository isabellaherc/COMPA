import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Como funciona",
  description:
    "Descubre la arquitectura de Compa: n8n orquesta los datos, ElevenLabs da la voz, y OpenAI genera preguntas criticas.",
};

const steps = [
  {
    num: "01",
    title: "Cache de datos",
    desc: "Oportunidades y perfiles se leen desde Supabase o desde fallback.json con la misma forma.",
    tech: "Supabase + JSON fallback",
  },
  {
    num: "02",
    title: "Matching por rubro",
    desc: "El rubro exacto sube el score a 100. Coincidencias parciales quedan como recomendacion secundaria.",
    tech: "PL/pgSQL + JS Code node",
  },
  {
    num: "03",
    title: "Llamada con voz",
    desc: "n8n envia productor, rubro y oportunidad detectada como variables dinamicas a ElevenLabs.",
    tech: "n8n Webhook + ElevenLabs ConvAI",
  },
  {
    num: "04",
    title: "Preguntas duras",
    desc: "GPT-4o-mini devuelve pregunta, intencion y palabras clave para guiar la conversacion.",
    tech: "OpenAI JSON Schema + Supabase",
  },
];

const techStack = [
  { name: "n8n Cloud", role: "Orquestacion", desc: "Workflows que conectan Supabase, ElevenLabs y OpenAI cada 6 horas o bajo demanda." },
  { name: "Supabase", role: "Base de datos", desc: "PostgreSQL con 6 tablas, RLS, indices y stored functions para matching." },
  { name: "ElevenLabs", role: "Voz", desc: "Agente conversacional en espanol SV (voz: Luis) con RAG de 8 documentos legales." },
  { name: "OpenAI", role: "Razonamiento", desc: "GPT-4o-mini con salida JSON estructurada para generar preguntas criticas." },
];

export default function ComoFuncionaPage() {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-5 pt-12 sm:px-8 sm:pt-16">
      <div className="mb-12">
        <div className="eyebrow">Arquitectura</div>
        <h1 className="max-w-3xl font-display text-4xl font-bold leading-tight tracking-[-0.02em] text-ink sm:text-5xl">
          n8n orquesta. La voz conversa. Los datos quedan auditables.
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-muted">
          La demo esta disenada para sobrevivir fallas de red: Supabase primero, JSON fallback como ultima defensa.
        </p>
      </div>

      {/* Flow Steps */}
      <div className="mb-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {steps.map((step) => (
          <div key={step.num} className="rounded-[18px] border border-border bg-paper p-5">
            <span className="font-display text-sm font-bold text-red">{step.num}</span>
            <h3 className="mt-4 font-display text-lg font-bold text-ink">{step.title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{step.desc}</p>
            <span className="mt-4 inline-block rounded-full bg-cream px-3 py-1 text-[11px] font-bold text-muted uppercase tracking-wider">
              {step.tech}
            </span>
          </div>
        ))}
      </div>

      {/* Tech Stack Cards */}
      <div className="pb-28">
        <div className="mb-8">
          <div className="eyebrow">Stack tecnologico</div>
          <h2 className="font-display text-3xl font-bold text-ink">Cada pieza tiene un proposito</h2>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {techStack.map((tech) => (
            <div key={tech.name} className="card-lift rounded-[18px] border border-border bg-paper p-6">
              <span className="text-[11px] font-bold text-red uppercase tracking-wider">{tech.role}</span>
              <h3 className="mt-2 font-display text-xl font-bold text-ink">{tech.name}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{tech.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
