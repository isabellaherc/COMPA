import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Marco legal",
  description:
    "Compa asiste, no representa. Conoce el marco regulatorio que guia cada recomendacion del asistente.",
};

const rules = [
  {
    code: "RN-001",
    title: "Perfil de negocio",
    desc: "Antes de recomendar, Compa verifica que el productor este activo en el rubro correspondiente.",
  },
  {
    code: "RN-005",
    title: "Referencia oficial",
    desc: "Toda explicacion incluye enlace o referencia verificable a la fuente original en COMPRASAL.",
  },
  {
    code: "RN-006",
    title: "No vinculante",
    desc: "Las recomendaciones son sugerencias. Compa no oferta, no firma, no adjudica ni modifica oportunidades.",
  },
  {
    code: "RN-009",
    title: "Consentimiento",
    desc: "Las llamadas solo se realizan con consentimiento previo del productor, verificable y revocable.",
  },
];

const docs = [
  { title: "LACAP", desc: "Ley de Adquisiciones y Contrataciones de la Administracion Publica. Regula todas las compras del Estado salvadoreno." },
  { title: "DINAC", desc: "Direccion Nacional de Compras Publicas. Ente rector que norma y supervisa las contrataciones publicas." },
  { title: "Codigo de Etica", desc: "Normas de conducta para funcionarios y oferentes en procesos de contratacion publica." },
  { title: "Lineamientos", desc: "Disposiciones tecnicas para la participacion de MYPE en compras publicas, incluyendo margen de preferencia." },
];

export default function LegalPage() {
  return (
    <div className="mx-auto w-full max-w-[1400px] px-5 pt-12 sm:px-8 sm:pt-16">
      <div className="mb-12">
        <div className="eyebrow">Marco legal</div>
        <h1 className="max-w-3xl font-display text-4xl font-bold leading-tight tracking-[-0.02em] text-ink sm:text-5xl">
          Asistencia, no representacion.
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-muted">
          Compa no oferta, no firma, no adjudica y no modifica oportunidades publicas. Toda
          recomendacion se presenta como sugerencia y conserva referencia a fuente oficial.
        </p>
      </div>

      {/* Business Rules */}
      <div className="mb-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {rules.map((rule) => (
          <div key={rule.code} className="card-lift rounded-[18px] border border-border bg-paper p-5">
            <strong className="font-display text-lg text-red">{rule.code}</strong>
            <h3 className="mt-3 font-display text-base font-bold text-ink">{rule.title}</h3>
            <p className="mt-2 text-sm leading-6 text-muted">{rule.desc}</p>
          </div>
        ))}
      </div>

      {/* Reference Docs */}
      <div className="pb-28">
        <div className="mb-8">
          <div className="eyebrow">Documentos de referencia</div>
          <h2 className="font-display text-3xl font-bold text-ink">Marco normativo que respalda a Compa</h2>
          <p className="mt-3 max-w-2xl text-base leading-7 text-muted">
            El asistente opera dentro del marco legal salvadoreno. Cada recomendacion respeta las
            normas de contratacion publica y los derechos del productor.
          </p>
        </div>
        <div className="grid gap-4 sm:grid-cols-2">
          {docs.map((doc) => (
            <div key={doc.title} className="card-lift rounded-[18px] border border-border bg-paper p-6">
              <h3 className="font-display text-lg font-bold text-red">{doc.title}</h3>
              <p className="mt-2 text-sm leading-6 text-muted">{doc.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
