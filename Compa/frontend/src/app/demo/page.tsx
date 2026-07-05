import type { Metadata } from "next";
import { DemoWorkspace } from "@/components/sections/DemoWorkspace";

export const metadata: Metadata = {
  title: "Demo interactiva",
  description:
    "Explora el asistente de Compa: selecciona un productor, mira oportunidades detectadas y simula una llamada con voz.",
};

export default function DemoPage() {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-5 pt-12 sm:px-8 sm:pt-16">
      <div className="mb-10">
        <div className="eyebrow">Workspace</div>
        <h1 className="max-w-3xl font-display text-4xl font-bold leading-tight tracking-[-0.02em] text-ink sm:text-5xl">
          Experimenta Compa en accion
        </h1>
        <p className="mt-3 max-w-2xl text-base leading-7 text-muted">
          Selecciona un perfil de productor, explora las oportunidades que el sistema detecta
          y simula la llamada que recibiria un productor real.
        </p>
      </div>
      <DemoWorkspace />
    </div>
  );
}
