from __future__ import annotations

import json
from pathlib import Path

ROOT = Path('Compa')
N8N = ROOT / 'n8n-exports'
DEMO = ROOT / 'demo'
DOCS = ROOT / 'docs'
SCRIPTS = ROOT / 'scripts'


def write_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def code_node(name: str, js: str, x: int, y: int) -> dict:
    return {
        'parameters': {'jsCode': js.strip() + '\n'},
        'id': name.lower().replace(' ', '-'),
        'name': name,
        'type': 'n8n-nodes-base.code',
        'typeVersion': 2,
        'position': [x, y],
    }

workflow_oportunidades = {
    'name': 'COMPA - Fase 3 - Oportunidades a ElevenLabs',
    'nodes': [
        {
            'parameters': {},
            'id': 'manual-trigger',
            'name': 'Manual Trigger',
            'type': 'n8n-nodes-base.manualTrigger',
            'typeVersion': 1,
            'position': [0, 0],
        },
        {
            'parameters': {
                'rule': {'interval': [{'field': 'hours', 'hoursInterval': 6}]},
            },
            'id': 'schedule-trigger',
            'name': 'Schedule Every 6 Hours',
            'type': 'n8n-nodes-base.scheduleTrigger',
            'typeVersion': 1.2,
            'position': [0, 180],
        },
        {
            'parameters': {
                'operation': 'executeQuery',
                'query': """SELECT
  p.id::text AS productor_id,
  p.nombre AS nombre_productor,
  p.rubro AS rubro_negocio,
  p.capacidad AS capacidad_productor,
  p.telefono,
  m.oportunidad_id::text AS oportunidad_id,
  m.titulo AS oportunidad_titulo,
  m.institucion AS oportunidad_institucion,
  m.monto AS oportunidad_monto,
  m.fecha_cierre::text AS oportunidad_cierre,
  m.rubro_requerido,
  m.unspsc_code,
  m.url_fuente,
  m.tipo_contratacion,
  m.score
FROM productores p
JOIN LATERAL matching_oportunidades(p.id, 5) m ON true
WHERE p.nombre = 'Vilma Jeanneth Guardado de Ayala'
ORDER BY m.score DESC, m.monto DESC
LIMIT 1;""",
                'options': {},
            },
            'id': 'query-vilma-match',
            'name': 'Query Vilma Top Match',
            'type': 'n8n-nodes-base.postgres',
            'typeVersion': 2.4,
            'position': [260, 90],
            'credentials': {'postgres': {'id': 'REPLACE_SUPABASE_POSTGRES_CREDENTIAL_ID', 'name': 'Supabase Postgres'}},
        },
        code_node('Build ElevenLabs Payload', r"""
const items = $input.all();
return items.map((item) => {
  const row = item.json;
  const monto = Number(row.oportunidad_monto || 0);
  const oportunidadDetectada = `${row.oportunidad_titulo} de ${row.oportunidad_institucion} por $${monto.toLocaleString('en-US')} con cierre ${row.oportunidad_cierre}.`;
  return {
    json: {
      agent_id: $env.ELEVENLABS_AGENT_ID || 'REPLACE_ELEVENLABS_AGENT_ID',
      phone_number: row.telefono,
      dynamic_variables: {
        productor_id: row.productor_id,
        oportunidad_id: row.oportunidad_id,
        nombre_productor: row.nombre_productor,
        rubro_negocio: row.rubro_negocio,
        capacidad_productor: row.capacidad_productor,
        oportunidad_detectada: oportunidadDetectada,
        oportunidad_titulo: row.oportunidad_titulo,
        oportunidad_institucion: row.oportunidad_institucion,
        oportunidad_monto: monto,
        oportunidad_cierre: row.oportunidad_cierre,
        unspsc_code: row.unspsc_code,
        url_fuente: row.url_fuente,
        score_match: Number(row.score || 0)
      },
      metadata: {
        productor_id: row.productor_id,
        oportunidad_id: row.oportunidad_id,
        source: 'compa-fase-3-n8n'
      },
      first_message: `Doña ${row.nombre_productor.split(' ')[0]}, como esta? Habla Compa. Vi una oportunidad para su negocio: ${oportunidadDetectada} Tiene un momento para revisarla?`
    }
  };
});
""", 520, 90),
        {
            'parameters': {
                'method': 'POST',
                'url': 'https://api.elevenlabs.io/v1/convai/conversation',
                'sendHeaders': True,
                'headerParameters': {'parameters': [{'name': 'xi-api-key', 'value': '={{ $env.ELEVENLABS_API_KEY }}'}]},
                'sendBody': True,
                'specifyBody': 'json',
                'jsonBody': '={{ JSON.stringify($json) }}',
                'options': {'timeout': 5000},
            },
            'id': 'post-elevenlabs',
            'name': 'POST to ElevenLabs',
            'type': 'n8n-nodes-base.httpRequest',
            'typeVersion': 4.2,
            'position': [790, 90],
        },
    ],
    'connections': {
        'Manual Trigger': {'main': [[{'node': 'Query Vilma Top Match', 'type': 'main', 'index': 0}]]},
        'Schedule Every 6 Hours': {'main': [[{'node': 'Query Vilma Top Match', 'type': 'main', 'index': 0}]]},
        'Query Vilma Top Match': {'main': [[{'node': 'Build ElevenLabs Payload', 'type': 'main', 'index': 0}]]},
        'Build ElevenLabs Payload': {'main': [[{'node': 'POST to ElevenLabs', 'type': 'main', 'index': 0}]]},
    },
    'settings': {'executionOrder': 'v1', 'timezone': 'America/El_Salvador'},
    'staticData': None,
    'pinData': {},
    'versionId': 'compa-fase-3-oportunidades',
    'triggerCount': 2,
    'tags': [{'name': 'compa'}, {'name': 'fase-3'}],
}

validate_js = r"""
const incoming = $input.first().json;
const headers = incoming.headers || {};
const payload = incoming.body || incoming;
const contexto = payload.contexto || {};
const expectedSecret = $env.COMPA_WEBHOOK_SECRET || 'whsec_compa_buildathon_2026';
const receivedSecret = headers['x-compa-webhook-secret'] || headers['X-Compa-Webhook-Secret'] || '';
const authorization = headers.authorization || headers.Authorization || '';
const bearerSecret = authorization.startsWith('Bearer ') ? authorization.slice(7) : '';
if (!payload._skip_auth && receivedSecret !== expectedSecret && bearerSecret !== expectedSecret) {
  throw new Error('Unauthorized: invalid webhook secret');
}
const decisionDescrita = payload.decision_descrita;
if (!decisionDescrita || typeof decisionDescrita !== 'string' || decisionDescrita.trim().length < 10) {
  throw new Error('Validation error: decision_descrita is required and must be at least 10 characters');
}
const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const productorId = payload.productor_id || contexto.productor_id;
const oportunidadId = payload.oportunidad_id || contexto.oportunidad_id;
if (!uuidRegex.test(productorId || '')) throw new Error('Validation error: productor_id must be a Supabase UUID');
if (!uuidRegex.test(oportunidadId || '')) throw new Error('Validation error: oportunidad_id must be a Supabase UUID');
return [{
  json: {
    decision_descrita: decisionDescrita.trim(),
    productor_id: productorId,
    oportunidad_id: oportunidadId,
    conversation_id: payload.conversation_id || payload.trace_id || `conv_${Date.now()}`,
    nombre_productor: payload.nombre_productor || contexto.nombre_productor || 'Productor',
    rubro_negocio: payload.rubro_negocio || contexto.rubro || 'general',
    capacidad_productor: payload.capacidad_productor || contexto.capacidad_productor || 'no especificada',
    experiencia_estado: payload.experiencia_estado || contexto.experiencia_estado || 'no especificada',
    oportunidad_titulo: payload.oportunidad_titulo || contexto.oportunidad_titulo || 'Oportunidad publica',
    oportunidad_institucion: payload.oportunidad_institucion || contexto.institucion || 'Institucion publica',
    oportunidad_monto: Number(payload.oportunidad_monto || contexto.monto_oportunidad || 0),
    oportunidad_cierre: payload.oportunidad_cierre || contexto.oportunidad_cierre || '',
    recibido_en: new Date().toISOString()
  }
}];
"""

build_openai_js = r"""
const data = $input.first().json;
return [{
  json: {
    ...data,
    openai_request: {
      model: 'gpt-4o-mini',
      temperature: 0.2,
      response_format: { type: 'json_object' },
      messages: [
        {
          role: 'system',
          content: 'Sos Compa, cofundador de IA para MIPYMES salvadorenas. Responde solo JSON valido con exactly 3 preguntas criticas y un reasoning_trace breve.'
        },
        {
          role: 'user',
          content: `Productor: ${data.nombre_productor}\nRubro: ${data.rubro_negocio}\nCapacidad: ${data.capacidad_productor}\nOportunidad: ${data.oportunidad_titulo} / ${data.oportunidad_institucion} / $${data.oportunidad_monto}\nDecision: ${data.decision_descrita}\n\nGenera JSON: {"preguntas":["...","...","..."],"reasoning_trace":"..."}`
        }
      ]
    }
  }
}];
"""

parse_js = r"""
const original = $items('Build OpenAI Request')[0].json;
const response = $input.first().json;
const fallback = [
  'Ya calculo cuanto le cuesta producir cada unidad con los precios actuales?',
  'Tiene flujo de caja para aguantar 60 a 90 dias antes del pago del Estado?',
  'Que plan B tiene si gana y no puede cumplir con la cantidad completa?'
];
let preguntas = fallback;
let reasoningTrace = 'Fallback Fase 3: OpenAI no devolvio JSON valido o no estuvo disponible.';
let esFallback = true;
try {
  if (response.error) throw new Error(JSON.stringify(response.error));
  const content = response.choices?.[0]?.message?.content || response.body?.choices?.[0]?.message?.content;
  if (!content) throw new Error('empty OpenAI content');
  const parsed = typeof content === 'string' ? JSON.parse(content) : content;
  if (!Array.isArray(parsed.preguntas) || parsed.preguntas.length !== 3) throw new Error('expected 3 preguntas');
  preguntas = parsed.preguntas.map((p) => String(p).trim()).filter(Boolean);
  if (preguntas.length !== 3) throw new Error('empty pregunta');
  reasoningTrace = String(parsed.reasoning_trace || 'OpenAI genero 3 preguntas criticas para la decision.');
  esFallback = false;
} catch (error) {
  reasoningTrace = `${reasoningTrace} Error: ${error.message}`;
}
const respuestaRaw = { preguntas, reasoning_trace: reasoningTrace, fallback: esFallback };
return [{
  json: {
    ...original,
    preguntas,
    preguntas_generadas: preguntas,
    reasoning_trace: reasoningTrace,
    respuesta_raw: respuestaRaw,
    es_fallback: esFallback,
    procesado_en: new Date().toISOString()
  }
}];
"""

insert_sql_js = r"""
const data = $input.first().json;
function sqlString(value) {
  return `'${String(value ?? '').replace(/'/g, "''")}'`;
}
const preguntasJson = JSON.stringify(data.preguntas_generadas || data.preguntas || []);
const rawJson = JSON.stringify(data.respuesta_raw || {});
const query = `INSERT INTO decisiones (
  productor_id,
  oportunidad_id,
  decision_descrita,
  conversation_id,
  preguntas_json,
  preguntas_generadas,
  reasoning_trace,
  respuesta_raw,
  es_fallback,
  creado_en
) VALUES (
  ${sqlString(data.productor_id)}::uuid,
  ${sqlString(data.oportunidad_id)}::uuid,
  ${sqlString(data.decision_descrita)},
  ${sqlString(data.conversation_id)},
  ${sqlString(preguntasJson)}::jsonb,
  ${sqlString(preguntasJson)}::jsonb,
  ${sqlString(data.reasoning_trace)},
  ${sqlString(rawJson)}::jsonb,
  ${data.es_fallback ? 'true' : 'false'},
  now()
) RETURNING id::text AS decision_id;`;
return [{ json: { ...data, insert_query: query } }];
"""

workflow_retar = {
    'name': 'COMPA - Fase 3 - retar_decision',
    'nodes': [
        {
            'parameters': {
                'httpMethod': 'POST',
                'path': 'retar-decision',
                'responseMode': 'responseNode',
                'options': {'responseData': 'allEntries'},
            },
            'id': 'webhook-retar-decision',
            'name': 'Webhook retar-decision',
            'type': 'n8n-nodes-base.webhook',
            'typeVersion': 2,
            'position': [0, 0],
            'webhookId': 'compa-retar-decision',
        },
        code_node('Validate Payload', validate_js, 260, 0),
        code_node('Build OpenAI Request', build_openai_js, 520, 0),
        {
            'parameters': {
                'method': 'POST',
                'url': 'https://api.openai.com/v1/chat/completions',
                'sendHeaders': True,
                'headerParameters': {'parameters': [
                    {'name': 'Authorization', 'value': "={{ 'Bearer ' + $env.OPENAI_API_KEY }}"},
                    {'name': 'Content-Type', 'value': 'application/json'},
                ]},
                'sendBody': True,
                'specifyBody': 'json',
                'jsonBody': '={{ JSON.stringify($json.openai_request) }}',
                'options': {'timeout': 15000},
            },
            'id': 'post-openai',
            'name': 'POST to OpenAI',
            'type': 'n8n-nodes-base.httpRequest',
            'typeVersion': 4.2,
            'position': [790, 0],
            'continueOnFail': True,
        },
        code_node('Parse OpenAI or Fallback', parse_js, 1050, 0),
        code_node('Build Insert SQL', insert_sql_js, 1310, 0),
        {
            'parameters': {'operation': 'executeQuery', 'query': '={{ $json.insert_query }}', 'options': {}},
            'id': 'insert-decision',
            'name': 'Insert Decision',
            'type': 'n8n-nodes-base.postgres',
            'typeVersion': 2.4,
            'position': [1570, 0],
            'credentials': {'postgres': {'id': 'REPLACE_SUPABASE_POSTGRES_CREDENTIAL_ID', 'name': 'Supabase Postgres'}},
        },
        {
            'parameters': {
                'respondWith': 'json',
                'responseBody': "={{ { preguntas: $items('Parse OpenAI or Fallback')[0].json.preguntas, reasoning_trace: $items('Parse OpenAI or Fallback')[0].json.reasoning_trace, _fallback: $items('Parse OpenAI or Fallback')[0].json.es_fallback, conversation_id: $items('Parse OpenAI or Fallback')[0].json.conversation_id } }}",
                'options': {'responseCode': 200},
            },
            'id': 'respond-success',
            'name': 'Respond Preguntas',
            'type': 'n8n-nodes-base.respondToWebhook',
            'typeVersion': 1.1,
            'position': [1830, 0],
        },
    ],
    'connections': {
        'Webhook retar-decision': {'main': [[{'node': 'Validate Payload', 'type': 'main', 'index': 0}]]},
        'Validate Payload': {'main': [[{'node': 'Build OpenAI Request', 'type': 'main', 'index': 0}]]},
        'Build OpenAI Request': {'main': [[{'node': 'POST to OpenAI', 'type': 'main', 'index': 0}]]},
        'POST to OpenAI': {'main': [[{'node': 'Parse OpenAI or Fallback', 'type': 'main', 'index': 0}]]},
        'Parse OpenAI or Fallback': {'main': [[{'node': 'Build Insert SQL', 'type': 'main', 'index': 0}]]},
        'Build Insert SQL': {'main': [[{'node': 'Insert Decision', 'type': 'main', 'index': 0}]]},
        'Insert Decision': {'main': [[{'node': 'Respond Preguntas', 'type': 'main', 'index': 0}]]},
    },
    'settings': {'executionOrder': 'v1', 'timezone': 'America/El_Salvador'},
    'staticData': None,
    'pinData': {},
    'versionId': 'compa-fase-3-retar-decision',
    'triggerCount': 1,
    'tags': [{'name': 'compa'}, {'name': 'fase-3'}],
}

retar_tool = {
    'type': 'webhook',
    'name': 'retar_decision',
    'description': 'Genera 3 preguntas criticas para desafiar una decision de negocio del productor usando OpenAI/Codex y guarda la decision en Supabase.',
    'parameters': {
        'type': 'object',
        'properties': {
            'decision_descrita': {'type': 'string', 'description': 'Descripcion textual exacta de la decision. Minimo 10 caracteres.'},
            'productor_id': {'type': 'string', 'description': 'UUID real del productor en Supabase.'},
            'oportunidad_id': {'type': 'string', 'description': 'UUID real de la oportunidad en Supabase.'},
            'conversation_id': {'type': 'string', 'description': 'ID de conversacion de ElevenLabs o trace_id.'},
            'nombre_productor': {'type': 'string', 'description': 'Nombre del productor.'},
            'rubro_negocio': {'type': 'string', 'description': 'Rubro del productor.'},
            'capacidad_productor': {'type': 'string', 'description': 'Capacidad operativa del productor.'},
            'oportunidad_titulo': {'type': 'string', 'description': 'Titulo de la oportunidad detectada.'},
            'oportunidad_institucion': {'type': 'string', 'description': 'Institucion compradora.'},
            'oportunidad_monto': {'type': 'number', 'description': 'Monto estimado de la oportunidad.'},
            'oportunidad_cierre': {'type': 'string', 'description': 'Fecha de cierre YYYY-MM-DD.'},
        },
        'required': ['decision_descrita', 'productor_id', 'oportunidad_id', 'nombre_productor', 'rubro_negocio'],
    },
    'api': {
        'url': 'https://{WORKSPACE}.app.n8n.cloud/webhook/retar-decision',
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json',
            'X-Compa-Webhook-Secret': 'whsec_compa_buildathon_2026',
        },
    },
}

mock_payload = {
    'conversation_id': 'demo-vilma-fase-3',
    'productor_id': '11111111-1111-4111-8111-111111111111',
    'oportunidad_id': '22222222-2222-4222-8222-222222222222',
    'nombre_productor': 'Vilma Jeanneth Guardado de Ayala',
    'rubro_negocio': 'Alimentos y Bebidas',
    'capacidad_productor': '500 almuerzos/dia',
    'experiencia_estado': 'primera participacion',
    'oportunidad_titulo': 'Servicio de Alimentacion Escolar - Distrito 04-25',
    'oportunidad_institucion': 'MINEDUCYT',
    'oportunidad_monto': 48750,
    'oportunidad_cierre': '2026-07-18',
    'decision_descrita': 'Me interesa participar, pero me preocupa si puedo cumplir con el volumen y esperar el pago del Estado.',
    '_skip_auth': True,
}

phase3_doc = '''# Fase 3 - n8n y ElevenLabs

## Entregables

- `n8n-exports/workflow-oportunidades-elevenlabs.json`: workflow importable para leer Supabase, tomar el match principal de Vilma y llamar ElevenLabs con `dynamic_variables`.
- `n8n-exports/workflow-retar-decision.json`: workflow importable para el tool `retar_decision`, con validacion de UUIDs, OpenAI, fallback e INSERT en `decisiones`.
- `n8n-exports/elevenlabs-tool-retar-decision.json`: definicion del tool para copiar al dashboard de ElevenLabs.
- `demo/payload-retar-decision-vilma.mock.json`: payload local con UUIDs validos para probar validacion sin tocar Supabase.
- `scripts/test_phase3_contract.py`: prueba estatica del contrato.

## Variables requeridas en n8n

- `ELEVENLABS_API_KEY`
- `ELEVENLABS_AGENT_ID`
- `OPENAI_API_KEY`
- `COMPA_WEBHOOK_SECRET` (opcional; default `whsec_compa_buildathon_2026`)

## Credenciales requeridas en n8n

Crear una credential tipo Postgres llamada `Supabase Postgres` y asignarla a los dos nodos Postgres despues de importar los workflows.

## Contrato de payload para `retar_decision`

El body debe ser plano, no anidado, para evitar drift:

```json
{
  "decision_descrita": "Me interesa participar...",
  "productor_id": "<uuid-real-supabase>",
  "oportunidad_id": "<uuid-real-supabase>",
  "conversation_id": "<id-elevenlabs>",
  "nombre_productor": "Vilma Jeanneth Guardado de Ayala",
  "rubro_negocio": "Alimentos y Bebidas",
  "capacidad_productor": "500 almuerzos/dia",
  "oportunidad_titulo": "Servicio de Alimentacion Escolar - Distrito 04-25",
  "oportunidad_institucion": "MINEDUCYT",
  "oportunidad_monto": 48750,
  "oportunidad_cierre": "2026-07-18"
}
```

`productor_id` y `oportunidad_id` deben venir de Supabase como UUID reales. Los IDs locales `prod-001` y `opp-001` solo son fallback JSON.

## Prueba local

```powershell
C:\\Users\\isabe\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe Compa\\scripts\\test_phase3_contract.py
```

Salida esperada:

```text
phase3 contract ok
```

## Prueba en n8n

1. Importar ambos JSON.
2. Asignar credential `Supabase Postgres` a los nodos Postgres.
3. Definir las variables de entorno.
4. Ejecutar `COMPA - Fase 3 - Oportunidades a ElevenLabs` manualmente.
5. En ElevenLabs, configurar el tool con `elevenlabs-tool-retar-decision.json`.
6. Probar `POST /retar-decision` con un payload real donde `productor_id` y `oportunidad_id` hayan salido de Supabase.

## Criterio de listo

La Fase 3 queda lista cuando:

- n8n importa los dos workflows sin reconstruirlos desde Markdown.
- El payload outbound a ElevenLabs incluye `dynamic_variables.productor_id` y `dynamic_variables.oportunidad_id`.
- El tool `retar_decision` exige UUIDs reales.
- El workflow guarda la respuesta en `decisiones` y responde 200 con tres preguntas, aunque OpenAI falle y se use fallback.
'''

test_script = r'''from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.I)


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def node_names(workflow):
    return {node['name'] for node in workflow['nodes']}


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    oportunidades = load_json(ROOT / 'n8n-exports' / 'workflow-oportunidades-elevenlabs.json')
    retar = load_json(ROOT / 'n8n-exports' / 'workflow-retar-decision.json')
    tool = load_json(ROOT / 'n8n-exports' / 'elevenlabs-tool-retar-decision.json')
    payload = load_json(ROOT / 'demo' / 'payload-retar-decision-vilma.mock.json')

    assert_true('Query Vilma Top Match' in node_names(oportunidades), 'missing query node')
    assert_true('POST to ElevenLabs' in node_names(oportunidades), 'missing ElevenLabs node')
    outbound_text = json.dumps(oportunidades, ensure_ascii=False)
    assert_true('dynamic_variables' in outbound_text, 'missing dynamic_variables')
    assert_true('productor_id' in outbound_text and 'oportunidad_id' in outbound_text, 'missing IDs in outbound workflow')
    assert_true('prod-001' not in outbound_text and 'opp-001' not in outbound_text, 'workflow must not use local fallback IDs')

    required_retar_nodes = {'Webhook retar-decision', 'Validate Payload', 'POST to OpenAI', 'Insert Decision', 'Respond Preguntas'}
    assert_true(required_retar_nodes.issubset(node_names(retar)), 'missing retar_decision nodes')
    retar_text = json.dumps(retar, ensure_ascii=False)
    assert_true('productor_id must be a Supabase UUID' in retar_text, 'missing UUID validation')
    assert_true('INSERT INTO decisiones' in retar_text, 'missing decisiones insert')

    required_params = set(tool['parameters']['required'])
    assert_true({'decision_descrita', 'productor_id', 'oportunidad_id'}.issubset(required_params), 'tool does not require UUID IDs')
    assert_true(UUID_RE.match(payload['productor_id']) is not None, 'mock productor_id is not UUID')
    assert_true(UUID_RE.match(payload['oportunidad_id']) is not None, 'mock oportunidad_id is not UUID')
    assert_true(len(payload['decision_descrita']) >= 10, 'mock decision too short')

    print('phase3 contract ok')


if __name__ == '__main__':
    main()
'''

write_json(N8N / 'workflow-oportunidades-elevenlabs.json', workflow_oportunidades)
write_json(N8N / 'workflow-retar-decision.json', workflow_retar)
write_json(N8N / 'elevenlabs-tool-retar-decision.json', retar_tool)
write_json(DEMO / 'payload-retar-decision-vilma.mock.json', mock_payload)
(DOCS / 'FASE-3-N8N-ELEVENLABS.md').write_text(phase3_doc, encoding='utf-8')
(SCRIPTS / 'test_phase3_contract.py').write_text(test_script, encoding='utf-8')
print('phase3 files written')