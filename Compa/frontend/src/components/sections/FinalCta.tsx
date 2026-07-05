import { Button } from "@/components/ui/Button";

export function FinalCta() {
  return (
    <section className="relative overflow-hidden bg-forest-900 px-5 py-20 text-paper sm:px-8 sm:py-28">
      <div className="absolute inset-0 bg-[radial-gradient(520px_360px_at_22%_0%,rgba(193,39,45,.38),transparent_62%),radial-gradient(460px_320px_at_88%_100%,rgba(255,197,211,.18),transparent_64%)]" />
      <div className="relative mx-auto max-w-2xl text-center">
        <div className="eyebrow on-dark">Listo para demo</div>
        <h2 className="font-display text-4xl font-bold leading-tight sm:text-[42px]">
          Un prototipo claro para explicar, probar y defender Compa.
        </h2>
        <p className="mt-4 text-base leading-7 text-paper/70">
          El frontend usa datos locales y deja visible el razonamiento de negocio que diferencia a Compa de una alerta automática.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-3">
          <Button href="#demo" variant="pink">
            Volver a la demo
          </Button>
          <Button href="/BRANDBOOK.md" variant="outline" className="border-paper/30 text-paper hover:border-pink hover:text-pink">
            Ver brandbook
          </Button>
        </div>
      </div>
    </section>
  );
}
