import { useEffect, useState } from "react";
import "./App.css";

// ---------- Backend (n8n webhooks) ----------
const API_BASE = import.meta.env.VITE_COMPA_API || "https://wilbe.app.n8n.cloud/webhook";
const WEBHOOK_SECRET = "whsec_compa_buildathon_2026";
const ELEVENLABS_AGENT_ID = "agent_9801kwr61ctre7x8c944ze53p95w";
// Demo: Vilma (productora real en Supabase) y su oportunidad top
const DEMO_PRODUCTOR_ID = "f5c952f0-a0b7-4a2e-a752-ddb373e04411";
const DEMO_OPORTUNIDAD_ID = "e173f2d6-26d9-46be-9f41-238978889572";

const fmtMonto = (m) =>
  Number(m || 0).toLocaleString("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 0 });

const TIPO_LABEL = { LP: "Licitación Pública", LG: "Libre Gestión", CD: "Contratación Directa" };

// ---------- Brand Mark (5-petal flower) ----------
function Mark({ className }) {
  return (
    <svg viewBox="0 0 32 32" className={className} aria-hidden="true">
      {[0, 72, 144, 216, 288].map((deg, i) => (
        <ellipse
          key={deg}
          cx="16"
          cy="7.5"
          rx="5.4"
          ry="8"
          fill={i % 2 === 0 ? "#C1272D" : "#FFC5D3"}
          transform={`rotate(${deg} 16 16)`}
        />
      ))}
      <circle cx="16" cy="16" r="4" fill="#FF6F91" />
    </svg>
  );
}

// ---------- Leaf + Falling Canopy ----------
function Leaf({ color }) {
  return (
    <svg viewBox="0 0 20 24" aria-hidden="true">
      <path d="M10 0C15 6 20 11 10 24C0 11 5 6 10 0Z" fill={color} />
    </svg>
  );
}

const LEAF_COLORS = ["#FFC5D3", "#FF6F91", "#C1272D"];

function FallingCanopy({ count = 16 }) {
  const leaves = Array.from({ length: count }, (_, i) => ({
    left: `${(i * 61) % 100}%`,
    duration: 16 + (i % 6) * 3,
    delay: -((i * 2.3) % 20).toFixed(1),
    size: 10 + (i % 4) * 5,
    color: LEAF_COLORS[i % LEAF_COLORS.length],
    sway: (i % 2 === 0 ? 1 : -1) * (24 + (i % 3) * 14),
  }));
  return (
    <div className="canopy" aria-hidden="true">
      {leaves.map((l, i) => (
        <span
          key={i}
          className="leaf"
          style={{
            left: l.left,
            width: l.size,
            height: l.size * 1.2,
            animationDuration: `${l.duration}s`,
            animationDelay: `${l.delay}s`,
            "--sway": `${l.sway}px`,
          }}
        >
          <Leaf color={l.color} />
        </span>
      ))}
    </div>
  );
}

// ---------- Opportunity card data ----------
const OPORTUNIDADES = [
  {
    icon: "🔍",
    color: "#C1272D",
    title: "Detección automática",
    description:
      "Compa revisa COMPRASAL cada 6 horas. Encuentra las licitaciones que hacen match con el rubro de tu negocio — sin buscar manualmente.",
  },
  {
    icon: "📞",
    color: "#FF6F91",
    title: "Te llama y te explica",
    description:
      "Recibís una llamada de Compa contándote la oportunidad en lenguaje simple. Como un socio que te avisa, no como un sistema de alertas.",
  },
  {
    icon: "✅",
    color: "#2E5339",
    title: "Match por rubro real",
    description:
      "Solo oportunidades de tu rubro. Compa usa tu perfil de negocio para filtrar lo que realmente te sirve. Nada de ruido.",
  },
];

const COMO_FUNCIONA = [
  {
    step: "1",
    color: "#C1272D",
    title: "n8n orquesta todo",
    description:
      "Los flujos automatizados conectan COMPRASAL, tu perfil y los datos. Detección, match y disparo de llamadas — 100% automatizado.",
    detail: "Workflows cada 6 horas o bajo demanda. Sin intervención manual.",
  },
  {
    step: "2",
    color: "#FF6F91",
    title: "ElevenLabs te llama",
    description:
      "El agente conversacional con voz de Luis — cercano, directo, en vos salvadoreño. Te explica la oportunidad y escucha tu respuesta.",
    detail: "Llamada outbound con variables dinámicas. Voz consistente, mismo personaje siempre.",
  },
  {
    step: "3",
    color: "#2E5339",
    title: "Supabase guarda tu perfil",
    description:
      "Tu información de negocio, tus decisiones y tu historial viven en una base de datos PostgreSQL. Rápida, segura, siempre disponible.",
    detail: "Perfiles con rubro, ubicación, capacidad. Datos de COMPRASAL cacheados para respuesta instantánea.",
  },
];

// ---------- Oportunidades en vivo (Supabase via n8n) ----------
function OportunidadesLive() {
  const [state, setState] = useState({ loading: true, error: null, items: [] });

  useEffect(() => {
    fetch(`${API_BASE}/oportunidades-feed`, { cache: "no-store" })
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then((data) =>
        setState({ loading: false, error: null, items: data.oportunidades || [] })
      )
      .catch((e) => setState({ loading: false, error: e.message, items: [] }));
  }, []);

  return (
    <section id="en-vivo" style={{ background: "var(--color-surface)" }}>
      <div className="wrap">
        <div className="section-head">
          <div className="eyebrow">En vivo</div>
          <h2>Oportunidades abiertas ahora en COMPRASAL</h2>
          <p>
            Datos reales desde la base de Compa — las mismas licitaciones que el agente
            usa para llamar a los productores.
          </p>
        </div>

        {state.loading && <p className="live-status">Cargando oportunidades…</p>}
        {state.error && (
          <p className="live-status">
            No se pudo cargar el feed ({state.error}). Probá de nuevo en un rato.
          </p>
        )}

        <div className="live-grid">
          {state.items.map((op) => (
            <div className="live-card" key={op.id}>
              <div className="live-card-top">
                <span className="live-tipo">{TIPO_LABEL[op.tipo_contratacion] || op.tipo_contratacion}</span>
                <span className="live-monto">{fmtMonto(op.monto)}</span>
              </div>
              <h4>{op.titulo}</h4>
              <p className="live-inst">{op.institucion}</p>
              <div className="live-card-foot">
                <span className="live-rubro">{op.rubro_requerido}</span>
                <span className="live-cierre">Cierra {op.fecha_cierre}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

// ---------- Retá tu decisión (OpenAI via n8n) ----------
function RetaTuDecision() {
  const [decision, setDecision] = useState("");
  const [state, setState] = useState({ loading: false, error: null, data: null });

  const submit = async (e) => {
    e.preventDefault();
    if (decision.trim().length < 10 || state.loading) return;
    setState({ loading: true, error: null, data: null });
    try {
      const r = await fetch(`${API_BASE}/retar-decision`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Compa-Webhook-Secret": WEBHOOK_SECRET,
        },
        body: JSON.stringify({
          decision_descrita: decision.trim(),
          productor_id: DEMO_PRODUCTOR_ID,
          oportunidad_id: DEMO_OPORTUNIDAD_ID,
          nombre_productor: "Vilma Jeanneth Guardado de Ayala",
          rubro_negocio: "Alimentos y Bebidas",
          conversation_id: `web_${Date.now()}`,
        }),
      });
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const data = await r.json();
      setState({ loading: false, error: null, data });
    } catch (err) {
      setState({ loading: false, error: err.message, data: null });
    }
  };

  return (
    <div className="reto-box">
      <h3>Probalo vos: contale una decisión a Compa</h3>
      <p className="reto-sub">
        Escribí una decisión de negocio que estés evaluando. Compa te devuelve las 3
        preguntas que un socio de verdad te haría — generadas en vivo por el mismo
        backend que usa el agente de voz.
      </p>
      <form onSubmit={submit} className="reto-form">
        <textarea
          value={decision}
          onChange={(e) => setDecision(e.target.value)}
          placeholder='Ej: "Quiero comprar un camión refrigerado para ampliar mis entregas a San Salvador"'
          rows={3}
          maxLength={400}
        />
        <button
          type="submit"
          className="btn btn-primary"
          disabled={decision.trim().length < 10 || state.loading}
        >
          {state.loading ? "Compa está pensando…" : "Que Compa me rete"}
        </button>
      </form>

      {state.error && (
        <p className="live-status">Error consultando a Compa ({state.error}).</p>
      )}

      {state.data && (
        <div className="reto-result">
          {(state.data.preguntas || []).map((q, i) => (
            <div className="reto-pregunta" key={i}>
              <span className="reto-num">{i + 1}</span>
              <p>{q}</p>
            </div>
          ))}
          {state.data.reasoning_trace && (
            <p className="reto-trace">{state.data.reasoning_trace}</p>
          )}
        </div>
      )}
    </div>
  );
}

// ---------- Widget de voz ElevenLabs ----------
function VoiceWidget() {
  useEffect(() => {
    if (document.querySelector('script[data-compa-convai]')) return;
    const s = document.createElement("script");
    s.src = "https://unpkg.com/@elevenlabs/convai-widget-embed";
    s.async = true;
    s.setAttribute("data-compa-convai", "1");
    document.body.appendChild(s);
  }, []);
  return <elevenlabs-convai agent-id={ELEVENLABS_AGENT_ID}></elevenlabs-convai>;
}

function StepCard({ item, index }) {
  return (
    <div className="step-card">
      <div className="step-num" style={{ background: item.color, color: "#FFFBF3" }}>
        {item.step}
      </div>
      <h3>{item.title}</h3>
      <p>{item.description}</p>
      <p className="step-detail">{item.detail}</p>
    </div>
  );
}

function App() {
  return (
    <div className="page">
      <FallingCanopy count={16} />

      {/* ---------- NAV ---------- */}
      <header className="nav">
        <div className="wrap nav-inner">
          <div className="brand">
            <Mark className="brand-mark" />
            Compa
          </div>
          <nav className="nav-links">
            <a href="#oportunidades">Oportunidades</a>
            <a href="#cofundador">Cofundador</a>
            <a href="#como-funciona">Cómo funciona</a>
          </nav>
          <div className="nav-cta">
            <a href="#cta" className="btn btn-outline btn-sm">
              Empezá hoy
            </a>
          </div>
        </div>
      </header>

      <main>
        {/* ---------- HERO ---------- */}
        <section className="hero">
          <div className="wrap hero-inner">
            <div className="eyebrow">Compa — Tu socio digital</div>
            <h1>
              Oportunidades de compras públicas,{" "}
              <span className="accent">directo a tu teléfono</span>
            </h1>
            <p className="lead">
              Compa detecta licitaciones en COMPRASAL que calzan con tu negocio, te llama
              por teléfono para explicártelas y te hace las preguntas difíciles que un buen
              socio haría antes de decidir. Pensado para MYPE y cooperativas salvadoreñas.
            </p>
            <div className="hero-actions">
              <a href="#oportunidades" className="btn btn-primary">
                Cómo funciona
              </a>
              <a href="#cofundador" className="btn btn-outline">
                Conocé al Cofundador
              </a>
            </div>
            <p className="hero-note">
              Sin instalar apps · Llamada directo a tu celular · Voz en español salvadoreño
            </p>
            <div className="hero-swatch-row">
              <span className="mini-swatch" style={{ background: "#C1272D" }} />
              <span className="mini-swatch" style={{ background: "#2E5339" }} />
              <span className="mini-swatch" style={{ background: "#FFC5D3" }} />
              <span className="mini-swatch" style={{ background: "#FF6F91" }} />
            </div>
          </div>
        </section>

        {/* ---------- OPORTUNIDADES ---------- */}
        <section id="oportunidades">
          <div className="wrap">
            <div className="section-head">
              <div className="eyebrow">Oportunidades</div>
              <h2>De COMPRASAL a tu oído, sin buscar</h2>
              <p>
                Compa cruza tu perfil de negocio con las licitaciones públicas de El Salvador
                y te avisa solo cuando hay algo que realmente te sirve.
              </p>
            </div>
            <div className="card-grid">
              {OPORTUNIDADES.map((op, i) => (
                <div className="ui-card" key={i}>
                  <div className="icon" style={{ background: op.color }}>
                    {op.icon}
                  </div>
                  <h4>{op.title}</h4>
                  <p>{op.description}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ---------- OPORTUNIDADES EN VIVO (Supabase via n8n) ---------- */}
        <OportunidadesLive />

        {/* ---------- COFUNDADOR ---------- */}
        <section id="cofundador" style={{ background: "var(--color-surface)" }}>
          <div className="wrap">
            <div className="section-head">
              <div className="eyebrow">Cofundador</div>
              <h2>Un socio que te hace las preguntas difíciles</h2>
              <p>
                Compa no es un asistente complaciente. Es un cofundador que te reta,
                te hace pensar y te ayuda a tomar mejores decisiones de negocio.
              </p>
            </div>

            <div className="cofounder-flow">
              <div className="cofounder-step">
                <div className="cofounder-icon" style={{ background: "#C1272D" }}>
                  <Mark className="brand-mark" style={{ width: 28, height: 28 }} />
                </div>
                <div className="cofounder-body">
                  <span className="badge badge-red">
                    <span className="badge-dot" /> Paso 1
                  </span>
                  <h4>Compa detecta una oportunidad</h4>
                  <p>
                    El workflow de n8n cruza tu rubro con COMPRASAL. Si hay match, dispara
                    una llamada a tu celular con ElevenLabs.
                  </p>
                </div>
              </div>

              <div className="cofounder-step">
                <div className="cofounder-icon" style={{ background: "#FF6F91" }}>
                  <span style={{ fontSize: 24 }}>📞</span>
                </div>
                <div className="cofounder-body">
                  <span className="badge badge-pink-deep">
                    <span className="badge-dot" /> Paso 2
                  </span>
                  <h4>Te llama y te explica la oportunidad</h4>
                  <p>
                    "Hola, soy Compa. Salió una licitación de alimentos para el ISSS que
                    calza con tu perfil. ¿La vemos ahora o después?"
                  </p>
                </div>
              </div>

              <div className="cofounder-step">
                <div className="cofounder-icon" style={{ background: "#2E5339" }}>
                  <span style={{ fontSize: 24 }}>💡</span>
                </div>
                <div className="cofounder-body">
                  <span className="badge badge-pink">
                    <span className="badge-dot" /> Paso 3
                  </span>
                  <h4>Te reta con 3 preguntas clave</h4>
                  <p>
                    Si describís tu decisión, Compa genera tres preguntas duras — las que un
                    socio real te haría. "¿Ya calculaste tu costo real de producción?"
                    "¿Tenés flujo de caja para aguantar 90 días sin cobrar?"
                  </p>
                </div>
              </div>
            </div>

            <RetaTuDecision />
          </div>
        </section>

        {/* ---------- CÓMO FUNCIONA ---------- */}
        <section id="como-funciona">
          <div className="wrap">
            <div className="section-head">
              <div className="eyebrow">Tecnología</div>
              <h2>Tres piezas que trabajan juntas</h2>
              <p>
                Compa corre sobre n8n, ElevenLabs y Supabase. Cada una hace una cosa
                y la hace bien — orquestadas para que el productor solo reciba una llamada.
              </p>
            </div>

            <div className="steps-grid">
              {COMO_FUNCIONA.map((item, i) => (
                <StepCard item={item} index={i} key={i} />
              ))}
            </div>
          </div>
        </section>

        {/* ---------- CTA OSCURO ---------- */}
        <section className="cta-dark" id="cta">
          <div className="wrap cta-dark-inner">
            <div className="eyebrow on-dark">Empezá hoy</div>
            <h2>Dejá que Compa te avise cuando hay oportunidad</h2>
            <p>
              Sin instalar apps. Sin registros complicados. Una llamada de teléfono
              cuando tu negocio tiene una oportunidad real en COMPRASAL.
            </p>
            <div className="cta-dark-actions">
              <a href="#oportunidades" className="btn btn-pink">
                Ver cómo funciona
              </a>
              <a href="mailto:compa@compa.sv" className="btn btn-outline on-dark">
                Contactanos
              </a>
            </div>
          </div>
        </section>
      </main>

      {/* ---------- FOOTER ---------- */}
      <footer className="footer">
        <div className="wrap footer-inner">
          <div className="brand">
            <Mark className="brand-mark" />
            Compa
          </div>
          <div className="footer-links">
            <a href="#oportunidades">Oportunidades</a>
            <a href="#cofundador">Cofundador</a>
            <a href="#como-funciona">Cómo funciona</a>
          </div>
          <div>© 2026 Compa — Hecho en El Salvador</div>
        </div>
      </footer>

      {/* ---------- Hablá con Compa (ElevenLabs ConvAI) ---------- */}
      <VoiceWidget />
    </div>
  );
}

export default App;
