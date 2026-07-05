"use client";

import { useMemo, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import { oportunidades, preguntasFallback, productores, proveedores } from "@/lib/demo-data";
import { formatCurrency, formatDate, shortName } from "@/lib/formatters";
import { getCompatibleSuppliers, getOpportunityMatches } from "@/lib/matching";

type TabId = "oportunidades" | "voz" | "criterio" | "proveedores";

export function DemoWorkspace() {
  const [selectedProductorId, setSelectedProductorId] = useState(productores[0].id);
  const [selectedMatchId, setSelectedMatchId] = useState<string | null>(null);
  const [consent, setConsent] = useState(true);
  const [callState, setCallState] = useState<"idle" | "ready" | "sent">("idle");
  const [activeTab, setActiveTab] = useState<TabId>("oportunidades");

  const productor = productores.find((item) => item.id === selectedProductorId) ?? productores[0];
  const matches = useMemo(() => getOpportunityMatches(productor, oportunidades), [productor]);
  const selectedMatch = matches.find((match) => match.id === selectedMatchId) ?? matches[0];
  const suppliers = useMemo(() => getCompatibleSuppliers(productor, proveedores), [productor]);

  const script = selectedMatch
    ? `Hola ${shortName(productor.nombre)}, soy Compa. Vi "${selectedMatch.titulo}" de ${selectedMatch.institucion}, por ${formatCurrency(selectedMatch.monto)}. Cierra el ${formatDate(selectedMatch.fechaCierre)} y coincide con ${productor.rubro}. Tene un momento para revisarlo?`
    : `Hola ${shortName(productor.nombre)}, soy Compa. Hoy no encontre una oportunidad fuerte para tu rubro, pero puedo seguir revisando el cache de COMPRASAL.`;

  const tabs: { id: TabId; label: string; count: number }[] = [
    { id: "oportunidades", label: "Oportunidades", count: matches.length },
    { id: "voz", label: "Voz", count: 0 },
    { id: "criterio", label: "Criterio", count: preguntasFallback.length },
    { id: "proveedores", label: "Proveedores", count: suppliers.length },
  ];

  function selectProductor(id: string) {
    setSelectedProductorId(id);
    setSelectedMatchId(null);
    setCallState("idle");
    setActiveTab("oportunidades");
  }

  return (
    <div className="pb-28">
      <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
        {/* Left Sidebar - Producer Selector */}
        <div className="space-y-4">
          <div className="surface-panel p-4">
            <div className="flex items-center justify-between mb-4">
              <span className="text-sm font-bold text-ink">Productores</span>
              <Badge variant="neutral">{productores.length} perfiles</Badge>
            </div>
            <div className="grid gap-2">
              {productores.map((item) => (
                <button
                  aria-pressed={item.id === productor.id}
                  className={`pressable rounded-[14px] border p-3.5 text-left transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-red/30 ${
                    item.id === productor.id
                      ? "border-red bg-red/5 shadow-sm"
                      : "border-border bg-cream/50 hover:border-red/30 hover:bg-cream"
                  }`}
                  key={item.id}
                  onClick={() => selectProductor(item.id)}
                  type="button"
                >
                  <strong className="block font-display text-[15px]">{shortName(item.nombre)}</strong>
                  <span className="mt-0.5 block text-xs text-muted">{item.nombreNegocio}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Active Profile Card */}
          <div className="surface-panel overflow-hidden">
            <div className="border-b border-border p-4">
              <span className="micro-label">Perfil activo</span>
              <h3 className="mt-1 font-display text-lg font-bold">{productor.nombre}</h3>
              <Badge variant="red">{productor.rubro}</Badge>
            </div>
            <div className="divide-y divide-border">
              <div className="p-4">
                <span className="micro-label">Negocio</span>
                <strong className="mt-1 block text-sm">{productor.nombreNegocio}</strong>
              </div>
              <div className="grid grid-cols-2 divide-x divide-border">
                <div className="p-4">
                  <span className="micro-label">Ubicacion</span>
                  <strong className="mt-1 block text-sm">{productor.ubicacion}</strong>
                </div>
                <div className="p-4">
                  <span className="micro-label">Capacidad</span>
                  <strong className="mt-1 block text-sm">{productor.capacidad}</strong>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel - Tabbed Content */}
        <div className="surface-panel flex min-h-[500px] flex-col">
          {/* Tab Bar */}
          <div className="flex border-b border-border">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-5 py-4 text-sm font-semibold transition ${
                  activeTab === tab.id
                    ? "text-red"
                    : "text-muted hover:text-ink"
                }`}
                type="button"
              >
                {tab.label}
                {tab.count > 0 && tab.id !== "voz" && (
                  <span className="ml-2 rounded-full bg-cream px-2 py-0.5 text-[11px] font-bold text-muted">
                    {tab.count}
                  </span>
                )}
                {activeTab === tab.id && (
                  <span className="absolute bottom-0 left-4 right-4 h-[2px] rounded-full bg-red" />
                )}
              </button>
            ))}
          </div>

          {/* Tab Content */}
          <div className="flex-1 p-6">
            {activeTab === "oportunidades" && (
              <div className="grid gap-3">
                {matches.length === 0 ? (
                  <div className="flex h-48 items-center justify-center text-sm text-muted">
                    No hay oportunidades compatibles para este rubro.
                  </div>
                ) : (
                  matches.map((match) => (
                    <button
                      aria-pressed={selectedMatch?.id === match.id}
                      className={`pressable rounded-[16px] border p-5 text-left transition-all focus:outline-none focus-visible:ring-2 focus-visible:ring-red/30 ${
                        selectedMatch?.id === match.id
                          ? "border-red bg-red/5"
                          : "border-border bg-cream/40 hover:border-red/30"
                      }`}
                      key={match.id}
                      onClick={() => {
                        setSelectedMatchId(match.id);
                        setCallState("ready");
                      }}
                      type="button"
                    >
                      <div className="grid gap-4 md:grid-cols-[1fr_150px] md:items-start">
                        <div>
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge variant={match.score === 100 ? "red" : "neutral"}>
                              {match.score}% match
                            </Badge>
                            <span className="text-[11px] font-bold text-muted uppercase tracking-wider">
                              {match.tipoContratacion}
                            </span>
                          </div>
                          <h4 className="font-display text-lg font-bold leading-tight">{match.titulo}</h4>
                          <p className="mt-1 text-sm leading-6 text-muted">{match.reason}</p>
                        </div>
                        <div className="rounded-xl border border-border bg-cream p-3 md:text-right">
                          <strong className="block font-display text-lg text-red">
                            {formatCurrency(match.monto)}
                          </strong>
                          <span className="mt-1 block text-[11px] font-bold text-muted uppercase tracking-wider">
                            {match.institucion}
                          </span>
                          <span className="mt-0.5 block text-xs text-muted">
                            Cierra {formatDate(match.fechaCierre)}
                          </span>
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            )}

            {activeTab === "voz" && (
              <div className="grid gap-6 lg:grid-cols-[1fr_300px]">
                <div>
                  <div className="rounded-[16px] border border-border bg-cream p-5 text-lg leading-8 text-ink">
                    {script}
                  </div>
                  <div className="mt-4 flex h-12 items-end gap-1.5 rounded-xl border border-border bg-cream px-4 py-3">
                    {[18, 34, 24, 44, 28, 38, 20].map((h, i) => (
                      <span
                        key={i}
                        className="w-full rounded-full bg-red/70 motion-safe:animate-wave"
                        style={{ height: h, animationDelay: `${i * 90}ms` }}
                      />
                    ))}
                  </div>
                </div>
                <div>
                  <label className="pressable flex items-start gap-3 rounded-xl border border-border bg-cream p-4 text-sm text-muted">
                    <input
                      checked={consent}
                      className="mt-1 h-4 w-4 accent-red"
                      onChange={(e) => setConsent(e.target.checked)}
                      type="checkbox"
                    />
                    Acepta recibir una llamada simulada de Compa para esta demo.
                  </label>
                  <button
                    className="pressable mt-4 w-full rounded-full bg-red py-3 text-sm font-semibold text-paper shadow-red-soft transition hover:bg-red-dark disabled:opacity-40"
                    disabled={!consent || !selectedMatch}
                    onClick={() => setCallState("sent")}
                    type="button"
                  >
                    {callState === "sent" ? "Llamada enviada" : "Reproducir simulacion"}
                  </button>
                  <div className="mt-4 rounded-xl border border-border bg-cream p-4 text-sm leading-6 text-muted">
                    {callState === "sent"
                      ? "Evento registrado. Trace ID: cmp-2026-local."
                      : "Selecciona una oportunidad y confirma consentimiento."}
                  </div>
                </div>
              </div>
            )}

            {activeTab === "criterio" && (
              <div className="grid gap-4 lg:grid-cols-3">
                {preguntasFallback.map((q, i) => (
                  <div
                    key={q.pregunta}
                    className="rounded-[16px] border border-border bg-cream p-5"
                  >
                    <span className="micro-label">Pregunta {i + 1}</span>
                    <p className="mt-3 font-display text-lg font-bold leading-7 text-ink">
                      {q.pregunta}
                    </p>
                    <p className="mt-3 text-sm leading-6 text-muted">{q.intencion}</p>
                  </div>
                ))}
              </div>
            )}

            {activeTab === "proveedores" && (
              <div className="grid gap-4 sm:grid-cols-2">
                {suppliers.length > 0 ? (
                  suppliers.map((s) => (
                    <div
                      key={s.id}
                      className="rounded-[16px] border border-border bg-cream p-5"
                    >
                      <div className="flex items-center justify-between gap-3">
                        <strong className="font-display text-lg">{s.nombre}</strong>
                        <Badge variant="green">{s.personalidad}</Badge>
                      </div>
                      <p className="mt-3 text-sm leading-6 text-muted">{s.capacidad}</p>
                      <p className="mt-1 text-xs font-bold text-muted">{s.ubicacion}</p>
                    </div>
                  ))
                ) : (
                  <div className="col-span-2 flex h-32 items-center justify-center text-sm text-muted">
                    No hay proveedores compatibles en el fallback para este rubro.
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
