const steps = [
  {
    id: "01",
    title: "Cache de datos",
    body: "Oportunidades y perfiles se leen desde Supabase o desde fallback.json con la misma forma.",
  },
  {
    id: "02",
    title: "Matching por rubro",
    body: "El rubro exacto sube el score a 100. Coincidencias parciales quedan como recomendación secundaria.",
  },
  {
    id: "03",
    title: "Llamada con voz",
    body: "n8n envía productor, rubro y oportunidad detectada como variables dinámicas a ElevenLabs.",
  },
  {
    id: "04",
    title: "Preguntas duras",
    body: "Codex/OpenAI devuelve pregunta, intención y palabras clave para guiar la conversación.",
  },
];

export function ArchitectureFlow() {
  return (
    <section className="border-y border-border bg-paper px-5 py-20 sm:px-8 sm:py-28" id="flujo">
      <div className="mx-auto max-w-7xl">
        <div className="mb-12 max-w-3xl">
          <div className="eyebrow">Arquitectura</div>
          <h2 className="font-display text-4xl font-bold leading-tight text-ink sm:text-[40px]">
            n8n orquesta. La voz conversa. Los datos quedan auditables.
          </h2>
          <p className="mt-4 text-base leading-7 text-muted">
            La demo está diseñada para sobrevivir fallas de red: Supabase primero, JSON fallback como última defensa.
          </p>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {steps.map((step) => (
            <article className="rounded-[18px] border border-border bg-cream p-5" key={step.id}>
              <span className="font-display text-sm font-bold text-red">{step.id}</span>
              <h3 className="mt-5 font-display text-xl font-bold">{step.title}</h3>
              <p className="mt-3 text-sm leading-6 text-muted">{step.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}
