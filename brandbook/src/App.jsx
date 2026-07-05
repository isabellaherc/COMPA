import { useState } from "react";
import "./App.css";

function luminance(hex) {
  const c = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map((i) => parseInt(c.slice(i, i + 2), 16) / 255);
  const lin = (v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4);
  return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b);
}

function contrast(hexA, hexB) {
  const lA = luminance(hexA) + 0.05;
  const lB = luminance(hexB) + 0.05;
  return lA > lB ? lA / lB : lB / lA;
}

function contrastTag(ratio) {
  if (ratio >= 4.5) return { label: "AA texto", cls: "pass" };
  if (ratio >= 3) return { label: "AA grande", cls: "large" };
  return { label: "No apto texto", cls: "fail" };
}

const COLORS = [
  {
    name: "Rojo Árbol de Fuego",
    hex: "#C1272D",
    role: "Primario",
    usage: "Las flores encendidas del Árbol de Fuego. Acciones principales, enlaces, encabezados y marca.",
  },
  {
    name: "Verde Follaje",
    hex: "#2E5339",
    role: "Secundario",
    usage: "El follaje que sostiene la copa. Fondos oscuros, superficies de contraste, footer.",
  },
  {
    name: "Rosa Maquilishuat",
    hex: "#FFC5D3",
    role: "Acento",
    usage: "Las flores del Maquilishuat cayendo entre el verde. Fondos suaves, tarjetas, etiquetas.",
  },
  {
    name: "Rosa Profundo",
    hex: "#FF6F91",
    role: "Acento énfasis",
    usage: "El Maquilishuat en su tono más intenso. Botones e insignias que deben resaltar — el protagonista.",
  },
];

const PAGE_STEPS = [
  {
    title: "Barra de navegación",
    surface: "Marfil translúcido, sticky",
    hex: "#F6ECDD",
    detail:
      "Logo + máximo 4 enlaces + un botón outline. Nunca un botón sólido acá — se guarda para el hero.",
  },
  {
    title: "Hero",
    surface: "Marfil + hojas cayendo de fondo",
    hex: "#C1272D",
    detail:
      "Un titular, un subtítulo, un botón primario rojo + uno outline. Nunca dos botones sólidos compitiendo.",
  },
  {
    title: "Contenido / prueba",
    surface: "Marfil, tarjetas claras",
    hex: "#FFC5D3",
    detail:
      "Grilla de tarjetas o features. Un solo color de ícono por tarjeta — no mezclar rojo y rosa profundo en la misma.",
  },
  {
    title: "Sección de énfasis",
    surface: "Marfil, un acento puntual",
    hex: "#FF6F91",
    detail:
      "Rosa profundo para UNA sola acción o insignia destacada por scroll — es el tono que más llama, se raciona.",
  },
  {
    title: "CTA final",
    surface: "Verde follaje oscuro",
    hex: "#2E5339",
    detail:
      "Único fondo oscuro del recorrido además del footer. Botón rosa profundo + uno outline claro.",
  },
  {
    title: "Footer",
    surface: "Verde follaje, misma superficie que el CTA",
    hex: "#16241B",
    detail: "Continúa el verde sin borde duro contra el CTA — misma superficie, sensación de cierre.",
  },
];

function AnatomyStep({ step, index, total }) {
  const textColor = luminance(step.hex) > 0.55 ? "#241512" : "#FFFBF3";
  return (
    <div className="anatomy-step">
      <div className="anatomy-num-col">
        <div className="anatomy-num" style={{ background: step.hex, color: textColor }}>
          {index + 1}
        </div>
        {index < total - 1 && <div className="anatomy-line" />}
      </div>
      <div className="anatomy-body">
        <div className="anatomy-title-row">
          <span className="anatomy-title">{step.title}</span>
          <span className="anatomy-bg-tag">{step.surface}</span>
        </div>
        <p className="anatomy-detail">{step.detail}</p>
      </div>
    </div>
  );
}

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

function ColorCard({ c }) {
  const [copied, setCopied] = useState(false);
  const copy = () => {
    navigator.clipboard?.writeText(c.hex);
    setCopied(true);
    setTimeout(() => setCopied(false), 1200);
  };
  return (
    <div className="color-card">
      <div className="color-swatch" style={{ background: c.hex }} />
      <div className="color-card-body">
        <div className="role">{c.role}</div>
        <div className="name">{c.name}</div>
        <button className="hex" onClick={copy} type="button">
          {c.hex} {copied ? "· copiado" : "· copiar"}
        </button>
        <p className="usage">{c.usage}</p>
        <div className="contrast-row">
          {["#FFFBF3", "#241512"].map((bg) => {
            const ratio = contrast(c.hex, bg);
            const tag = contrastTag(ratio);
            return (
              <span className={`contrast-tag ${tag.cls}`} key={bg}>
                {tag.label} sobre {bg === "#FFFBF3" ? "marfil" : "tinta"} ({ratio.toFixed(1)}:1)
              </span>
            );
          })}
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <div className="page">
      <FallingCanopy count={16} />
      <header className="nav">
        <div className="wrap nav-inner">
          <div className="brand">
            <Mark className="brand-mark" />
            Brandbook
          </div>
          <nav className="nav-links">
            <a href="#colores">Colores</a>
            <a href="#tipografia">Tipografía</a>
            <a href="#componentes">Componentes</a>
            <a href="#armado">Armar la página</a>
          </nav>
          <div className="nav-cta">
            <a href="#componentes" className="btn btn-outline btn-sm">
              Ver componentes
            </a>
          </div>
        </div>
      </header>

      <main>
        {/* HERO */}
        <section className="hero">
          <div className="wrap hero-inner">
            <div className="eyebrow">Guía de marca · v1.0</div>
            <h1>
              Un sistema visual inspirado en <span className="accent">los bosques de El Salvador</span>
            </h1>
            <p className="lead">
              Rojo del Árbol de Fuego en flor, verde del follaje y el rosa del Maquilishuat,
              protagonista, cayendo entre las hojas — cuatro colores, roles claros, aplicación
              consistente en cada superficie.
            </p>
            <div className="hero-actions">
              <a href="#colores" className="btn btn-primary">
                Ver la paleta
              </a>
              <a href="#componentes" className="btn btn-outline">
                Ver componentes
              </a>
            </div>
            <p className="hero-note">4 colores base · 2 tipografías · un sistema de componentes</p>
            <div className="hero-swatch-row">
              <span className="mini-swatch" style={{ background: "#C1272D" }} />
              <span className="mini-swatch" style={{ background: "#2E5339" }} />
              <span className="mini-swatch" style={{ background: "#FFC5D3" }} />
              <span className="mini-swatch" style={{ background: "#FF6F91" }} />
            </div>
          </div>
        </section>

        {/* COLORES */}
        <section id="colores">
          <div className="wrap">
            <div className="section-head">
              <div className="eyebrow">Paleta</div>
              <h2>Cuatro colores, del Árbol de Fuego y el Maquilishuat</h2>
              <p>
                Rojo de las flores encendidas, verde del follaje y dos tonos del Maquilishuat
                — el rosa protagoniza la paleta, nunca los cuatro compitiendo a la vez.
              </p>
            </div>
            <div className="color-grid">
              {COLORS.map((c) => (
                <ColorCard c={c} key={c.hex} />
              ))}
            </div>
          </div>
        </section>

        {/* TIPOGRAFÍA */}
        <section id="tipografia">
          <div className="wrap">
            <div className="section-head">
              <div className="eyebrow">Tipografía</div>
              <h2>Space Grotesk para títulos, Inter para lectura</h2>
              <p>
                Una tipografía geométrica le da personalidad a los títulos; una fuente neutra
                mantiene el contenido largo fácil de leer.
              </p>
            </div>

            <div className="font-pair-grid">
              <div className="font-pair-card display">
                <div className="role">Títulos — Space Grotesk</div>
                <div className="big">Aa Bb Cc 123</div>
                <p className="note">Titulares, etiquetas, botones, UI.</p>
              </div>
              <div className="font-pair-card body">
                <div className="role">Cuerpo — Inter</div>
                <div className="big">Aa Bb Cc 123</div>
                <p className="note">Párrafos, campos de formulario, notas.</p>
              </div>
            </div>

            <div className="type-scale" style={{ marginTop: 40 }}>
              <div className="type-row">
                <div className="meta">
                  Display
                  <span>64 / 700</span>
                </div>
                <div className="sample" style={{ fontSize: 56, fontWeight: 700 }}>
                  Copas en flor
                </div>
              </div>
              <div className="type-row">
                <div className="meta">
                  Título 1
                  <span>40 / 700</span>
                </div>
                <div className="sample" style={{ fontSize: 40, fontWeight: 700 }}>
                  Construido para ser consistente
                </div>
              </div>
              <div className="type-row">
                <div className="meta">
                  Título 2
                  <span>28 / 700</span>
                </div>
                <div className="sample" style={{ fontSize: 28, fontWeight: 700 }}>
                  Títulos de sección claros
                </div>
              </div>
              <div className="type-row">
                <div className="meta">
                  Título 3
                  <span>20 / 600</span>
                </div>
                <div className="sample" style={{ fontSize: 20, fontWeight: 600 }}>
                  Etiquetas de componentes y tarjetas
                </div>
              </div>
              <div className="type-row">
                <div className="meta">
                  Cuerpo
                  <span>16 / 400</span>
                </div>
                <div className="sample" style={{ fontFamily: "var(--font-body)", fontSize: 16, fontWeight: 400 }}>
                  El texto de párrafo va a 16px con interlineado de 1.6 para una lectura cómoda.
                </div>
              </div>
              <div className="type-row">
                <div className="meta">
                  Nota
                  <span>13 / 600</span>
                </div>
                <div
                  className="sample"
                  style={{
                    fontFamily: "var(--font-body)",
                    fontSize: 13,
                    fontWeight: 600,
                    textTransform: "uppercase",
                    letterSpacing: "0.05em",
                    color: "var(--color-muted)",
                  }}
                >
                  Etiquetas y metadatos
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* COMPONENTES */}
        <section id="componentes">
          <div className="wrap">
            <div className="section-head">
              <div className="eyebrow">Componentes</div>
              <h2>Construidos desde la paleta</h2>
              <p>Botones, insignias, tarjetas y campos — todos derivados de los mismos cuatro colores.</p>
            </div>

            <div className="comp-block">
              <h3>Botones</h3>
              <div className="comp-panel">
                <button className="btn btn-primary" type="button">
                  Acción primaria
                </button>
                <button className="btn btn-pink" type="button">
                  Destacado rosa
                </button>
                <button className="btn btn-outline" type="button">
                  Secundario
                </button>
                <button className="btn btn-ghost" type="button">
                  Ghost
                </button>
                <button className="btn btn-disabled" type="button" disabled>
                  Deshabilitado
                </button>
              </div>
            </div>

            <div className="comp-block">
              <h3>Insignias</h3>
              <div className="comp-panel">
                <span className="badge badge-red">
                  <span className="badge-dot" /> En progreso
                </span>
                <span className="badge badge-pink-deep">
                  <span className="badge-dot" /> Destacado
                </span>
                <span className="badge badge-pink">
                  <span className="badge-dot" /> Nuevo
                </span>
                <span className="badge badge-neutral">
                  <span className="badge-dot" /> Archivado
                </span>
              </div>
            </div>

            <div className="comp-block">
              <h3>Tarjetas</h3>
              <div className="card-grid">
                <div className="ui-card">
                  <div className="icon" style={{ background: "var(--color-red)" }}>
                    A
                  </div>
                  <h4>Tarjeta roja</h4>
                  <p>Ícono rojo para la variante por defecto, de mayor énfasis.</p>
                </div>
                <div className="ui-card">
                  <div className="icon" style={{ background: "var(--color-green)" }}>
                    B
                  </div>
                  <h4>Tarjeta verde</h4>
                  <p>Follaje como base sobria para contenido informativo o de fondo.</p>
                </div>
                <div className="ui-card">
                  <div className="icon" style={{ background: "var(--color-pink)" }}>
                    C
                  </div>
                  <h4>Tarjeta rosa suave</h4>
                  <p>Acento suave para contenido secundario o de apoyo, más ligero.</p>
                </div>
                <div className="ui-card">
                  <div className="icon" style={{ background: "var(--color-pink-deep)" }}>
                    D
                  </div>
                  <h4>Tarjeta rosa profundo</h4>
                  <p>El tono protagonista — para lo que necesita máximo énfasis.</p>
                </div>
              </div>
            </div>

            <div className="comp-block">
              <h3>Campos de formulario</h3>
              <div className="comp-panel">
                <div className="field-row" style={{ width: "100%" }}>
                  <div className="field">
                    <label>Nombre completo</label>
                    <input placeholder="María Hernández" />
                  </div>
                  <div className="field">
                    <label>Correo</label>
                    <input placeholder="maria@empresa.com" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* GUÍA DE ARMADO */}
        <section id="armado">
          <div className="wrap">
            <div className="section-head">
              <div className="eyebrow">Guía de construcción</div>
              <h2>Cómo armar la página completa</h2>
              <p>
                La página es un orden fijo de secciones, no un catálogo suelto de piezas. Seguí
                esta secuencia de arriba a abajo para que cualquier página nueva se sienta parte
                del mismo sistema.
              </p>
            </div>

            <div className="anatomy">
              {PAGE_STEPS.map((step, i) => (
                <AnatomyStep step={step} index={i} total={PAGE_STEPS.length} key={step.title} />
              ))}
            </div>

            <div className="rules-grid">
              <div className="rules-col do">
                <h4>Hacé esto</h4>
                <ul>
                  <li>Un solo botón sólido (rojo o rosa profundo) por sección.</li>
                  <li>Alterná marfil y superficie clara entre secciones, sin bordes duros.</li>
                  <li>Un h1 por página; los h2 marcan cada sección, nunca saltés a h4 directo.</li>
                  <li>108px de aire vertical entre secciones en escritorio, 72px en mobile.</li>
                </ul>
              </div>
              <div className="rules-col dont">
                <h4>Evitá esto</h4>
                <ul>
                  <li>Dos fondos verde oscuro seguidos — satura el cierre de la página.</li>
                  <li>Rosa profundo en más de una acción por scroll — deja de ser énfasis.</li>
                  <li>Mezclar rojo y rosa profundo en el mismo botón o insignia.</li>
                  <li>Hojas cayendo dentro de tarjetas o formularios — solo en el fondo general.</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* CTA OSCURO */}
        <section className="cta-dark">
          <div className="wrap cta-dark-inner">
            <div className="eyebrow on-dark">Consistencia ante todo</div>
            <h2>Aplica el sistema de la misma forma, en todas partes</h2>
            <p>
              Misma paleta, misma tipografía, mismos componentes — en el sitio, en el producto
              y en cada presentación.
            </p>
            <div className="cta-dark-actions">
              <a href="#colores" className="btn btn-pink">
                Volver a la paleta
              </a>
              <a href="#tipografia" className="btn btn-outline on-dark">
                Volver a tipografía
              </a>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div className="wrap footer-inner">
          <div className="brand">
            <Mark className="brand-mark" />
            Brandbook
          </div>
          <div className="footer-links">
            <a href="#colores">Colores</a>
            <a href="#tipografia">Tipografía</a>
            <a href="#componentes">Componentes</a>
          </div>
          <div>© 2026 Brandbook. Referencia interna de marca.</div>
        </div>
      </footer>
    </div>
  );
}

export default App;
