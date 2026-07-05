import { Badge } from "@/components/ui/Badge";

const sources = [
  ["COMPRASAL cacheado", "Oportunidades con fuente oficial y fecha de cierre."],
  ["RUPES público", "Base futura para competidores y proveedores inscritos."],
  ["Fallback sintético", "Datos de demo cuando Supabase o Nemotron no estén disponibles."],
];

export function DataSection() {
  return (
    <section className="px-5 py-20 sm:px-8 sm:py-28" id="datos">
      <div className="mx-auto grid max-w-7xl gap-10 lg:grid-cols-[.9fr_1.1fr]">
        <div>
          <div className="eyebrow">Bolsa de empresas</div>
          <h2 className="font-display text-4xl font-bold leading-tight text-ink sm:text-[40px]">
            Compa también muestra quién más vende al Estado.
          </h2>
          <p className="mt-4 text-base leading-7 text-muted">
            El productor puede ver proveedores del mismo rubro, su capacidad y comportamiento simulado para cotizar insumos. En producción, esta capa se alimenta de RUPES y sanciones públicas.
          </p>
        </div>
        <div className="rounded-[18px] border border-border bg-paper p-5 shadow-soft">
          <div className="mb-5 flex items-center justify-between gap-4">
            <h3 className="font-display text-xl font-bold">Transparencia de datos</h3>
            <Badge variant="pink">auditable</Badge>
          </div>
          <div className="grid gap-3">
            {sources.map(([title, body]) => (
              <article className="rounded-2xl border border-border bg-cream p-4" key={title}>
                <strong className="font-display text-[16px]">{title}</strong>
                <p className="mt-2 text-sm leading-6 text-muted">{body}</p>
              </article>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
