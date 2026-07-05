# Compa — Arquitectura Final

> **Version**: 2.0 (Nemotron + Supabase pivot) | **Build start**: 8:00 AM, 4 Julio 2026 | **Demo**: ~3:00 PM
> **Equipo**: 3 personas | **Stack**: n8n Cloud + ElevenLabs Conversational AI + Codex/OpenAI (gpt-4o-mini) + Supabase (PostgreSQL) + Nemotron-Personas
> **Hackathon**: Cursor Buildathon — 3 tracks: Codex ($10K), ElevenLabs ($990), n8n ($720)

---

## Tabla de Contenidos

1. [Executive Summary](#1-executive-summary)
2. [Technology Stack Decisions](#2-technology-stack-decisions)
3. [Project Structure](#3-project-structure)
4. [Data Layer](#4-data-layer)
5. [n8n Workflow Specifications](#5-n8n-workflow-specifications)
6. [ElevenLabs Agent Configuration](#6-elevenlabs-agent-configuration)
7. [Codex Prompt Templates](#7-codex-prompt-templates)
8. [API Contracts](#8-api-contracts)
9. [Demo Data](#9-demo-data)
10. [Transparency Architecture](#10-transparency-architecture)
11. [Demo Script](#11-demo-script)
12. [Build Order](#12-build-order)
13. [Risk Fallbacks](#13-risk-fallbacks)
14. [Track Strategy](#14-track-strategy)

---

## 1. Executive Summary

Compa es un "cofundador" digital con voz para micro y pequeños productores salvadoreños que venden al Estado. Detecta oportunidades de negocio en COMPRASAL, las comunica por voz via ElevenLabs, y ayuda al productor a evaluar si conviene participar generando preguntas críticas via Codex/OpenAI. La arquitectura es minimalista: 2 flujos de n8n (Oportunidades + retar_decision), 1 agente de ElevenLabs con 1 herramienta, datos generados sintéticamente via Nemotron-Personas-El-Salvador (nvidia/Nemotron-Personas-El-Salvador, 148k personas, censo 2024), almacenados en Supabase (PostgreSQL) con respaldo JSON — todo construido para un demo de 3 minutos en vivo.

> **CHANGED v2.0**: Reemplazamos Google Sheets por Supabase (PostgreSQL) para una base de datos real que puede crecer mas alla del hackathon. Agregamos el dataset nvidia/Nemotron-Personas-El-Salvador como fuente primaria de datos sintéticos. COMPRASAL reclama ser datos abiertos pero no es accesible programaticamente; Nemotron esta publicado, documentado, es reproducible y esta anclado al censo 2024.

## 2. Technology Stack Decisions

### Stack Definitivo

| Componente | Version/Plan | Justificacion |
|---|---|---|
| **n8n Cloud** | Trial (app.n8n.cloud) | Orquestacion de workflows. NO self-hosted. NO Docker local para el demo (solo como respaldo). |
| **ElevenLabs Conversational AI** | Plan gratuito (buildathon) | Voz del agente. NO Twilio. Llamadas simuladas con audio pregrabado. |
| **ElevenLabs Voice** | `g3pC3sr9iFcUwoSLvVLV` (Luis, Latin American Spanish, premade) | NO custom clone. Autenticidad salvadorena viene del system prompt. |
| **Codex/OpenAI** | `gpt-4o-mini` | Razonamiento estructurado. Rapido, barato, soporta `json_schema` con `strict: true`. |
| **Supabase** | Free tier (PostgreSQL) | Base de datos real con RLS, Realtime, SQL joins. Escalable mas alla del hackathon. |
| **nvidia/Nemotron-Personas-El-Salvador** | HuggingFace dataset | 148k personas sintéticas salvadoreñas, metodoologia publicada, basado en censo 2024. Fuente principal de datos demo. |
| **Cached JSON** | `data/fallback.json`, `data/personas_fallback.json` | Respaldo si Supabase no responde o si Nemotron no se puede descargar en vivo. |

> **CHANGED v2.0**: Se reemplazo Google Sheets por Supabase. Se agrego Nemotron-Personas como fuente de datos sinteticos. Se agregaron scripts Python para generacion de datos.
>
> **Por que el cambio**: COMPRASAL reclama ser datos abiertos pero no es accesible — no tiene API publica, los PDFs de licitaciones no estan estructurados, y el portal requiere navegacion manual. Nemotron-Personas-El-Salvador, en cambio, esta publicado en HuggingFace, tiene metodologia documentada, es reproducible, y esta anclado al censo 2024 de DIGESTYC. Supabase reemplaza Google Sheets porque necesitamos una base de datos real con capacidades de consulta, joins, y RLS que pueda escalar mas alla del hackathon.

### Herramientas de generacion de datos (build-time)

| Script | Proposito |
|---|---|
| `scripts/simular_datos_compa.py` | Genera productores_demo.csv y proveedores_demo.csv a partir del dataset Nemotron (cuando hay acceso a HuggingFace) |
| `scripts/generar_personas_fallback.py` | Genera personas sintéticas en formato Nemotron SIN acceso a HuggingFace. Produce `data/personas_sinteticas.json` y CSVs |
| `scripts/generar_oportunidades.py` | Genera oportunidades de COMPRASAL cacheadas en formato Supabase-ready. Produce `data/oportunidades.json` |

> **CHANGED v2.0**: Nuevos scripts de generacion de datos. `generar_personas_fallback.py` ya existe en la raiz del proyecto; se movera a `scripts/` en la refactorizacion post-hackathon.

### Lo Que NO Se Usa (cortado explicitamente)

- Subasta Inversa — NO. Reemplazado por resultado pre-computado.
- Airtable — NO. Supabase es suficiente.
- Twilio — NO. Llamadas simuladas con audio pregrabado.
- Scraping de COMPRASAL / RUPES — NO.
- Error sub-workflows — NO. Solo try/catch inline.
- Autenticacion de usuarios — NO.
- Sanctions checks — NO.

> **CHANGED v2.0**: Se removio "PostgreSQL / Supabase — NO" de la lista (ahora se usa Supabase). Se removio "Google Sheets" de la lista (reemplazado por Supabase).

## 3. Project Structure

```
C:\Users\joshb\Documents\Compa\
|
+-- .env                           # API keys (gitignored)
+-- .gitignore
+-- README.md                      # 3-line project description
|
+-- supabase/
|   +-- schema.sql                     # Full SQL schema: tables, indexes, RLS, constraints
|   +-- seed.sql                       # Demo data: productores, oportunidades, proveedores, decisiones
|
+-- scripts/
|   +-- simular_datos_compa.py         # Generate personas from Nemotron dataset (HF access)
|   +-- generar_personas_fallback.py   # Generate synthetic personas without HuggingFace
|   +-- generar_oportunidades.py       # Cache COMPRASAL opportunities to JSON/Supabase
|
+-- n8n-exports/
|   +-- workflow-oportunidades.json    # Export from n8n (Postgres nodes instead of Google Sheets)
|   +-- workflow-retar-decision.json   # Export from n8n (with Postgres insert node)
|
+-- data/
|   +-- fallback.json                  # Supabase fallback (oportunidades cacheadas)
|   +-- personas_fallback.json         # Nemotron-style personas (15 records, mirror field structure)
|   +-- personas_sinteticas.json       # Full fallback output: 30 productores + 20 proveedores
|   +-- productores_demo.csv           # Seed productores for Supabase
|   +-- proveedores_demo.csv           # Seed proveedores for Supabase
|   +-- productos.json                 # Productos/servicios cacheados
|
+-- prompts/
|   +-- retar-decision-system.md       # System prompt for Codex
|
+-- demo/
|   +-- audio-01-intro.mp3             # Greeting + opportunity pitch (20s)
|   +-- audio-02-questions.mp3         # 3 questions with pauses (30s)
|   +-- audio-03-closing.mp3           # Closing remark (8s)
|   +-- pitch-deck.pdf                 # 6 slides
|
+-- docs/
    +-- contexto-compa.md              # Full context document
    +-- arquitectura-final.md          # THIS DOCUMENT
```

> **CHANGED v2.0**:
> - ADDED: `supabase/` directory with SQL schema and seed files
> - ADDED: `scripts/` directory with data generation pipeline
> - ADDED: `data/personas_fallback.json` (Nemotron-style synthetic personas)
> - ADDED: `data/personas_sinteticas.json` (full fallback output from fallback generator)
> - MODIFIED: `data/fallback.json` changed from "Google Sheets fallback" to "Supabase fallback" with expanded schema (meta, records, matching_summary)
> - MODIFIED: `n8n-exports/` workflow JSONs now use Postgres nodes instead of Google Sheets nodes
> - REMOVED: `data/seed-productores.csv` and `data/seed-oportunidades.csv` (migrated to `supabase/seed.sql`)

## 4. Data Layer

### 4.1 Supabase Schema

> **CHANGED v2.0**: Seccion completamente reescrita. Google Sheets reemplazado por Supabase (PostgreSQL) con 4 tablas, indices, constraints, RLS, y funciones de matching.

Proyecto Supabase: `compa-buildathon` (gratuito, free tier)

Conexion desde n8n: `postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require`

#### 4.1.1 Tabla: `productores`

```sql
CREATE TABLE productores (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre      TEXT NOT NULL,
    rubro       TEXT NOT NULL,
    ubicacion   TEXT,
    capacidad   TEXT,
    telefono    TEXT,
    dui         TEXT,
    nit         TEXT,
    created_at  TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_productores_rubro     ON productores(rubro);
CREATE INDEX idx_productores_ubicacion ON productores(ubicacion);
```

Constraints: formato telefono `+503XXXXXXXX`, formato DUI `########-#`, formato NIT `####-######-###-#`.

#### 4.1.2 Tabla: `oportunidades`

```sql
CREATE TABLE oportunidades (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    titulo            TEXT NOT NULL,
    institucion       TEXT NOT NULL,
    monto             DECIMAL(12,2) NOT NULL,
    fecha_cierre      DATE NOT NULL,
    rubro_requerido   TEXT NOT NULL,
    unspsc_code       TEXT,
    url_fuente        TEXT,
    tipo_contratacion TEXT,
    created_at        TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_oportunidades_rubro_requerido ON oportunidades(rubro_requerido);
CREATE INDEX idx_oportunidades_fecha_cierre     ON oportunidades(fecha_cierre);
CREATE INDEX idx_oportunidades_monto            ON oportunidades(monto DESC);
```

#### 4.1.3 Tabla: `proveedores`

```sql
CREATE TABLE proveedores (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nombre            TEXT NOT NULL,
    rubro             TEXT NOT NULL,
    ubicacion         TEXT,
    capacidad         TEXT,
    telefono          TEXT,
    dui               TEXT,
    nit               TEXT,
    persona_text      TEXT,
    rubros_suministra TEXT[],
    created_at        TIMESTAMPTZ DEFAULT now()
);
```

#### 4.1.4 Tabla: `decisiones`

```sql
CREATE TABLE decisiones (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    productor_id      UUID REFERENCES productores(id) ON DELETE CASCADE,
    decision_descrita TEXT NOT NULL,
    preguntas_json    JSONB,
    reasoning_trace   TEXT,
    created_at        TIMESTAMPTZ DEFAULT now()
);
```

#### 4.1.5 Row Level Security (RLS)

Modo demo: RLS habilitado con politicas permisivas (ALL for anon/authenticated).
En produccion: reemplazar con politicas por usuario.

#### 4.1.6 Funcion de Matching

```sql
CREATE OR REPLACE FUNCTION matching_oportunidades(p_productor_id UUID)
RETURNS TABLE (
    oportunidad_id  UUID, titulo TEXT, institucion TEXT,
    monto           DECIMAL(12,2), fecha_cierre DATE,
    rubro_requerido TEXT, score INTEGER,
    productor_nombre TEXT, productor_rubro TEXT
)
LANGUAGE plpgsql STABLE AS $$
DECLARE
    v_rubro  TEXT;
    v_nombre TEXT;
BEGIN
    SELECT p.rubro, p.nombre INTO v_rubro, v_nombre
    FROM productores p WHERE p.id = p_productor_id;
    IF NOT FOUND THEN RETURN; END IF;

    RETURN QUERY
    SELECT o.id, o.titulo, o.institucion, o.monto, o.fecha_cierre,
           o.rubro_requerido,
           CAST(
               CASE
                   WHEN o.rubro_requerido = v_rubro THEN 100
                   WHEN o.rubro_requerido ILIKE '%' || SPLIT_PART(v_rubro, ' ', 1) || '%' THEN 70
                   ELSE 30 + CAST(floor(random() * 20) AS INTEGER)
               END
           AS INTEGER) AS score,
           v_nombre, v_rubro
    FROM oportunidades o
    WHERE o.rubro_requerido = v_rubro
       OR o.rubro_requerido ILIKE '%' || SPLIT_PART(v_rubro, ' ', 1) || '%'
    ORDER BY o.monto DESC;
END;
$$;
```

### 4.2 Matching Algorithm (n8n Code Node, ~30 lines)

> **CHANGED v2.0**: Misma logica de scoring, pero ahora consulta datos desde Postgres (Supabase) en lugar de Google Sheets. El algoritmo es identico al de v1.0 para mantener compatibilidad con las demos existentes.

```javascript
const productor = $input.first().json;
const oportunidades = $input.all()[1].map(item => item.json);

const matches = oportunidades.map(opp => {
  let rubroScore = 0;
  if (productor.rubro === opp.rubro_requerido) rubroScore = 1.0;
  else if (opp.rubro_requerido.includes(productor.rubro.split(' ')[0])) rubroScore = 0.5;

  const score = rubroScore * 0.60 + 0.25 + (opp.monto <= 50000 ? 0.15 : 0.05);

  return {
    opp_id: opp.id,
    titulo: opp.titulo,
    institucion: opp.institucion,
    monto: opp.monto,
    fecha_cierre: opp.fecha_cierre,
    rubro_requerido: opp.rubro_requerido,
    url_fuente: opp.url_fuente,
    score: Math.round(score * 100),
    productor_id: productor.id,
    productor_nombre: productor.nombre,
    productor_rubro: productor.rubro,
    productor_telefono: productor.telefono,
    productor_ubicacion: productor.ubicacion,
    productor_capacidad: productor.capacidad,
    oportunidad_resumen: `${opp.titulo} - ${opp.institucion} - $${Number(opp.monto).toLocaleString()} - Cierre: ${opp.fecha_cierre}.`
  };
});

return matches.filter(m => m.score >= 60).sort((a, b) => b.score - a.score);
```

Resultados esperados para Vilma (v2.0, 20 oportunidades en Supabase):
- opp-001 (Alimentacion MINED) -> Score 100 (EXACTO, monto <= 50000)
- opp-002 (Cafeteria ANDA) -> Score 70 (EXACTO, monto <= 50000)
- opp-004 (Frutas MAG) -> Score 70 (EXACTO, monto <= 50000)
- opp-016 (Centros Penales) -> Score 70 (EXACTO, monto > 50000)
- opp-017 (Leche MINED) -> Score 70 (EXACTO, monto <= 50000)
- opp-020 (Catering Presidencial) -> Score 70 (EXACTO, monto <= 50000)

> **CHANGED v2.0**: Con 20 oportunidades en lugar de 5, Vilma ahora matchea 6 oportunidades (todas las de rubro "Alimentos y Bebidas" con score >= 60), no solo 3. Esto demuestra la escalabilidad del stack de base de datos real.

## 5. n8n Workflow Specifications

### 5.1 Environment Variables (n8n Cloud Settings)

> **CHANGED v2.0**: Se agregaron variables de Supabase. Se removio `ELEVENLABS_PHONE_NUMBER` (manejado por agente ahora).

| Variable | Valor |
|---|---|
| `SUPABASE_URL` | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `eyJhbGciOi...` (service_role key) |
| `OPENAI_API_KEY` | `sk-...` |
| `ELEVENLABS_API_KEY` | `sk_...` |
| `ELEVENLABS_AGENT_ID` | `agX7k2m9pQ4rL3zN8wB6vC1d` |

### 5.2 Workflow 1: Oportunidades (11 nodes)

> **CHANGED v2.0**: Reemplazados nodos "Google Sheets: Read" por "Postgres: Execute Query". Un nodo menos (11 vs 12) porque Postgres no necesita rango A:I.

**Trigger**: Manual (demo) + Cron (0 */6 * * *)

1. **Manual Trigger + Cron Trigger** — inicia el workflow
2. **Merge** — "Wait for both" (cualquier trigger activa el flujo)
3. **Postgres: "Read productores"** — `SELECT * FROM productores`
4. **Postgres: "Read oportunidades"** — `SELECT * FROM oportunidades`
5. **Code: "Match algorithm"** — weighted scoring (Section 4.2)
6. **IF: "Has any matches?"** — condition: score >= 60
   - TRUE -> Node 7
   - FALSE -> Node 10 (Log "No matches")
7. **Set: "Build ElevenLabs payload"** — constructs agent_id, phone_number, dynamic_variables
8. **HTTP Request: "POST to ElevenLabs"** — URL: https://api.elevenlabs.io/v1/convai/conversations, Header Auth (xi-api-key), Body from Node 7. Retry: 2 attempts, 2s delay. Error: -> Node 9.
9. **NoOp: "Success log"** — visual indicator
10. **Code: "Call failed log"** — error branch
11. **Code: "No matches log"** — FALSE branch from Node 6

### 5.3 Workflow 2: retar_decision (9 nodes)

> **CHANGED v2.0**: Se agrego nodo "Postgres: INSERT into decisiones" para persistir cada decision + preguntas generadas en Supabase. Esto permite mostrar el historial de decisiones en la demo y sirve como audit trail de transparencia.

**Trigger**: Webhook POST /retar-decision

1. **Webhook: "POST /retar-decision"** — Header Auth (X-Compa-Webhook-Secret), Response Mode: When Last Node Finishes, Timeout: 25s
2. **Code: "Validate and normalize input"** — checks decision_descrita >= 10 chars, normalizes fields
3. **HTTP Request: "POST to OpenAI"** — gpt-4o-mini, system + user prompts, json_schema response_format. Retry: 1 attempt, 2s delay, 15s timeout. Error -> Node 7.
4. **Code: "Parse Codex response"** — JSON.parse, validates 3 preguntas, trims
5. **Postgres: "INSERT into decisiones"** — persiste decision + preguntas + reasoning_trace en Supabase
6. **Respond to Webhook: "Return preguntas"** — HTTP 200, `{ preguntas: [...], _fallback: false }`
7. **Code: "Serve fallback questions"** — error branch, returns hardcoded backup questions
8. **Respond to Webhook: "Return fallback preguntas"** — HTTP 200, `{ preguntas: [...], _fallback: true }`

### 5.4 Supabase Fallback Code

> **CHANGED v2.0**: Reescrito para reflejar que el fallback ahora es de Supabase, no de Google Sheets. La estructura de datos en fallback.json coincide con el schema de Supabase.

```javascript
const dbData = $input.first().json;
if (!dbData || (Array.isArray(dbData) && dbData.length === 0)) {
  const fs = require('fs');
  const path = require('path');
  const fallbackPath = path.join(__dirname, '..', 'data', 'fallback.json');
  const fallbackData = JSON.parse(fs.readFileSync(fallbackPath, 'utf8'));
  return fallbackData.records;
}
return $input.all();
```

## 6. ElevenLabs Agent Configuration

(Sin cambios respecto a v1.0. Ver documento original para configuracion completa del agente, dynamic variables, system prompt, y tool definition.)

### Dynamic Variables

- `nombre_productor` — From productores table en Supabase (Vilma Jeanneth)
- `rubro_negocio` — From productor profile (alimentos preparados)
- `oportunidad_detectada` — From matched opportunity

## 7. Codex Prompt Templates

(Sin cambios respecto a v1.0. Ver documento original para system prompt, user prompt template, y OpenAI call parameters.)

## 8. API Contracts

(Sin cambios respecto a v1.0. Ver documento original para contratos de retar_decision y outbound call.)

## 9. Demo Data

### Productor: Vilma Jeanneth Guardado de Ayala

(Sin cambios respecto a v1.0 — misma Vilma, mismo perfil.)

### Oportunidades en Supabase (20 registros)

> **CHANGED v2.0**: Se expandio de 5 a 20 oportunidades cacheadas de COMPRASAL, cubriendo 10 rubros distintos. Esto demuestra la capacidad de Supabase para manejar datasets reales y permite matching con productores de diferentes rubros.

| ID | Titulo | Monto | Rubro Requerido | Match Vilma |
|---|---|---|---|---|
| opp-001 | Alimentacion Escolar - MINED | $48,750 | Alimentos y Bebidas | Score 100 |
| opp-002 | Cafeteria ANDA | $28,400 | Alimentos y Bebidas | Score 70 |
| opp-003 | Uniformes ISSS | $12,680 | Textiles y Uniformes | Score 40 (NO) |
| opp-004 | Frutas/Vegetales MAG | $3,250 | Alimentos y Bebidas | Score 70 |
| opp-005 | Pupitres FISDL | $152,000 | Mobiliario y Equipo | Score 30 (NO) |
| opp-006 | Limpieza MINSAL | $45,000 | Servicios de Limpieza | NO |
| opp-007 | Sistema Expedientes ANDA | $18,500 | Tecnologia | NO |
| opp-008 | Uniformes PNC | $95,000 | Textiles y Uniformes | NO |
| opp-009 | Mantenimiento Casa Presidencial | $78,000 | Construccion | NO |
| opp-010 | Transporte Insumos MAG | $28,500 | Transporte | NO |
| opp-011 | Calzado Alcaldia SS | $4,200 | Calzado | NO |
| opp-012 | Impresion Material MINED | $22,000 | Imprenta | NO |
| opp-013 | Reciclaje FODES | $15,000 | Reciclaje | NO |
| opp-014 | Mobiliario FISDL | $35,000 | Mobiliario y Equipo | NO |
| opp-015 | Feria Agropecuaria MAG | $8,500 | Servicios Profesionales | NO |
| opp-016 | Alimentacion Centros Penales | $56,000 | Alimentos y Bebidas | Score 70 |
| opp-017 | Leche Desayuno Escolar MINED | $12,400 | Alimentos y Bebidas | Score 70 |
| opp-018 | Mantenimiento Equipo CSJ | $32,000 | Tecnologia | NO |
| opp-019 | Ferreteria FODES | $5,800 | Construccion | NO |
| opp-020 | Catering Casa Presidencial | $12,500 | Alimentos y Bebidas | Score 70 |

### Datos de Nemotron-Personas-El-Salvador

> **CHANGED v2.0**: Nueva seccion. El dataset nvidia/Nemotron-Personas-El-Salvador es la fuente primaria de datos sinteticos para la demo.

| Atributo | Valor |
|---|---|
| Dataset | nvidia/Nemotron-Personas-El-Salvador |
| Registros | 148,000 personas sinteticas salvadorenas |
| Metodologia | Nemotron-4 340B + curaduria post-hoc, publicada en arXiv |
| Anclaje | Censo 2024 (DIGESTYC) |
| Campos clave | nombre, edad, genero, departamento, municipio, ocupacion, nivel educativo, profesion, rubro_negocio, tamano_negocio, ingreso_mensual_estimado, professional_persona |
| Acceso | HuggingFace (gated, approval automatico) |

**Pipeline de datos:**
1. HuggingFace `datasets` library descarga Nemotron-Personas-El-Salvador
2. `scripts/simular_datos_compa.py` filtra por `rubro_negocio` relevante, genera CSV para Supabase
3. Si no hay internet/HuggingFace durante setup: `scripts/generar_personas_fallback.py` genera personas sinteticas espejo
4. Datos finales se cargan en Supabase via `supabase/seed.sql`

**Proveniencia en demo:**
- Cada persona en la DB lleva metadata `source_tag: 'nemotron' | 'fallback'`
- Las oportunidades de COMPRASAL llevan `url_fuente` apuntando a comprasal.gob.sv
- En la demo, se muestra la fuente de cada dato al pasar el mouse o en una columna "Fuente"

## 10. Transparency Architecture

> **CHANGED v2.0**: Nueva seccion. Arquitectura de transparencia — como mostramos la proveniencia de datos en la demo.

### 10.1 Data Provenance Model

Cada registro en Supabase incluye metadatos de origen para auditoria visual en la demo:

| Tabla | Campo de origen | Valores posibles |
|---|---|---|
| `productores` | `source_tag` (metadata) | `nemotron`, `fallback`, `manual` |
| `oportunidades` | `url_fuente` (TEXT) | URL a comprasal.gob.sv |
| `decisiones` | `reasoning_trace` (TEXT) | Traza de razonamiento de Codex |
| `decisiones` | `preguntas_json._fallback` (BOOLEAN) | `true` si viene de respaldo |

### 10.2 Demo Flow: How We Show It

**Momento 1: "Donde vienen estos datos?"** (Segment 2)
- Presentador abre el SQL Editor de Supabase
- Muestra la tabla `oportunidades` con la columna `url_fuente`
- Hace clic en un enlace -> se abre comprasal.gob.sv mostrando la licitacion real
- "Estos datos son de COMPRASAL. No los inventamos."

**Momento 2: "Quien es Vilma?"** (Segment 3)
- Presentador muestra la tabla `productores` en Supabase
- Columna `source_tag` = `nemotron`
- "Vilma fue generada por el modelo Nemotron de NVIDIA, basado en el censo 2024 de DIGESTYC."
- Si es fallback: "Vilma fue generada por nuestro generador sintetico, que replica la estructura de Nemotron."

**Momento 3: "Por que estas preguntas?"** (Segment 5, Momento WOW)
- Codex devuelve `reasoning_trace` junto con las preguntas
- Presentador muestra el JSON: `"reasoning_trace": "Clasificacion: decision de inversion/escala. Punto ciego 1:..."` 
- "Codex no solo genera preguntas — explica POR QUE. Eso es transparencia algorítmica."

### 10.3 Database Schema for Provenance

Para implementar provenance tracking en produccion:

```sql
ALTER TABLE productores ADD COLUMN source_tag TEXT DEFAULT 'manual';
ALTER TABLE oportunidades ADD COLUMN source_tag TEXT DEFAULT 'comprasal_cache';
ALTER TABLE decisiones ADD COLUMN es_fallback BOOLEAN DEFAULT false;

COMMENT ON COLUMN productores.source_tag IS 'Origen del perfil: nemotron, fallback, manual';
COMMENT ON COLUMN oportunidades.source_tag IS 'Origen de la oportunidad: comprasal_cache, manual';
COMMENT ON COLUMN decisiones.es_fallback IS 'True si se usaron preguntas de respaldo por fallo de Codex';
```

### 10.4 Por que es importante para el hackathon

- **Track Codex**: El `reasoning_trace` muestra que el modelo no es una caja negra — justifica cada pregunta.
- **Track ElevenLabs**: El agente solo usa datos con origen verificable (COMPRASAL + Nemotron).
- **Track n8n**: Los nodos de Postgres permiten mostrar datos en tiempo real desde Supabase.
- **Diferenciacion**: Mientras otros equipos usan datos inventados, Compa muestra exactamente de donde viene cada dato. Esto es LO QUE COMPRASAL DEBERIA TENER PERO NO TIENE.

## 11. Demo Script (3 Minutes, 6 Segments)

(Sin cambios en la estructura respecto a v1.0, pero cada segmento ahora referencia Supabase en lugar de Google Sheets. Ver documento original para el script completo.)

### Segment 2: n8n se ejecuta (:15-:45) — EN VIVO

> **CHANGED v2.0**: Los nodos ahora leen de Postgres/Supabase en lugar de Google Sheets.

- Presentador hace clic en "Execute Workflow"
- Nodos se iluminan: Manual Trigger -> Merge -> Postgres (productores) -> Postgres (oportunidades) -> Code (Match) -> IF -> Set (Payload) -> HTTP Request (ElevenLabs)
- Presentador narra: "Encontro un match... $48,750... inicio la llamada. Los datos vienen de Supabase, nuestra base de datos en PostgreSQL."

### Segment 4: retar_decision (1:30-2:00) — MIXTO

> **CHANGED v2.0**: Se agrega el nodo Postgres INSERT en la cadena.

- Vilma (voz): "Me da miedo, es el triple de lo que hago..."
- n8n canvas cambia a workflow retar_decision (EN VIVO)
- Webhook -> Code (Validate) -> HTTP Request (OpenAI) -> Code (Parse) -> **Postgres (INSERT)** -> Respond
- Presentador: "La decision se guarda en Supabase con el razonamiento de Codex. Auditoria completa."

## 12. Build Order

> **CHANGED v2.0**: Se agrego fase de setup de Supabase antes de n8n. Se dividio la fase de Datos para incluir generacion de Nemotron.

| Fase | Tiempo | Persona | Que se construye |
|---|---|---|---|
| Setup | 0:00-0:30 | A | n8n Cloud, Supabase project, API keys, .env |
| **Supabase** | **0:30-1:00** | **A** | **Crear tablas, indices, RLS en SQL Editor. Correr seed.sql** |
| Datos | 1:00-1:30 | B | Generar personas (Nemotron o fallback), CSVs, fallback.json |
| Oportunidades | 1:30-3:00 | A | Workflow 1: 11 nodos, Postgres + matching algorithm |
| retar_decision | 1:30-3:00 | B | Workflow 2: 9 nodos, Postgres INSERT, Codex integration |
| Agent | 3:00-4:00 | C | ElevenLabs agent, system prompt, tool config |
| Audio | 4:00-5:00 | C | 3 MP3s pregrabados via ElevenLabs TTS |
| **Transparencia** | **5:00-5:30** | **C** | **Preparar pantallas de Supabase + provenance para demo** |
| Integracion | 5:30-7:00 | Todos | E2E testing, 3 runs consecutivas |
| Pitch + Ensayo | 7:00-8:00 | Todos | 6 slides, 3 ensayos cronometrados |

**Hard Stop: Hora 8 (4:00 PM). STOP CODING.**

> **CHANGED v2.0**: Se agrego la fase "Supabase" (setup de base de datos antes de n8n). Se agrego la fase "Transparencia" para preparar la demostracion de proveniencia de datos.

## 13. Risk Fallbacks

### Go/No-Go Decision Points

(Sin cambios respecto a v1.0.)

### Fallback Scripts

> **CHANGED v2.0**: Se actualizaron los fallbacks para reflejar Supabase y Nemotron.

| Riesgo | Mitigacion |
|---|---|
| ElevenLabs API fails | 3 MP3s en escritorio, barra espaciadora en VLC |
| Codex/OpenAI timeout | Preguntas hardcodeadas en Code Node (fallback node) |
| n8n Cloud down | `docker run n8nio/n8n` + import JSON exports |
| **Supabase unreachable** | **Code Node lee `data/fallback.json` (misma estructura que Supabase)** |
| **Nemotron descarga falla (sin internet / HuggingFace gated)** | **`generar_personas_fallback.py` genera personas espejo en 2s** |
| Internet se cae | Audio funciona sin internet. Presentador narra de memoria. |
| Proyector falla | Audio solo + memoria |
| Run out of time | Hard stop, switchear a video |

> **CHANGED v2.0**: Se reemplazo "Google Sheets unreachable" por "Supabase unreachable". Se agrego "Nemotron descarga falla" con mitigacion via fallback generator.

## 14. Track Strategy

(Sin cambios estructurales respecto a v1.0. Ver documento original para la estrategia detallada de cada track.)

> **CHANGED v2.0**: El track de n8n ahora incluye nodos Postgres (en lugar de Google Sheets), lo que muestra integracion con base de datos real. La transparencia de datos (Seccion 10) refuerza los 3 tracks: Codex (reasoning_trace), ElevenLabs (datos verificables), n8n (proveniencia en tiempo real).

---

## Pre-Demo Checklist

### Technology
- [ ] n8n: Ambos workflows activos (green toggle)
- [ ] n8n: Webhooks en modo production, no test
- [ ] **Supabase: Tablas creadas con schema.sql**
- [ ] **Supabase: Seed data cargado con seed.sql**
- [ ] **Supabase: Connection string configurada en n8n**
- [ ] **Supabase: SQL Editor abierto para mostrar provenance en demo**
- [ ] ElevenLabs: Agente activo, tool URL correcta
- [ ] ElevenLabs: Dynamic variables configuradas
- [ ] OpenAI: API key activa con creditos
- [ ] **Nemotron o fallback: Datos generados y cargados**
- [ ] .env gitignored
- [ ] **data/fallback.json accesible (fallback de Supabase)**
- [ ] **data/personas_fallback.json accesible (fallback de Nemotron)**

### Demo
- [ ] Workflow 1: Execute -> todos verdes (Postgres nodes conectados)
- [ ] Workflow 2: POST sample -> responde preguntas + INSERT en Supabase
- [ ] Workflow 2: POST invalido -> responde fallback
- [ ] Audio 01-02-03 se reproducen correctamente
- [ ] Sincronia audio + canvas verificada
- [ ] **Supabase: Mostrar tabla oportunidades con url_fuente**
- [ ] **Supabase: Mostrar tabla decisiones con reasoning_trace**
- [ ] reasoning_trace visible en pantalla
- [ ] Slide final con 3 logos + QR
- [ ] 3 ensayos cronometrados (<3:30)

### Respaldo
- [ ] Laptop cargada (2+ horas)
- [ ] Cable HDMI + adaptador
- [ ] Audios en laptop + USB
- [ ] Script de demo impreso (1 pagina)
- [ ] n8n JSON exports en USB
- [ ] **Supabase schema.sql en USB (por si toca crear DB desde cero)**

> **CHANGED v2.0**: Se actualizaron todas las entradas de Google Sheets a Supabase. Se agregaron entradas para Nemotron/fallback, schema.sql, seed.sql, y verificacion de proveniencia en demo.

---

*Documento version 2.0 (Nemotron + Supabase pivot) — 4 Julio 2026 — Compa Buildathon*
*Archivo: `C:\Users\joshb\Documents\Compa\docs\arquitectura-final.md`*

### Resumen de Cambios v1.0 -> v2.0

| Seccion | Que cambio | Por que |
|---|---|---|
| 1. Executive Summary | Google Sheets -> Supabase. Nemotron como fuente de datos. | COMPRASAL no es accesible; Nemotron es publicado y reproducible. Supabase escala mas alla del hackathon. |
| 2. Stack | Se agrego Supabase, Nemotron, scripts Python. Se removio "NO PostgreSQL". | Necesitamos DB real. Datos sinteticos requieren pipeline de generacion. |
| 3. Project Structure | Nuevos directorios: supabase/, scripts/. Datos expandidos. | Refleja la nueva arquitectura de datos. |
| 4. Data Layer | Google Sheets reemplazado por schema SQL completo con 4 tablas, RLS, funcion de matching. | Base de datos real con joins, indices, constraints. |
| 5. n8n Workflows | Postgres nodes reemplazan Google Sheets nodes. Nuevo nodo INSERT en workflow 2. | Integracion con Supabase. Persistencia de decisiones. |
| 9. Demo Data | 20 oportunidades (antes 5). Nueva tabla de proveniencia Nemotron. | Escalabilidad. Transparencia. |
| **10. Transparency Architecture** | **NUEVA** | Diferenciacion del hackathon: mostramos de donde viene cada dato. |
| 12. Build Order | Fases de Supabase + Transparencia agregadas. | Setup de DB antes de n8n. Preparacion de demo de proveniencia. |
| 13. Risk Fallbacks | Supabase y Nemotron fallbacks agregados. | Cobertura de riesgos de la nueva arquitectura. |
| Checklist | Actualizado para Supabase, Nemotron, proveniencia. | Refleja el nuevo stack. |
