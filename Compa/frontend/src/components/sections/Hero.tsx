import { Button } from "@/components/ui/Button";
import { productores } from "@/lib/demo-data";
import { shortName } from "@/lib/formatters";

export function Hero() {
  const producer = productores[0];

  return (
    <section className="px-5 pb-20 pt-16 sm:px-8 sm:pb-28 sm:pt-24" id="inicio">
      <div className="mx-auto grid max-w-7xl items-center gap-10 lg:grid-cols-[1fr_420px]">
        <div>
          <div className="eyebrow">COMPRASAL + voz + criterio humano</div>
          <h1 className="max-w-4xl font-display text-[42px] font-bold leading-[1.04] text-ink sm:text-6xl lg:text-[66px]">
            El socio que llama antes de que una MYPE pierda una oportunidad.
          </h1>
          <p className="mt-6 max-w-2xl text-lg leading-8 text-muted">
            Compa detecta contratos públicos compatibles, los explica en español claro y hace las preguntas incómodas antes de decidir si conviene participar.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button href="#demo">Simular una llamada</Button>
            <Button href="#flujo" variant="outline">
              Ver arquitectura
            </Button>
          </div>
        </div>

        <aside className="rounded-[18px] border border-border bg-paper p-6 shadow-soft" aria-label="Resumen de llamada de demostración">
          <div className="mb-5 flex items-center gap-2 text-sm font-semibold text-red">
            <span className="h-2.5 w-2.5 rounded-full bg-red shadow-[0_0_0_6px_rgba(193,39,45,.12)]" />
            Llamada saliente lista
          </div>
          <div className="grid grid-cols-2 gap-3 rounded-2xl bg-surface p-4">
            <div>
              <span className="micro-label">Productora</span>
              <strong className="mt-1 block font-display text-lg">{shortName(producer.nombre)}</strong>
            </div>
            <div>
              <span className="micro-label">Match</span>
              <strong className="mt-1 block font-display text-lg text-red">100%</strong>
            </div>
          </div>
          <p className="my-6 text-[17px] leading-8 text-ink">
            "Hola Vilma, soy Compa. Te llamo porque vi una oportunidad de alimentación escolar que calza con tu comedor."
          </p>
          <div className="flex h-16 items-end gap-2 rounded-2xl border border-border bg-cream px-4 py-3" aria-hidden="true">
            {[28, 44, 22, 52, 36, 48, 26].map((height, index) => (
              <span
                className="w-full rounded-full bg-red/80 motion-safe:animate-wave"
                key={height}
                style={{ height, animationDelay: `${index * 90}ms` }}
              />
            ))}
          </div>
        </aside>
      </div>
    </section>
  );
}
