export function ProofStrip() {
  const stats = [
    ["20", "oportunidades cacheadas para demo"],
    ["3", "preguntas duras por decisión"],
    ["0", "trámites asumidos por Compa"],
  ];

  return (
    <section className="border-y border-border bg-paper px-5 py-8 sm:px-8">
      <div className="mx-auto grid max-w-7xl gap-4 sm:grid-cols-3">
        {stats.map(([value, label]) => (
          <div className="flex items-baseline gap-3" key={label}>
            <strong className="font-display text-4xl text-red">{value}</strong>
            <span className="text-sm font-medium text-muted">{label}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
