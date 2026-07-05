const rules = [
  ["RN-001", "Perfil de negocio antes de recomendar."],
  ["RN-005", "Explicaciones con enlace o referencia oficial."],
  ["RN-006", "Recomendaciones no vinculantes."],
  ["RN-009", "Llamadas solo con consentimiento previo."],
];

export function LegalSection() {
  return (
    <section className="border-y border-border bg-paper px-5 py-20 sm:px-8 sm:py-28" id="legal">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[.9fr_1.1fr]">
        <article>
          <div className="eyebrow">Marco legal</div>
          <h2 className="font-display text-4xl font-bold leading-tight text-ink sm:text-[40px]">
            Asistencia, no representación.
          </h2>
          <p className="mt-4 text-base leading-7 text-muted">
            Compa no oferta, no firma, no adjudica y no modifica oportunidades públicas. Toda recomendación se presenta como sugerencia y conserva referencia a fuente oficial.
          </p>
        </article>
        <div className="grid gap-3 sm:grid-cols-2">
          {rules.map(([code, body]) => (
            <div className="rounded-[18px] border border-border bg-cream p-5" key={code}>
              <strong className="font-display text-lg text-red">{code}</strong>
              <p className="mt-3 text-sm leading-6 text-muted">{body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
