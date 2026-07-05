# Brandbook — Guía de Marca
Inspirado en los bosques de El Salvador: el rojo del Árbol de Fuego en flor y el rosa del Maquilishuat cayendo entre el verde follaje.

## 1. Paleta

| Color | Hex | Rol | Uso |
|---|---|---|---|
| Rojo Árbol de Fuego | `#C1272D` | Primario | Acciones principales, enlaces, encabezados, marca |
| Verde Follaje | `#2E5339` | Secundario | Fondos oscuros, CTA final, footer |
| Rosa Maquilishuat | `#FFC5D3` | Acento | Fondos suaves, tarjetas, etiquetas secundarias |
| Rosa Profundo | `#FF6F91` | Acento énfasis | Un solo botón/insignia destacado por sección — el protagonista, se raciona |

Neutros (no son color de marca, son soporte):

| Token | Hex | Uso |
|---|---|---|
| Marfil (paper) | `#FFFBF3` | Tarjetas, inputs, superficie más clara |
| Marfil (cream) | `#F6ECDD` | Fondo de página |
| Superficie | `#F0E3CF` | Paneles (comp-panel, font-pair-card) |
| Borde | `#E4D5BD` | Bordes de tarjetas/inputs |
| Tinta | `#241512` | Texto |
| Verde oscuro (forest) | `#16241B` | Fondo CTA final y footer |
| Texto mudo | `#7A6A5D` | Texto secundario |

Sin azul, sin blanco puro, sin amarillo/ámbar, sin naranja — descartados a propósito en iteraciones previas.

### Contraste (WCAG, calculado en runtime con luminancia relativa)
- Rojo sobre marfil: **8.4:1** — AA texto. Rojo sobre tinta: 2.2:1 — no apto texto.
- Verde sobre marfil: **8.4:1** — AA texto. Verde sobre tinta: **2.0:1** — no apto.
- Rosa suave: falla como fondo de texto (muy claro) — úsalo como fondo, no como color de texto.
- Rosa profundo sobre marfil: AA grande (~3:1) — usar en botones grandes/negrita, no en texto corrido.

## 2. Tipografía

- **Display — Space Grotesk** (500/600/700): titulares, eyebrows, botones, UI.
- **Cuerpo — Inter** (400/500/600/700/800): párrafos, campos de formulario, notas.

Escala:

| Nivel | Tamaño / peso |
|---|---|
| Display | 64 / 700 |
| Título 1 | 40 / 700 |
| Título 2 | 28 / 700 |
| Título 3 | 20 / 600 |
| Cuerpo | 16 / 400, line-height 1.6 |
| Nota / eyebrow | 13 / 600, uppercase, letter-spacing 0.05em |

## 3. Elemento de firma

**Marca**: flor de 5 pétalos (rojo/rosa alternados) con centro rosa profundo — representa Maquilishuat + Árbol de Fuego a la vez.

**Hojas cayendo**: capa fija (`position: fixed`, `z-index: -1`) de 16 hojas SVG cayendo en loop infinito, colores `#FFC5D3 / #FF6F91 / #C1272D` (dos rosas por cada rojo — el rosa domina). Solo `transform` y `opacity` animados (GPU, sin layout thrashing), `prefers-reduced-motion` pausa la animación. Nunca dentro de tarjetas o formularios, solo en el fondo general de la página.

## 4. Componentes

- **Botones**: `primary` (rojo), `pink` (rosa profundo, un solo uso destacado por sección), `outline`, `ghost`, `disabled`. Radio 999px (pill), hover con lift de -1px.
- **Insignias**: `red`, `pink-deep`, `pink` (suave), `neutral` — punto de color + texto.
- **Tarjetas**: ícono de color sólido (40×40, radio 11px) + título + descripción. Un solo color de ícono por tarjeta.
- **Campos de formulario**: label uppercase mudo + input 44px alto, focus con borde rojo y halo `rgba(193,39,45,.15)`.

## 5. Cómo armar la página completa

Orden fijo de secciones, de arriba a abajo:

1. **Nav** — marfil translúcido, sticky. Logo + máx. 4 enlaces + un botón outline (nunca sólido acá).
2. **Hero** — marfil + hojas cayendo. Un titular, un botón primario rojo + uno outline.
3. **Contenido / prueba** — marfil, tarjetas claras. Un color de ícono por tarjeta.
4. **Sección de énfasis** — rosa profundo para una sola acción/insignia destacada por scroll.
5. **CTA final** — verde follaje oscuro. Único fondo oscuro del recorrido además del footer. Botón rosa profundo + outline claro.
6. **Footer** — mismo verde oscuro que el CTA, sin borde duro entre ambos.

### Reglas
**Hacé esto**
- Un solo botón sólido (rojo o rosa profundo) por sección.
- Alterná marfil y superficie clara entre secciones, sin bordes duros.
- Un h1 por página; los h2 marcan cada sección, nunca saltar a h4 directo.
- 108px de aire vertical entre secciones en escritorio, 72px en mobile.

**Evitá esto**
- Dos fondos verde oscuro seguidos.
- Rosa profundo en más de una acción por scroll.
- Mezclar rojo y rosa profundo en el mismo botón o insignia.
- Hojas cayendo dentro de tarjetas o formularios.

## 6. Archivos de referencia
- `src/` — implementación React/Vite completa (fuente de verdad, componentes vivos).
- `example.html` — ejemplo estático standalone (HTML/CSS/JS vanilla, sin build), mismo sistema aplicado a una página completa.
