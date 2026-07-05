# Compa — n8n Workflow Specifications (Supabase)

> Basado en `docs/arquitectura-final.md` v1.0 | Adaptado a Supabase/Postgres
> n8n Cloud | 2 July 2026

---

## Environment Variables (n8n Cloud Settings)

| Variable | Valor |
|---|---|
| `SUPABASE_URL` | `https://xxxx.supabase.co` |
| `SUPABASE_SERVICE_KEY` | `eyJhbGciOi...` (service_role key) |
| `OPENAI_API_KEY` | `sk-...` |
| `ELEVENLABS_API_KEY` | `sk_...` |
| `ELEVENLABS_AGENT_ID` | `agX7k2m9pQ4rL3zN8wB6vC1d` |

---

## WORKFLOW 1: Oportunidades (11 nodes)

**Propósito:** Cada 6 horas (o manual en demo), leer productores y oportunidades desde Supabase, ejecutar el algoritmo de matching, y si hay match con score >= 60, iniciar una llamada outbound a ElevenLabs.

### Conexión entre nodos (diagrama)

```
[Manual Trigger + Cron Trigger] (merge: Mode "Wait for both")
    |
    v
[Postgres: Read productores]  ----+
                                   |---> [Code: Match algorithm] ---> [IF: score >= 60?]
[Postgres: Read oportunidades]  --+                                          |
                                                              TRUE (score >= 60)    FALSE
                                                                  |                   |
                                                                  v                   v
                                                          [Set: Build payload]   [Code: No matches log]
                                                                  |
                                                                  v
                                                          [HTTP Request: ElevenLabs] --- ERROR ---> [Code: Call failed log]
                                                                  |
                                                                  v
                                                          [NoOp: Success log]
```

### Node 1: Manual Trigger

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.manualTrigger` |
| **Mode** | N/A (no configuration needed) |

No additional config. Used for demo execution.

### Node 2: Cron Trigger

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.cron` |
| **Trigger Times** | `0 */6 * * *` |
| **Mode** | `everyXHours` (o `custom` con cron expression) |

Disparo cada 6 horas en punto. Los nodos 1 y 2 se conectan a un nodo "Merge" (Mode: "Wait for both") que espera cualquiera de los dos triggers, o se colocan en paralelo como entradas del workflow (n8n permite múltiples triggers en un workflow; el primero que se active ejecuta el flujo).

### Node 3: Postgres — Read productores

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.postgres` |
| **Operation** | `Execute Query` |
| **Query** | `SELECT * FROM productores` |
| **Credentials** | Supabase Postgres (connection string o host+port+db+user+password) |

Opcional: usar `"Single"` output para que el resultado sea un objeto plano, no un array de arrays.

### Node 4: Postgres — Read oportunidades

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.postgres` |
| **Operation** | `Execute Query` |
| **Query** | `SELECT * FROM oportunidades` |
| **Credentials** | Supabase Postgres (misma conexion) |

### Node 5: Code — "Match algorithm"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.code` |
| **Mode** | `runOnceForAllItems` |
| **Language** | JavaScript |

**Código JavaScript:**

```javascript
// El primer input trae el productor (1 fila)
const productor = $input.first().json;

// El segundo input trae las oportunidades (N filas)
const oportunidades = $input.all()[1].map(item => item.json);

const matches = oportunidades.map(opp => {
  let rubroScore = 0;
  if (productor.rubro === opp.rubro_requerido) rubroScore = 1.0;
  else if (opp.rubro_requerido && productor.rubro &&
           opp.rubro_requerido.includes(productor.rubro.split(' ')[0]))
    rubroScore = 0.5;

  const score = rubroScore * 0.60 + 0.25 + (opp.monto <= 50000 ? 0.15 : 0.05);

  return {
    // Datos de la oportunidad
    opp_id: opp.id,
    titulo: opp.titulo,
    institucion: opp.institucion,
    monto: opp.monto,
    fecha_cierre: opp.fecha_cierre,
    rubro_requerido: opp.rubro_requerido,
    unspsc_code: opp.unspsc_code,
    url_fuente: opp.url_fuente,
    // Score
    score: Math.round(score * 100),
    // Datos del productor (para dynamic_variables)
    productor_id: productor.id,
    productor_nombre: productor.nombre,
    productor_rubro: productor.rubro,
    productor_telefono: productor.telefono,
    productor_ubicacion: productor.ubicacion,
    productor_capacidad: productor.capacidad,
    productor_voice_id: productor.voice_id_elevenlabs || '',
    // Resumen para ElevenLabs dynamic_variables
    oportunidad_resumen: `${opp.titulo} - ${opp.institucion} - $${Number(opp.monto).toLocaleString()} - Cierre: ${opp.fecha_cierre}.`
  };
});

const filtered = matches
  .filter(m => m.score >= 60)
  .sort((a, b) => b.score - a.score);

if (filtered.length === 0) {
  return [{ json: { matches_count: 0, productor_nombre: productor.nombre } }];
}

return filtered;
```

**Nota:** En n8n, un `return` con un array de objetos produce múltiples output items. Cada item con score >= 60 será procesado individualmente por los nodos siguientes.

### Node 6: IF — "score >= 60?"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.if` |
| **Conditions** | `score` >= `60` (Number) |
| **Mode** | `all` (todas las condiciones deben cumplirse, aunque solo hay una) |

**Outputs:**
- `true` (matches verdes) → Node 7
- `false` (no matches) → Node 10

### Node 7: Set — "Build ElevenLabs payload"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.set` |
| **Mode** | `RAW` (o `Fields`, pero `RAW` da control total sobre el body) |
| **Keep Output** | `false` (no conservar campos anteriores) |

**RAW JSON template:**

```json
{
  "agent_id": "agX7k2m9pQ4rL3zN8wB6vC1d",
  "phone_number": "{{ $json.productor_telefono }}",
  "dynamic_variables": {
    "nombre_productor": "{{ $json.productor_nombre }}",
    "rubro_negocio": "{{ $json.productor_rubro }}",
    "oportunidad_detectada": "{{ $json.oportunidad_resumen }}"
  }
}
```

### Node 8: HTTP Request — "POST to ElevenLabs"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.httpRequest` |
| **Method** | `POST` |
| **URL** | `https://api.elevenlabs.io/v1/convai/conversations` |
| **Authentication** | `Generic Credentials` → `Header Auth` |
| **Header Name** | `xi-api-key` |
| **Header Value** | `{{ $env.ELEVENLABS_API_KEY }}` |
| **Body Content Type** | `JSON` |
| **Body** | (toma del input del Node 7 — RAW JSON) |
| **Options > Retry on Fail** | `true` |
| **Max Retries** | `2` |
| **Retry Interval** | `2000` ms |
| **Ignore SSL Issues** | `false` |

**Conexión de error:**
- Output `error` → Node 9 (Code: "Call failed log")

### Node 9: Code — "Call failed log" (error branch)

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.code` |
| **Mode** | `runOnceForAllItems` |
| **Language** | JavaScript |

**Código JavaScript:**

```javascript
const errorMessage = $json.error || $json.message || 'Unknown error';
const productor = $json.productor_nombre || 'Unknown';
const telefono = $json.productor_telefono || 'Unknown';

console.log(`[ELEVENLABS FAIL] Productor: ${productor}, Telefono: ${telefono}, Error: ${errorMessage}`);

return [{
  json: {
    status: 'call_failed',
    productor_nombre: productor,
    productor_telefono: telefono,
    error: errorMessage,
    fallback_audio: 'audio-02-questions.mp3',
    timestamp: new Date().toISOString()
  }
}];
```

### Node 10: Code — "No matches log" (FALSE branch)

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.code` |
| **Mode** | `runOnceForAllItems` |
| **Language** | JavaScript |

**Código JavaScript:**

```javascript
const count = $json.matches_count || 0;
const productor = $json.productor_nombre || 'Unknown';

console.log(`[NO MATCHES] Productor: ${productor} — 0 oportunidades con score >= 60`);

return [{
  json: {
    status: 'no_matches',
    productor_nombre: productor,
    matches_count: 0,
    timestamp: new Date().toISOString()
  }
}];
```

### Node 11: NoOp — "Success log"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.noOp` |
| **Mode** | N/A |

Nodo de marcador visual. Indica que la llamada se inició exitosamente. Opcionalmente se puede reemplazar con un Code node que haga log.

---

## WORKFLOW 2: retar_decision (8 nodes)

**Propósito:** Recibir una `decision_descrita` desde el agente ElevenLabs (vía webhook), validarla, consultar OpenAI/gpt-4o-mini con el prompt de cofundador, insertar la decisión en Supabase, y devolver 3 preguntas críticas. Si algo falla, devolver preguntas de respaldo hardcodeadas.

### Conexión entre nodos (diagrama)

```
[Webhook: POST /retar-decision]
    |
    v
[Code: Validate input] --- ERROR (throw) ---> [Code: Serve fallback questions]
    |                                                    |
    v                                                    v
[HTTP Request: OpenAI] --- ERROR (retry) ---> [Code: Serve fallback questions]
    |
    v
[Code: Parse response]
    |
    v
[Postgres: INSERT into decisiones]
    |
    v
[Respond to Webhook: Return preguntas]

[Code: Serve fallback questions]
    |
    v
[Respond to Webhook: Return fallback]
```

### Node 1: Webhook — "POST /retar-decision"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.webhook` |
| **Webhook Name** | `retar-decision` |
| **Path** | `retar-decision` |
| **HTTP Method** | `POST` |
| **Response Mode** | `Last Node` |
| **Response Data** | `All Entries` |
| **Options > Raw Body** | `false` |
| **Options > Ignore Incoming Query** | `false` |

**Headers esperados (validados en el Code node, no en Webhook):**
- `Content-Type: application/json`
- `X-Compa-Webhook-Secret: whsec_compa_buildathon_2026`
- `Timeout: 25s` (configurado en Options)

**URL generada automáticamente por n8n:**
- Producción: `https://{WORKSPACE}.app.n8n.cloud/webhook/{ID}/retar-decision`
- Test: `https://{WORKSPACE}.app.n8n.cloud/webhook-test/{ID}/retar-decision`

### Node 2: Code — "Validate and normalize input"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.code` |
| **Mode** | `runOnceForAllItems` |
| **Language** | JavaScript |

**Código JavaScript:**

```javascript
const payload = $input.first().json;

// Validar webhook secret
const expectedSecret = 'whsec_compa_buildathon_2026';
const receivedSecret = $input.first().headers?.['x-compa-webhook-secret'];

if (receivedSecret !== expectedSecret) {
  throw new Error('Unauthorized: invalid webhook secret');
}

// Validar decision_descrita
const decisionDescrita = payload.decision_descrita;
if (!decisionDescrita || typeof decisionDescrita !== 'string') {
  throw new Error('Validation error: decision_descrita is required and must be a string');
}

if (decisionDescrita.trim().length < 10) {
  throw new Error('Validation error: decision_descrita must be at least 10 characters');
}

// Extraer contexto adicional (opcional, viene del agente ElevenLabs)
const conversationId = payload.conversation_id || ('conv_' + Date.now());
const nombreProductor = payload.nombre_productor || 'Productor';
const rubroNegocio = payload.rubro_negocio || 'general';
const capacidadProductor = payload.capacidad_productor || 'no especificada';
const experienciaEstado = payload.experiencia_estado || 'ninguna';

// Valores hardcodeados para demo (productor Vilma)
const oportunidadTitulo = payload.oportunidad_titulo || 'Servicio de Alimentacion Escolar';
const oportunidadInstitucion = payload.oportunidad_institucion || 'MINEDUCYT';
const oportunidadMonto = payload.oportunidad_monto || 48750;
const oportunidadCierre = payload.oportunidad_cierre || '2026-07-18';

return [{
  json: {
    decision_descrita: decisionDescrita.trim(),
    conversation_id: conversationId,
    nombre_productor: nombreProductor,
    rubro_negocio: rubroNegocio,
    capacidad_productor: capacidadProductor,
    experiencia_estado: experienciaEstado,
    oportunidad_titulo: oportunidadTitulo,
    oportunidad_institucion: oportunidadInstitucion,
    oportunidad_monto: oportunidadMonto,
    oportunidad_cierre: oportunidadCierre,
    // Timestamp para la DB
    recibido_en: new Date().toISOString()
  }
}];
```

### Node 3: HTTP Request — "POST to OpenAI"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.httpRequest` |
| **Method** | `POST` |
| **URL** | `https://api.openai.com/v1/chat/completions` |
| **Authentication** | `Generic Credentials` → `Header Auth` |
| **Header Name** | `Authorization` |
| **Header Value** | `Bearer {{ $env.OPENAI_API_KEY }}` |
| **Body Content Type** | `JSON` |
| **Options > Timeout** | `15000` ms (15s) |
| **Options > Retry on Fail** | `true` |
| **Max Retries** | `1` |
| **Retry Interval** | `2000` ms |

**RAW JSON body:**

```json
{
  "model": "gpt-4o-mini",
  "temperature": 0.3,
  "max_tokens": 500,
  "response_format": {
    "type": "json_schema",
    "json_schema": {
      "name": "cofundador_preguntas",
      "strict": true,
      "schema": {
        "type": "object",
        "properties": {
          "preguntas": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "minItems": 3,
            "maxItems": 3
          },
          "reasoning_trace": {
            "type": "string"
          }
        },
        "required": ["preguntas", "reasoning_trace"],
        "additionalProperties": false
      }
    }
  },
  "messages": [
    {
      "role": "system",
      "content": "# Role\nSos el \"cofundador\" de Compa — un socio exigente y pragmatico para pequenos productores salvadorenos que venden al Estado. Tu unica funcion es generar preguntas que pongan a prueba si una decision de negocio tiene sentido.\n\n# Output format\nDebes responder UNICAMENTE con un objeto JSON:\n{\n  \"reasoning_trace\": \"string - explicacion de tu razonamiento paso a paso\",\n  \"preguntas\": [\"pregunta 1\", \"pregunta 2\", \"pregunta 3\"]\n}\n\nCada pregunta debe ser una oracion directa en espanol salvadoreno (usa VOS: \"tenes\", \"podes\", \"decis\"), entre 10 y 25 palabras.\n\n# Rules\n1. Clasifica la decision del productor primero (inversion, capacidad, financiamiento, logistica, riesgo).\n2. Identifica los puntos ciegos mas probables segun la decision.\n3. Genera 3 preguntas que apunten a puntos ciegos DIFERENTES.\n4. Cada pregunta debe ser concreta al contexto del productor Y la oportunidad.\n5. La tercera pregunta debe ser la mas incomoda.\n\n# Conocimiento del contexto salvadoreno\n- El Estado paga entre 30 y 90 dias (Art. 108 LACAP).\n- La fianza de cumplimiento es del 10% del monto (Art. 92 LACAP).\n- RUPES es obligatorio para contratar con el Estado.\n- Las MYPE subestiman costos de fianza, retencion de IVA (13%) y Renta.\n- Muchos productores necesitan anticipo del 30% para comprar insumos.\n\n# Anti-hallucination\n- NO inventes numeros de articulos de ley que no existan.\n- NO uses datos que no esten en el contexto proporcionado.\n- NO des tu opinion. Solo genera preguntas.\n- NO generes mas ni menos de 3 preguntas."
    },
    {
      "role": "user",
      "content": "## Contexto del productor\n- Nombre: {{ $json.nombre_productor }}\n- Rubro: {{ $json.rubro_negocio }}\n- Capacidad: {{ $json.capacidad_productor }}\n- Experiencia con el Estado: {{ $json.experiencia_estado }}\n\n## Oportunidad relacionada\n- Titulo: {{ $json.oportunidad_titulo }}\n- Institucion: {{ $json.oportunidad_institucion }}\n- Monto: ${{ $json.oportunidad_monto }}\n- Fecha de cierre: {{ $json.oportunidad_cierre }}\n\n## Decision descrita por el productor\n\"{{ $json.decision_descrita }}\"\n\n---\n\nGenera exactamente 3 preguntas en formato JSON."
    }
  ]
}
```

**Conexión de error:**
- Output `error` → Node 6 (Code: "Serve fallback questions")

### Node 4: Code — "Parse Codex response"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.code` |
| **Mode** | `runOnceForAllItems` |
| **Language** | JavaScript |

**Código JavaScript:**

```javascript
const openaiResponse = $input.first().json;

// Parsear la respuesta de OpenAI
let parsed;
try {
  const content = openaiResponse.choices?.[0]?.message?.content;
  if (!content) throw new Error('Empty response from OpenAI');
  parsed = JSON.parse(content);
} catch (e) {
  throw new Error(`Failed to parse OpenAI response: ${e.message}`);
}

// Validar estructura
if (!parsed.preguntas || !Array.isArray(parsed.preguntas) || parsed.preguntas.length !== 3) {
  throw new Error(`Invalid response: expected 3 preguntas, got ${parsed.preguntas?.length || 0}`);
}

// Validar que cada pregunta sea un string no vacio
const validadas = parsed.preguntas.map((p, i) => {
  if (typeof p !== 'string' || p.trim().length === 0) {
    throw new Error(`Invalid response: pregunta ${i + 1} is empty`);
  }
  return p.trim();
});

// Preservar datos originales para la DB
const inputData = $input.all()[0].map(item => item.json);

return [{
  json: {
    preguntas: validadas,
    reasoning_trace: parsed.reasoning_trace || '',
    _fallback: false,
    // Datos para INSERT en Supabase
    conversation_id: inputData[0]?.conversation_id || 'unknown',
    decision_descrita: inputData[0]?.decision_descrita || '',
    nombre_productor: inputData[0]?.nombre_productor || '',
    recibido_en: inputData[0]?.recibido_en || new Date().toISOString(),
    procesado_en: new Date().toISOString()
  }
}];
```

### Node 5: Postgres — "INSERT into decisiones"

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.postgres` |
| **Operation** | `Insert` |
| **Schema** | `public` |
| **Table** | `decisiones` |
| **Columns** | `productor_id`, `oportunidad_id`, `decision_descrita`, `conversation_id`, `preguntas_generadas`, `reasoning_trace`, `respuesta_raw`, `es_fallback`, `creado_en` |

**Mapping de columnas** (usando el output del Node 4 y los datos originales):

| Columna | Valor |
|---|---|
| `productor_id` | `{{ $json.nombre_productor }}` (idealmente pasar el ID real desde el payload) |
| `oportunidad_id` | `{{ $json.conversation_id }}` |
| `decision_descrita` | `{{ $json.decision_descrita }}` |
| `conversation_id` | `{{ $json.conversation_id }}` |
| `preguntas_generadas` | `{{ JSON.stringify($json.preguntas) }}` |
| `reasoning_trace` | `{{ $json.reasoning_trace }}` |
| `respuesta_raw` | `{{ JSON.stringify({ preguntas: $json.preguntas, reasoning_trace: $json.reasoning_trace }) }}` |
| `es_fallback` | `false` |
| `creado_en` | `{{ $json.procesado_en }}` |

**Schema de la tabla `decisiones`:**

```sql
CREATE TABLE decisiones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  productor_id TEXT,
  oportunidad_id TEXT,
  decision_descrita TEXT NOT NULL,
  conversation_id TEXT,
  preguntas_generadas JSONB,
  reasoning_trace TEXT,
  respuesta_raw JSONB,
  es_fallback BOOLEAN DEFAULT false,
  creado_en TIMESTAMPTZ DEFAULT NOW()
);
```

### Node 6: Code — "Serve fallback questions" (error branch)

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.code` |
| **Mode** | `runOnceForAllItems` |
| **Language** | JavaScript |

**Código JavaScript:**

```javascript
// Extraer el error si existe
const errorDetail = $json?.error || $json?.message || 'Unknown error';
console.log(`[FALLBACK] Sirviendo preguntas de respaldo. Error: ${errorDetail}`);

// Preguntas hardcodeadas de respaldo (basadas en el contexto de Vilma)
const fallbackPreguntas = [
  "Ya calculaste cuanto te cuesta producir cada almuerzo?",
  "Tenes el flujo de caja para aguandar 90 dias sin cobrar?",
  "Que pasa si ganas y no podes cumplir?"
];

return [{
  json: {
    preguntas: fallbackPreguntas,
    reasoning_trace: "Preguntas de respaldo generadas localmente (fallback activado)",
    _fallback: true,
    error: errorDetail,
    procesado_en: new Date().toISOString()
  }
}];
```

### Node 7: Respond to Webhook — "Return preguntas" (success)

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.respondToWebhook` |
| **Respond With** | `JSON` |
| **Response Status Code** | `200` |
| **Response Body** | Use `Current Node Input` (RAW JSON) |

**RAW JSON template:**

```json
{
  "preguntas": "{{ $json.preguntas }}",
  "_fallback": "{{ $json._fallback }}"
}
```

O en modo RAW:

```json
{
  "preguntas": {{ JSON.stringify($json.preguntas) }},
  "_fallback": {{ $json._fallback }}
}
```

### Node 8: Respond to Webhook — "Return fallback preguntas" (error)

| Campo | Valor |
|---|---|
| **Node type** | `n8n-nodes-base.respondToWebhook` |
| **Respond With** | `JSON` |
| **Response Status Code** | `200` (siempre 200, aunque sea fallback, para que ElevenLabs no marque error) |
| **Response Body** | RAW JSON |

**RAW JSON template:**

```json
{
  "preguntas": {{ JSON.stringify($json.preguntas) }},
  "_fallback": true,
  "error": "{{ $json.error }}"
}
```

---

## Supabase Database Schema Completo

```sql
-- Tabla: productores
CREATE TABLE productores (
  id TEXT PRIMARY KEY,
  nombre TEXT NOT NULL,
  rubro TEXT NOT NULL,
  ubicacion TEXT,
  capacidad TEXT,
  telefono TEXT,
  dui TEXT,
  nit TEXT,
  fecha_cierre_oportunidad DATE,
  voice_id_elevenlabs TEXT DEFAULT 'g3pC3sr9iFcUwoSLvVLV',
  creado_en TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: oportunidades
CREATE TABLE oportunidades (
  id TEXT PRIMARY KEY,
  titulo TEXT NOT NULL,
  institucion TEXT NOT NULL,
  monto NUMERIC(12,2) NOT NULL,
  fecha_cierre DATE NOT NULL,
  rubro_requerido TEXT NOT NULL,
  unspsc_code TEXT,
  url_fuente TEXT,
  creado_en TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: match_oportunidades
CREATE TABLE match_oportunidades (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  productor_id TEXT REFERENCES productores(id),
  oportunidad_id TEXT REFERENCES oportunidades(id),
  score INTEGER NOT NULL CHECK (score >= 0 AND score <= 100),
  estado TEXT DEFAULT 'pendiente' CHECK (estado IN ('pendiente', 'contactado', 'interesado', 'no_interesado')),
  creado_en TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla: decisiones
CREATE TABLE decisiones (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  productor_id TEXT,
  oportunidad_id TEXT,
  decision_descrita TEXT NOT NULL,
  conversation_id TEXT,
  preguntas_generadas JSONB,
  reasoning_trace TEXT,
  respuesta_raw JSONB,
  es_fallback BOOLEAN DEFAULT false,
  creado_en TIMESTAMPTZ DEFAULT NOW()
);

-- Seed data: 1 productor
INSERT INTO productores (id, nombre, rubro, ubicacion, capacidad, telefono) VALUES
('prod-001', 'Vilma Jeanneth Guardado de Ayala', 'Alimentos y Bebidas', 'Canton El Zapote, San Juan Opico, La Libertad', '500 almuerzos/dia', '+50377234567');

-- Seed data: 5 oportunidades
INSERT INTO oportunidades (id, titulo, institucion, monto, fecha_cierre, rubro_requerido, unspsc_code, url_fuente) VALUES
('opp-001', 'Servicio de Alimentacion Escolar - Distrito 04-25', 'MINEDUCYT', 48750.00, '2026-07-18', 'Alimentos y Bebidas', '50200000', 'https://www.comprasal.gob.sv/licitaciones/lp-07-2026-mined'),
('opp-002', 'Servicio de Cafeteria - Edificio Central ANDA', 'ANDA', 28400.00, '2026-07-22', 'Alimentos y Bebidas', '50200000', 'https://www.comprasal.gob.sv/libre-gestion/lg-12-2026-anda'),
('opp-003', 'Confeccion de Uniformes - Hospital ISSS', 'ISSS', 12680.00, '2026-07-12', 'Textiles y Uniformes', '53000000', 'https://www.comprasal.gob.sv/licitaciones/li-03-2026-isss'),
('opp-004', 'Frutas/Vegetales Deshidratados - MAG', 'MAG', 3250.00, '2026-07-08', 'Alimentos y Bebidas', '51120000', 'https://www.comprasal.gob.sv/contrataciones/cd-05-2026-mag'),
('opp-005', 'Fabricacion Pupitres Metalicos - FISDL', 'FISDL', 152000.00, '2026-07-28', 'Mobiliario y Equipo', '56000000', 'https://www.comprasal.gob.sv/licitaciones/lp-02-2026-fisdl');
```

---

## Resumen de conexiones entre nodos

### Workflow 1: Oportunidades

| Desde | Hacia | Condición |
|---|---|---|
| Manual Trigger (1) | Merge | Siempre |
| Cron Trigger (2) | Merge | Siempre |
| Merge | Postgres: Read productores (3) | Siempre |
| Merge | Postgres: Read oportunidades (4) | Siempre |
| Postgres: Read productores (3) | Code: Match algorithm (5) | Input 0 |
| Postgres: Read oportunidades (4) | Code: Match algorithm (5) | Input 1 |
| Code: Match algorithm (5) | IF: score >= 60? (6) | Siempre |
| IF (6) — true | Set: Build payload (7) | score >= 60 |
| IF (6) — false | Code: No matches log (10) | score < 60 |
| Set: Build payload (7) | HTTP Request: ElevenLabs (8) | Siempre |
| HTTP Request (8) — success | NoOp: Success log (11) | HTTP 2xx |
| HTTP Request (8) — error | Code: Call failed log (9) | HTTP error |

### Workflow 2: retar_decision

| Desde | Hacia | Condición |
|---|---|---|
| Webhook: POST (1) | Code: Validate input (2) | Siempre |
| Code: Validate input (2) — success | HTTP Request: OpenAI (3) | Validación OK |
| Code: Validate input (2) — error | Code: Serve fallback (6) | Validación falla |
| HTTP Request: OpenAI (3) — success | Code: Parse response (4) | HTTP 2xx |
| HTTP Request: OpenAI (3) — error | Code: Serve fallback (6) | HTTP error / timeout |
| Code: Parse response (4) | Postgres: INSERT (5) | Parseo OK |
| Postgres: INSERT (5) | Respond to Webhook: Return (7) | INSERT OK |
| Code: Serve fallback (6) | Respond to Webhook: Fallback (8) | Siempre |

---

## Notas importantes para n8n Cloud

1. **Conexion a Supabase:** Usar `n8n-nodes-base.postgres` con credentials tipo `Postgres`. La connection string es: `postgresql://{user}:{password}@{host}:{port}/{database}?sslmode=require`

2. **Multiple triggers en Workflow 1:** n8n soporta múltiples nodos trigger en un workflow. Para ejecutar con Manual Trigger sin esperar al cron, ambos triggers deben estar conectados al mismo workflow. Usar un nodo `Merge` con mode `Wait for Both` si se necesita que ambos eventos consoliden datos, o simplemente conectar ambos al primer Postgres node.

3. **Error handling:** n8n permite conectar el output `error` de un nodo directamente a otro nodo. Esto se configura en el canvas arrastrando desde el círculo rojo de error del nodo. No se necesita un bloque try/catch dentro del código.

4. **Fallback de Supabase (si la DB no responde):** Si se desea un respaldo ante falla de conexion a Supabase, se puede insertar un Code node de fallback entre los Postgres nodes y el Code de matching, similar al fallback de Google Sheets original:

```javascript
const dbData = $input.first().json;
if (!dbData || (Array.isArray(dbData) && dbData.length === 0)) {
  // Leer de archivo JSON local
  const fs = require('fs');
  const fallbackPath = require('path').join(__dirname, '..', 'data', 'fallback.json');
  return JSON.parse(fs.readFileSync(fallbackPath, 'utf8'));
}
return $input.all();
```

5. **Demo execution:** En el demo en vivo, usar el boton "Execute Workflow" en el canvas de n8n, que activa el Manual Trigger. Los nodos se iluminan uno por uno en tiempo real.
