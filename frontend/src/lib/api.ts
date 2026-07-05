// Cliente del backend real de Compa (webhooks n8n -> Supabase / OpenAI / ElevenLabs)

export const API_BASE =
  process.env.NEXT_PUBLIC_COMPA_API || "https://wilbe.app.n8n.cloud/webhook";

export const WEBHOOK_SECRET = "whsec_compa_buildathon_2026";
export const ELEVENLABS_AGENT_ID = "agent_9801kwr61ctre7x8c944ze53p95w";

// Perfil demo real en Supabase (Vilma) — los demas perfiles del demo usan
// estos UUIDs para que retar_decision / generar_documento escriban en la DB real.
export const DEMO_PRODUCTOR_ID = "f5c952f0-a0b7-4a2e-a752-ddb373e04411";
export const DEMO_OPORTUNIDAD_ID = "e173f2d6-26d9-46be-9f41-238978889572";

export type OportunidadLive = {
  id: string;
  titulo: string;
  institucion: string;
  monto: number;
  fecha_cierre: string;
  rubro_requerido: string;
  tipo_contratacion: string;
};

export type FeedResponse = {
  oportunidades: OportunidadLive[];
  total: number;
  actualizado_en: string;
};

export type RetarResponse = {
  preguntas: string[];
  reasoning_trace: string;
  _fallback: boolean;
  conversation_id: string;
};

export type GenerarDocumentoResponse = {
  estado: "borrador" | "incompleto" | "error";
  mensaje?: string;
  tipo_documento?: string;
  campos_faltantes?: string[];
  datos_usados?: Record<string, string>;
  archivo_nombre?: string;
  archivo_url?: string;
  error?: string;
};

export const TIPOS_DOCUMENTO = [
  { value: "declaracion_jurada_persona_natural", label: "Declaración jurada — Persona natural" },
  { value: "declaracion_jurada_apoderado_persona_natural", label: "Declaración jurada — Apoderado (natural)" },
  { value: "declaracion_jurada_persona_juridica", label: "Declaración jurada — Persona jurídica" },
  { value: "declaracion_jurada_apoderado_persona_juridica", label: "Declaración jurada — Apoderado (jurídica)" },
  { value: "carta_compromiso", label: "Carta compromiso" },
  { value: "desglose_precios", label: "Desglose de precios" },
  { value: "documento_estandar_contratacion_directa", label: "Doc. estándar — Contratación directa" },
  { value: "documento_estandar_comparacion_precios_bienes_servicios", label: "Doc. estándar — Comparación de precios" },
] as const;

export async function getOportunidadesFeed(): Promise<FeedResponse> {
  const r = await fetch(`${API_BASE}/oportunidades-feed`, { cache: "no-store" });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function retarDecision(input: {
  decision: string;
  nombreProductor: string;
  rubro: string;
  capacidad?: string;
  oportunidadTitulo?: string;
  oportunidadInstitucion?: string;
  oportunidadMonto?: number;
}): Promise<RetarResponse> {
  const r = await fetch(`${API_BASE}/retar-decision`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Compa-Webhook-Secret": WEBHOOK_SECRET,
    },
    body: JSON.stringify({
      decision_descrita: input.decision,
      productor_id: DEMO_PRODUCTOR_ID,
      oportunidad_id: DEMO_OPORTUNIDAD_ID,
      nombre_productor: input.nombreProductor,
      rubro_negocio: input.rubro,
      capacidad_productor: input.capacidad || "no especificada",
      oportunidad_titulo: input.oportunidadTitulo || "Oportunidad publica",
      oportunidad_institucion: input.oportunidadInstitucion || "Institucion publica",
      oportunidad_monto: input.oportunidadMonto || 0,
      conversation_id: `web_${Date.now()}`,
    }),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}

export async function generarDocumento(input: {
  tipoDocumento: string;
  datosAdicionales?: Record<string, string>;
}): Promise<GenerarDocumentoResponse> {
  const r = await fetch(`${API_BASE}/generar-documento-dinac`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Compa-Webhook-Secret": WEBHOOK_SECRET,
    },
    body: JSON.stringify({
      productor_id: DEMO_PRODUCTOR_ID,
      tipo_documento: input.tipoDocumento,
      datos_adicionales: {
        fecha: new Date().toISOString().slice(0, 10),
        ...input.datosAdicionales,
      },
    }),
  });
  if (!r.ok) throw new Error(`HTTP ${r.status}`);
  return r.json();
}
