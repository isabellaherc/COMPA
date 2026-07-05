"use client";

import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { oportunidades, preguntasFallback, productores, proveedores } from "@/lib/demo-data";
import { formatCurrency, formatDate, shortName } from "@/lib/formatters";
import { getCompatibleSuppliers, getOpportunityMatches } from "@/lib/matching";

export function DemoWorkspace() {
  const [selectedProductorId, setSelectedProductorId] = useState(productores[0].id);
  const [selectedMatchId, setSelectedMatchId] = useState<string | null>(null);
  const [consent, setConsent] = useState(true);
  const [callState, setCallState] = useState<"idle" | "ready" | "sent">("idle");

  const productor = productores.find((item) => item.id === selectedProductorId) ?? productores[0];
  const matches = useMemo(() => getOpportunityMatches(productor, oportunidades), [productor]);
  const selectedMatch = matches.find((match) => match.id === selectedMatchId) ?? matches[0];
  const suppliers = useMemo(() => getCompatibleSuppliers(productor, proveedores), [productor]);

  const script = selectedMatch
    ? `Hola ${shortName(productor.nombre)}, soy Compa. Vi "${selectedMatch.titulo}" de ${selectedMatch.institucion}, por ${formatCurrency(selectedMatch.monto)}. Cierra el ${formatDate(selectedMatch.fechaCierre)} y coincide con ${productor.rubro}. ¿Tenés un momento para revisar si te conviene?`
    : `Hola ${shortName(productor.nombre)}, soy Compa. Hoy no encontré una oportunidad fuerte para tu rubro, pero puedo seguir revisando el cache de COMPRASAL.`;

  function selectProductor(id: string) {
    setSelectedProductorId(id);
    setSelectedMatchId(null);
    setCallState("idle");
  }

  return (
    <section className="px-5 py-20 sm:px-8 sm:py-28" id="demo">
      <div className="mx-auto max-w-7xl">
        <div className="mb-12 grid gap-6 lg:grid-cols-[1fr_420px]">
          <div>
            <div className="eyebrow">Demo operativa</div>
            <h2 className="max-w-3xl font-display text-4xl font-bold leading-tight text-ink sm:text-[40px]">
              El recorrido completo en una sola pantalla.
            </h2>
          </div>
          <p className="text-base leading-7 text-muted">
            Selecciona un productor. Compa calcula matches por rubro, arma el mensaje de ElevenLabs, genera preguntas críticas y muestra proveedores compatibles.
          </p>
        </div>

        <div className="grid gap-5 lg:grid-cols-[300px_1fr]">
          <aside className="rounded-[18px] border border-border bg-paper p-4 shadow-soft" aria-label="Productores de demostración">
            <PanelTitle label="Productores" detail="dataset fallback" />
            <div className="mt-4 grid gap-2">
              {productores.map((item) => (
                <button
                  className={`rounded-2xl border p-4 text-left transition focus:outline-none focus-visible:ring-4 focus-visible:ring-red/15 ${
                    item.id === productor.id
                      ? "border-red bg-red/5"
                      : "border-border bg-cream hover:border-red/50"
                  }`}
                  key={item.id}
                  onClick={() => selectProductor(item.id)}
                  type="button"
                >
                  <strong className="block font-display text-[15px]">{shortName(item.nombre)}</strong>
                  <span className="mt-1 block text-xs font-medium text-muted">{item.nombreNegocio}</span>
                </button>
              ))}
            </div>
          </aside>

          <div className="rounded-[18px] border border-border bg-paper p-5 shadow-soft">
            <div className="flex flex-wrap items-start justify-between gap-4 border-b border-border pb-5">
              <div>
                <span className="micro-label">Perfil activo</span>
                <h3 className="mt-1 font-display text-2xl font-bold">{productor.nombre}</h3>
              </div>
              <Badge variant="red">{productor.rubro}</Badge>
            </div>

            <div className="grid gap-3 py-5 sm:grid-cols-2 xl:grid-cols-4">
              <ProfileItem label="Negocio" value={productor.nombreNegocio} />
              <ProfileItem label="Ubicación" value={productor.ubicacion} />
              <ProfileItem label="Capacidad" value={productor.capacidad} />
              <ProfileItem label="Experiencia Estado" value={productor.experienciaEstado} />
            </div>

            <div className="grid gap-5 xl:grid-cols-[1.1fr_.9fr]">
              <div className="rounded-2xl border border-border bg-cream p-4">
                <PanelTitle label="Oportunidades recomendadas" detail={`${matches.length} matches`} />
                <div className="mt-4 grid gap-3">
                  {matches.map((match) => (
                    <button
                      className={`rounded-2xl border p-4 text-left transition focus:outline-none focus-visible:ring-4 focus-visible:ring-red/15 ${
                        selectedMatch?.id === match.id
                          ? "border-red bg-paper"
                          : "border-border bg-paper/70 hover:border-red/50"
                      }`}
                      key={match.id}
                      onClick={() => {
                        setSelectedMatchId(match.id);
                        setCallState("ready");
                      }}
                      type="button"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <strong className="font-display text-[16px] leading-snug">{match.titulo}</strong>
                        <span className="rounded-full bg-red px-2.5 py-1 text-xs font-bold text-paper">{match.score}%</span>
                      </div>
                      <div className="mt-3 flex flex-wrap gap-2 text-xs font-semibold text-muted">
                        <span>{match.institucion}</span>
                        <span>{formatCurrency(match.monto)}</span>
                        <span>Cierra {formatDate(match.fechaCierre)}</span>
                      </div>
                      <p className="mt-3 text-sm leading-6 text-muted">{match.reason}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-border bg-cream p-4">
                <PanelTitle label="Guion de llamada" detail="ElevenLabs" />
                <div className="mt-4 rounded-2xl border border-border bg-paper p-4 text-[15px] leading-7 text-ink">
                  {script}
                </div>
                <label className="mt-4 flex items-start gap-3 rounded-2xl border border-border bg-paper p-3 text-sm text-muted">
                  <input
                    checked={consent}
                    className="mt-1 h-4 w-4 accent-red"
                    onChange={(event) => setConsent(event.target.checked)}
                    type="checkbox"
                  />
                  Acepta recibir una llamada simulada de Compa para esta demo.
                </label>
                <Button
                  className="mt-4 w-full"
                  disabled={!consent || !selectedMatch}
                  onClick={() => setCallState("sent")}
                  type="button"
                >
                  Reproducir simulación
                </Button>
                <div className="mt-4 min-h-16 rounded-2xl border border-border bg-paper p-4 text-sm leading-6 text-muted">
                  {callState === "sent"
                    ? "Evento registrado: n8n enviaría agent_id, teléfono y dynamic_variables a ElevenLabs. Trace ID demo: cmp-2026-local."
                    : "Selecciona una oportunidad y confirma consentimiento para preparar la llamada."}
                </div>
              </div>
            </div>

            <div className="mt-5 grid gap-5 xl:grid-cols-[.9fr_1.1fr]">
              <div className="rounded-2xl border border-border bg-cream p-4">
                <PanelTitle label="Preguntas duras" detail="retar_decision" />
                <div className="mt-4 grid gap-3">
                  {preguntasFallback.map((question, index) => (
                    <article className="rounded-2xl border border-border bg-paper p-4" key={question.pregunta}>
                      <span className="micro-label">Pregunta {index + 1}</span>
                      <p className="mt-2 font-semibold leading-7 text-ink">{question.pregunta}</p>
                      <p className="mt-2 text-sm leading-6 text-muted">{question.intencion}</p>
                    </article>
                  ))}
                </div>
              </div>

              <div className="rounded-2xl border border-border bg-cream p-4">
                <PanelTitle label="Proveedores compatibles" detail={`${suppliers.length} disponibles`} />
                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                  {suppliers.length > 0 ? (
                    suppliers.map((supplier) => (
                      <article className="rounded-2xl border border-border bg-paper p-4" key={supplier.id}>
                        <div className="flex items-center justify-between gap-3">
                          <strong className="font-display text-[15px]">{supplier.nombre}</strong>
                          <Badge variant="green">{supplier.personalidad}</Badge>
                        </div>
                        <p className="mt-3 text-sm leading-6 text-muted">{supplier.capacidad}</p>
                        <p className="mt-1 text-xs font-semibold text-muted">{supplier.ubicacion}</p>
                      </article>
                    ))
                  ) : (
                    <div className="rounded-2xl border border-border bg-paper p-4 text-sm text-muted">
                      No hay proveedores compatibles en el fallback para este rubro.
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function PanelTitle({ label, detail }: { label: string; detail: string }) {
  return (
    <div className="flex items-center justify-between gap-3">
      <span className="font-display text-sm font-bold">{label}</span>
      <small className="rounded-full bg-surface px-2.5 py-1 text-xs font-semibold text-muted">{detail}</small>
    </div>
  );
}

function ProfileItem({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-border bg-cream p-4">
      <span className="micro-label">{label}</span>
      <strong className="mt-2 block text-sm leading-6">{value}</strong>
    </div>
  );
}
