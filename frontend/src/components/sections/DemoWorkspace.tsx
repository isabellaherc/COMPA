"use client";

import { useEffect, useMemo, useState } from "react";
import { Badge } from "@/components/ui/Badge";
import {
  generarDocumento,
  getOportunidadesFeed,
  retarDecision,
  TIPOS_DOCUMENTO,
  type GenerarDocumentoResponse,
  type OportunidadLive,
  type RetarResponse,
} from "@/lib/api";
import { preguntasFallback, productores, proveedores } from "@/lib/demo-data";
import { formatCurrency, formatDate, shortName } from "@/lib/formatters";
import { getCompatibleSuppliers } from "@/lib/matching";

type TabId = "oportunidades" | "criterio" | "documentos" | "voz" | "proveedores";

type LiveMatch = OportunidadLive & { score: number; reason: string };

const TIPO_LABEL: Record<string, string> = {
  LP: "Licitación Pública",
  LG: "Libre Gestión",
  CD: "Contratación Directa",
};

function scoreOportunidad(rubroProductor: string, op: OportunidadLive): LiveMatch {
  const exact = op.rubro_requerido === rubroProductor;
  const sharedWord = op.rubro_requerido
    .toLowerCase()
    .includes(rubroProductor.split(" ")[0].toLowerCase());
  const score = exact ? 100 : sharedWord ? 70 : 38;
  return {
    ...op,
    score,
    reason: exact
      ? "Rubro exacto y capacidad compatible"
      : sharedWord
        ? "Rubro parcialmente relacionado"
        : "Baja afinidad con el perfil",
  };
}

export function DemoWorkspace() {
  const [selectedProductorId, setSelectedProductorId] = useState(productores[0].id);
  const [selectedMatchId, setSelectedMatchId] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<TabId>("oportunidades");

  // ── Feed en vivo (Supabase via n8n) ────────────────────────────────────────
  const [feed, setFeed] = useState<{ items: OportunidadLive[]; live: boolean; loading: boolean }>({
    items: [],
    live: false,
    loading: true,
  });

  useEffect(() => {
    getOportunidadesFeed()
      .then((data) => setFeed({ items: data.oportunidades, live: true, loading: false }))
      .catch(() => setFeed({ items: [], live: false, loading: false }));
  }, []);

  const productor = productores.find((item) => item.id === selectedProductorId) ?? productores[0];

  const matches = useMemo(
    () =>
      feed.items
        .map((op) => scoreOportunidad(productor.rubro, op))
        .filter((m) => m.score >= 60)
        .sort((a, b) => b.score - a.score || b.monto - a.monto),
    [feed.items, productor],
  );

  const selectedMatch = matches.find((m) => m.id === selectedMatchId) ?? matches[0];
  const suppliers = useMemo(() => getCompatibleSuppliers(productor, proveedores), [productor]);

  // ── Criterio (retar_decision → OpenAI real) ────────────────────────────────
  const [decision, setDecision] = useState("");
  const [reto, setReto] = useState<{ loading: boolean; error: string | null; data: RetarResponse | null }>({
    loading: false,
    error: null,
    data: null,
  });

  async function enviarReto() {
    if (decision.trim().length < 10 || reto.loading) return;
    setReto({ loading: true, error: null, data: null });
    try {
      const data = await retarDecision({
        decision: decision.trim(),
        nombreProductor: productor.nombre,
        rubro: productor.rubro,
        capacidad: productor.capacidad,
        oportunidadTitulo: selectedMatch?.titulo,
        oportunidadInstitucion: selectedMatch?.institucion,
        oportunidadMonto: selectedMatch?.monto,
      });
      setReto({ loading: false, error: null, data });
    } catch (e) {
      setReto({ loading: false, error: e instanceof Error ? e.message : "error", data: null });
    }
  }

  // ── Documentos (generar_documento → plantillas DINAC) ─────────────────────
  const [tipoDoc, setTipoDoc] = useState<string>(TIPOS_DOCUMENTO[0].value);
  const [doc, setDoc] = useState<{ loading: boolean; error: string | null; data: GenerarDocumentoResponse | null }>({
    loading: false,
    error: null,
    data: null,
  });

  async function pedirDocumento() {
    if (doc.loading) return;
    setDoc({ loading: true, error: null, data: null });
    try {
      const data = await generarDocumento({ tipoDocumento: tipoDoc });
      setDoc({ loading: false, error: null, data });
    } catch (e) {
      setDoc({ loading: false, error: e instanceof Error ? e.message : "error", data: null });
    }
  }

  const script = selectedMatch
    ? `Doña ${shortName(productor.nombre).split(" ")[0]}, ¿cómo está? Habla Compa. Vi una oportunidad para su negocio: ${selectedMatch.titulo} de ${selectedMatch.institucion} por ${formatCurrency(selectedMatch.monto)} con cierre ${formatDate(selectedMatch.fecha_cierre)}. ¿Tiene un momento para revisarla?`
    : `Hola ${shortName(productor.nombre)}, soy Compa. Hoy no encontré una oportunidad fuerte para tu rubro, pero sigo revisando COMPRASAL cada 6 horas.`;

  const tabs: { id: TabId; label: string; count: number }[] = [
    { id: "oportunidades", label: "Oportunidades", count: matches.length },
    { id: "criterio", label: "Criterio", count: reto.data ? reto.data.preguntas.length : 3 },
    { id: "documentos", label: "Documentos", count: TIPOS_DOCUMENTO.length },
    { id: "voz", label: "Voz", count: 0 },
    { id: "proveedores", label: "Proveedores", count: suppliers.length },
  ];

  function selectProductor(id: string) {
    setSelectedProductorId(id);
    setSelectedMatchId(null);
    setActiveTab("oportunidades");
    setReto({ loading: false, error: null, data: null });
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

          {/* Live status */}
          <div className="surface-panel flex items-center gap-3 p-4">
            <span
              className={`h-2.5 w-2.5 rounded-full ${feed.live ? "bg-green shadow-[0_0_0_4px_rgba(46,83,57,.15)]" : "bg-muted"}`}
            />
            <span className="text-xs font-semibold text-muted">
              {feed.loading
                ? "Conectando con Supabase…"
                : feed.live
                  ? `Backend en vivo — ${feed.items.length} licitaciones abiertas`
                  : "Sin conexión — mostrando datos locales"}
            </span>
          </div>
        </div>

        {/* Right Panel - Tabbed Content */}
        <div className="surface-panel flex min-h-[500px] flex-col">
          {/* Tab Bar */}
          <div className="flex flex-wrap border-b border-border">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`relative px-5 py-4 text-sm font-semibold transition ${
                  activeTab === tab.id ? "text-red" : "text-muted hover:text-ink"
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
            {/* ── OPORTUNIDADES: feed real de Supabase via n8n ── */}
            {activeTab === "oportunidades" && (
              <div className="grid gap-3">
                {feed.loading ? (
                  <div className="flex h-48 items-center justify-center text-sm text-muted">
                    Consultando licitaciones reales en Supabase…
                  </div>
                ) : matches.length === 0 ? (
                  <div className="flex h-48 flex-col items-center justify-center gap-2 text-sm text-muted">
                    <span>No hay oportunidades abiertas compatibles con {productor.rubro}.</span>
                    <span className="text-xs">
                      El agente sigue revisando el feed cada 6 horas — probá otro perfil.
                    </span>
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
                      onClick={() => setSelectedMatchId(match.id)}
                      type="button"
                    >
                      <div className="grid gap-4 md:grid-cols-[1fr_170px] md:items-start">
                        <div>
                          <div className="flex flex-wrap items-center gap-2 mb-2">
                            <Badge variant={match.score === 100 ? "red" : "neutral"}>
                              {match.score}% match
                            </Badge>
                            <span className="text-[11px] font-bold text-muted uppercase tracking-wider">
                              {TIPO_LABEL[match.tipo_contratacion] || match.tipo_contratacion}
                            </span>
                            {feed.live && (
                              <span className="text-[10px] font-bold uppercase tracking-wider text-green">
                                ● en vivo
                              </span>
                            )}
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
                            Cierra {formatDate(match.fecha_cierre)}
                          </span>
                        </div>
                      </div>
                    </button>
                  ))
                )}
              </div>
            )}

            {/* ── CRITERIO: retar_decision real (OpenAI + Supabase) ── */}
            {activeTab === "criterio" && (
              <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
                <div>
                  <span className="micro-label">Contale tu decisión a Compa</span>
                  <textarea
                    className="mt-2 w-full rounded-[14px] border border-border bg-cream p-4 text-sm leading-6 text-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-red/30"
                    maxLength={400}
                    onChange={(e) => setDecision(e.target.value)}
                    placeholder={`Ej: "Quiero ofertar en ${selectedMatch ? selectedMatch.titulo : "una licitación"} aunque nunca le he vendido al Estado"`}
                    rows={4}
                    value={decision}
                  />
                  <div className="mt-3 flex flex-wrap items-center gap-3">
                    <button
                      className="pressable rounded-full bg-red px-6 py-3 text-sm font-semibold text-paper shadow-red-soft transition hover:bg-red-dark disabled:opacity-40"
                      disabled={decision.trim().length < 10 || reto.loading}
                      onClick={enviarReto}
                      type="button"
                    >
                      {reto.loading ? "Compa está pensando…" : "Que Compa me rete"}
                    </button>
                    <span className="text-xs text-muted">
                      Genera 3 preguntas con OpenAI y guarda la decisión en Supabase.
                    </span>
                  </div>

                  {reto.error && (
                    <p className="mt-4 text-sm text-red">
                      No se pudo consultar al backend ({reto.error}). Abajo quedan las preguntas de
                      respaldo.
                    </p>
                  )}

                  <div className="mt-6 grid gap-4">
                    {(reto.data?.preguntas ?? preguntasFallback.map((q) => q.pregunta)).map((q, i) => (
                      <div className="rounded-[16px] border border-border bg-cream p-5" key={`${i}-${q.slice(0, 12)}`}>
                        <div className="flex items-center gap-2">
                          <span className="micro-label">Pregunta {i + 1}</span>
                          {reto.data && !reto.data._fallback && (
                            <span className="text-[10px] font-bold uppercase tracking-wider text-green">
                              ● generada en vivo
                            </span>
                          )}
                        </div>
                        <p className="mt-3 font-display text-lg font-bold leading-7 text-ink">{q}</p>
                        {!reto.data && (
                          <p className="mt-3 text-sm leading-6 text-muted">
                            {preguntasFallback[i]?.intencion}
                          </p>
                        )}
                      </div>
                    ))}
                  </div>

                  {reto.data?.reasoning_trace && (
                    <p className="mt-4 rounded-xl border border-border bg-cream p-4 text-xs italic leading-5 text-muted">
                      Trace del razonamiento: {reto.data.reasoning_trace}
                    </p>
                  )}
                </div>

                <div className="space-y-4">
                  <div className="rounded-[16px] border border-border bg-cream p-5 text-sm leading-6 text-muted">
                    <strong className="mb-2 block text-ink">¿Qué pasa al enviar?</strong>
                    <ol className="list-decimal space-y-1.5 pl-4">
                      <li>El webhook n8n valida el secreto y tu decisión.</li>
                      <li>OpenAI (gpt-4o-mini) genera 3 preguntas de socio exigente.</li>
                      <li>La decisión queda auditada en la tabla <code>decisiones</code>.</li>
                      <li>Es el mismo tool que usa el agente de voz en la llamada.</li>
                    </ol>
                  </div>
                  {selectedMatch && (
                    <div className="rounded-[16px] border border-border bg-cream p-5 text-sm text-muted">
                      <span className="micro-label">Contexto enviado</span>
                      <p className="mt-2 font-semibold text-ink">{selectedMatch.titulo}</p>
                      <p className="mt-1">
                        {selectedMatch.institucion} · {formatCurrency(selectedMatch.monto)}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* ── DOCUMENTOS: generar_documento real (plantillas DINAC) ── */}
            {activeTab === "documentos" && (
              <div className="grid gap-6 lg:grid-cols-[320px_1fr]">
                <div className="space-y-4">
                  <div>
                    <span className="micro-label">Tipo de documento DINAC</span>
                    <select
                      className="mt-2 w-full rounded-[14px] border border-border bg-cream p-3.5 text-sm font-semibold text-ink focus:outline-none focus-visible:ring-2 focus-visible:ring-red/30"
                      onChange={(e) => setTipoDoc(e.target.value)}
                      value={tipoDoc}
                    >
                      {TIPOS_DOCUMENTO.map((t) => (
                        <option key={t.value} value={t.value}>
                          {t.label}
                        </option>
                      ))}
                    </select>
                  </div>
                  <button
                    className="pressable w-full rounded-full bg-red py-3 text-sm font-semibold text-paper shadow-red-soft transition hover:bg-red-dark disabled:opacity-40"
                    disabled={doc.loading}
                    onClick={pedirDocumento}
                    type="button"
                  >
                    {doc.loading ? "Prellenando borrador…" : "Generar borrador"}
                  </button>
                  <div className="rounded-[16px] border border-border bg-cream p-5 text-sm leading-6 text-muted">
                    <strong className="mb-2 block text-ink">Cómo funciona</strong>
                    El webhook busca el perfil del productor y la plantilla oficial en Supabase,
                    valida qué campos faltan y prellena un borrador. Nunca firma ni presenta:
                    el productor siempre revisa y firma por su cuenta.
                  </div>
                </div>

                <div>
                  {doc.error && (
                    <p className="text-sm text-red">Error del backend ({doc.error}).</p>
                  )}
                  {!doc.data && !doc.error && (
                    <div className="flex h-48 items-center justify-center rounded-[16px] border border-dashed border-border text-sm text-muted">
                      Elegí un tipo de documento y generá el borrador con datos reales de la DB.
                    </div>
                  )}
                  {doc.data?.estado === "borrador" && (
                    <div className="rounded-[16px] border border-border bg-cream p-6">
                      <div className="flex flex-wrap items-center gap-3">
                        <Badge variant="green">BORRADOR</Badge>
                        <span className="text-xs font-bold text-muted">{doc.data.archivo_nombre}</span>
                      </div>
                      <div className="mt-5 grid gap-3 sm:grid-cols-2">
                        {Object.entries(doc.data.datos_usados ?? {}).map(([campo, valor]) => (
                          <div className="rounded-xl border border-border bg-paper p-3" key={campo}>
                            <span className="micro-label">{campo.replaceAll("_", " ")}</span>
                            <strong className="mt-1 block break-words text-sm">{valor || "—"}</strong>
                          </div>
                        ))}
                      </div>
                      <p className="mt-5 text-xs leading-5 text-muted">{doc.data.mensaje}</p>
                    </div>
                  )}
                  {doc.data?.estado === "incompleto" && (
                    <div className="rounded-[16px] border border-border bg-cream p-6">
                      <Badge variant="neutral">FALTAN DATOS</Badge>
                      <p className="mt-3 text-sm leading-6 text-ink">{doc.data.mensaje}</p>
                      <div className="mt-4 flex flex-wrap gap-2">
                        {(doc.data.campos_faltantes ?? []).map((c) => (
                          <span
                            className="rounded-full bg-paper px-3 py-1.5 text-xs font-bold text-muted"
                            key={c}
                          >
                            {c.replaceAll("_", " ")}
                          </span>
                        ))}
                      </div>
                      <p className="mt-4 text-xs leading-5 text-muted">
                        En una llamada real, Compa pregunta estos datos por voz antes de generar el
                        borrador.
                      </p>
                    </div>
                  )}
                  {doc.data?.estado === "error" && (
                    <p className="text-sm text-red">{doc.data.mensaje}</p>
                  )}
                </div>
              </div>
            )}

            {/* ── VOZ: agente ElevenLabs real ── */}
            {activeTab === "voz" && (
              <div className="grid gap-6 lg:grid-cols-[1fr_320px]">
                <div>
                  <span className="micro-label">Así abre Compa la llamada</span>
                  <div className="mt-2 rounded-[16px] border border-border bg-cream p-5 text-lg leading-8 text-ink">
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
                  <div className="mt-4 grid gap-3 sm:grid-cols-3">
                    {[
                      ["Detecta", "n8n cruza tu rubro con COMPRASAL y arma la llamada"],
                      ["Conversa", "ElevenLabs habla en salvadoreño con voseo y te reta"],
                      ["Ejecuta", "Los tools llaman a n8n: retar decisión y generar documento"],
                    ].map(([t, d]) => (
                      <div className="rounded-xl border border-border bg-cream p-4" key={t}>
                        <strong className="block font-display text-sm text-ink">{t}</strong>
                        <span className="mt-1 block text-xs leading-5 text-muted">{d}</span>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-4">
                  <div className="rounded-[16px] border-2 border-red/20 bg-red/5 p-5">
                    <strong className="block font-display text-base text-ink">
                      Hablá con Compa ahora
                    </strong>
                    <p className="mt-2 text-sm leading-6 text-muted">
                      El botón <strong className="text-ink">“Start a call”</strong> (abajo a la
                      derecha) te conecta con el agente real: mismo prompt, mismos tools de n8n y
                      Knowledge Base legal de DINAC.
                    </p>
                    <p className="mt-3 text-xs leading-5 text-muted">
                      Probá: “¿Desde qué monto aplica licitación competitiva?” o contale una
                      decisión de negocio.
                    </p>
                  </div>
                  <div className="rounded-[16px] border border-border bg-cream p-5 text-sm leading-6 text-muted">
                    <strong className="mb-1 block text-ink">Variables dinámicas</strong>
                    En una llamada saliente, n8n inyecta nombre, rubro y la oportunidad detectada —
                    el guion de la izquierda se arma solo con esos datos.
                  </div>
                </div>
              </div>
            )}

            {/* ── PROVEEDORES (perfiles sintéticos Nemotron) ── */}
            {activeTab === "proveedores" && (
              <div className="grid gap-4 sm:grid-cols-2">
                {suppliers.length > 0 ? (
                  suppliers.map((s) => (
                    <div key={s.id} className="rounded-[16px] border border-border bg-cream p-5">
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
