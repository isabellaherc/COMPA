from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path('Compa')
LEGAL_ROOT = ROOT / 'DocumentacionLegal'
DATA = ROOT / 'data'
DOCS = ROOT / 'docs'
N8N = ROOT / 'n8n-exports'
DEMO = ROOT / 'demo'
SCRIPTS = ROOT / 'scripts'
SCHEMA = ROOT / 'supabase-schema.sql'


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def rel(path: Path) -> str:
    return path.as_posix()


def legal_rel(path: Path) -> str:
    return rel(path.relative_to(ROOT))


def classify_template(path: Path) -> str:
    name = path.name.lower()
    if name.endswith('.pdf') and 'persona-natural-apoderado' in name:
        return 'declaracion_usuario'
    if name.endswith('.pdf') and 'persona-natural' in name:
        return 'declaracion_usuario'
    if name.endswith('.pdf') and 'persona-juridica-apoderado' in name:
        return 'declaracion_usuario'
    if name.endswith('.pdf') and 'persona-juridica' in name:
        return 'declaracion_usuario'
    if name.endswith('.docx') and name.startswith('des-'):
        return 'documento_estandar_generable'
    return 'plantilla_usuario'


def build_manifests() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    template_files: list[dict[str, Any]] = []
    kb_files: list[dict[str, Any]] = []
    for path in sorted(LEGAL_ROOT.rglob('*')):
        if not path.is_file():
            continue
        entry = {
            'archivo': path.name,
            'path': legal_rel(path),
            'extension': path.suffix.lower().lstrip('.'),
            'bytes': path.stat().st_size,
        }
        parts = {part.lower() for part in path.parts}
        if any('documentación-usuario' in part.lower() or 'documentacion-usuario' in part.lower() for part in path.parts):
            template_files.append({**entry, 'uso': classify_template(path), 'subir_a_rag': False})
        else:
            area = 'repositorio_legal'
            if any('leyes y reglamentos' in part.lower() for part in path.parts):
                area = 'leyes_y_reglamentos'
            elif any('lineamientos' in part.lower() for part in path.parts):
                area = 'lineamientos'
            elif any('políticas' in part.lower() or 'politicas' in part.lower() for part in path.parts):
                area = 'politicas'
            kb_files.append({**entry, 'area': area, 'subir_a_rag': path.suffix.lower() in {'.pdf', '.txt'}})
    return template_files, kb_files


def update_schema(template_files: list[dict[str, Any]]) -> None:
    text = SCHEMA.read_text(encoding='utf-8-sig')
    text = text.replace('plantilla_id    UUID REFERENCES plantillas_documentos(id),', 'plantilla_id    UUID REFERENCES plantillas_documentos(id) ON DELETE SET NULL,')

    template_by_name = {item['archivo']: item['path'] for item in template_files}
    rows = [
        (
            'Declaración Jurada Persona Natural',
            'declaracion_jurada_persona_natural',
            '["nombre","dui","nit","direccion","telefono","rubro","fecha"]',
            'https://dinac.gob.sv/documentos/persona-natural',
            template_by_name['PERSONA-NATURAL.pdf'],
        ),
        (
            'Declaración Jurada Persona Natural con Apoderado',
            'declaracion_jurada_apoderado_persona_natural',
            '["nombre_apoderado","dui_apoderado","nombre_representado","dui_representado","direccion","telefono","rubro","fecha"]',
            'https://dinac.gob.sv/documentos/persona-natural-apoderado',
            template_by_name['PERSONA-NATURAL-APODERADO.pdf'],
        ),
        (
            'Declaración Jurada Persona Jurídica',
            'declaracion_jurada_persona_juridica',
            '["nombre_empresa","nit","nombre_representante","dui_representante","direccion","telefono","rubro","fecha"]',
            'https://dinac.gob.sv/documentos/persona-juridica',
            template_by_name['PERSONA-JURIDICA.pdf'],
        ),
        (
            'Declaración Jurada Persona Jurídica con Apoderado',
            'declaracion_jurada_apoderado_persona_juridica',
            '["nombre_apoderado","dui_apoderado","nombre_empresa","nit","nombre_representante","dui_representante","direccion","telefono","rubro","fecha"]',
            'https://dinac.gob.sv/documentos/persona-juridica-apoderado',
            template_by_name['PERSONA-JURIDICA-APODERADO.pdf'],
        ),
        (
            'Documento Estándar de Contratación Directa',
            'documento_estandar_contratacion_directa',
            '["nombre","dui","nit","direccion","oportunidad_titulo","institucion","monto","fecha"]',
            'https://dinac.gob.sv/documentos/contratacion-directa',
            template_by_name['DES-2025-001-Documento-Estandar-de-contratacion-directa-version-word.docx'],
        ),
        (
            'Documento Estándar de Comparación de Precios - Bienes y Servicios',
            'documento_estandar_comparacion_precios_bienes_servicios',
            '["nombre","dui","nit","direccion","oportunidad_titulo","institucion","monto","items","precios_unitarios","fecha"]',
            'https://dinac.gob.sv/documentos/comparacion-precios-bienes-servicios',
            template_by_name['DES-2024-004.-Documento-Estandar-Comparacion-de-Precios.-Bienes-y-Servicios.docx'],
        ),
        (
            'Formulario de Carta Compromiso',
            'carta_compromiso',
            '["nombre","dui","nit","direccion","oportunidad_titulo","institucion","monto","fecha"]',
            'https://dinac.gob.sv/documentos/carta-compromiso',
            template_by_name['DES-2025-001-Documento-Estandar-de-contratacion-directa-version-word.docx'],
        ),
        (
            'Formulario de Desglose de Precios',
            'desglose_precios',
            '["nombre","nit","oportunidad_titulo","items","precios_unitarios","fecha"]',
            'https://dinac.gob.sv/documentos/desglose-precios',
            template_by_name['DES-2024-004.-Documento-Estandar-Comparacion-de-Precios.-Bienes-y-Servicios.docx'],
        ),
    ]

    def sql_quote(value: str) -> str:
        return "'" + value.replace("'", "''") + "'"

    values = []
    for nombre, tipo, campos, url, path in rows:
        values.append(
            "(\n"
            f"    {sql_quote(nombre)},\n"
            f"    {sql_quote(tipo)},\n"
            f"    {sql_quote(campos)}::jsonb,\n"
            f"    {sql_quote(url)},\n"
            f"    {sql_quote(path)}\n"
            ")"
        )

    seed = (
        "-- 11.3 SEED: Plantillas generables para usuarios (Documentación-usuario)\n"
        "--      Nota: Documentación-usuario contiene plantillas/formularios generables.\n"
        "--      Leyes, lineamientos y políticas son repositorio legal/RAG, no plantillas.\n"
        "INSERT INTO plantillas_documentos (nombre, tipo, campos_requeridos, url_original_dinac, path_template) VALUES\n"
        + ",\n".join(values)
        + "\nON CONFLICT (tipo) DO UPDATE SET\n"
        "    nombre = EXCLUDED.nombre,\n"
        "    campos_requeridos = EXCLUDED.campos_requeridos,\n"
        "    url_original_dinac = EXCLUDED.url_original_dinac,\n"
        "    path_template = EXCLUDED.path_template;"
    )

    pattern = re.compile(r"-- 11\.3 SEED: Plantillas disponibles.*?;", re.DOTALL)
    if not pattern.search(text):
        raise RuntimeError('No se encontro seed legal en supabase-schema.sql')
    text = pattern.sub(seed, text, count=1)
    SCHEMA.write_text(text, encoding='utf-8')


def build_legal_workflow() -> dict[str, Any]:
    def code_node(name: str, js: str, x: int, y: int) -> dict[str, Any]:
        return {
            'parameters': {'jsCode': js.strip() + '\n'},
            'id': name.lower().replace(' ', '-'),
            'name': name,
            'type': 'n8n-nodes-base.code',
            'typeVersion': 2,
            'position': [x, y],
        }

    validate_js = r"""
const incoming = $input.first().json;
const headers = incoming.headers || {};
const payload = incoming.body || incoming;
const expectedSecret = $env.COMPA_WEBHOOK_SECRET || 'whsec_compa_buildathon_2026';
const receivedSecret = headers['x-compa-webhook-secret'] || headers['X-Compa-Webhook-Secret'] || '';
const authorization = headers.authorization || headers.Authorization || '';
const bearerSecret = authorization.startsWith('Bearer ') ? authorization.slice(7) : '';
if (!payload._skip_auth && receivedSecret !== expectedSecret && bearerSecret !== expectedSecret) {
  throw new Error('Unauthorized: invalid webhook secret');
}
const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
if (!uuidRegex.test(payload.productor_id || '')) throw new Error('productor_id must be a Supabase UUID');
if (!payload.tipo_documento || typeof payload.tipo_documento !== 'string') throw new Error('tipo_documento is required');
function sqlString(value) {
  return `'${String(value ?? '').replace(/'/g, "''")}'`;
}
const query = `SELECT
  to_jsonb(p) AS productor,
  to_jsonb(pl) AS plantilla
FROM productores p
CROSS JOIN plantillas_documentos pl
WHERE p.id = ${sqlString(payload.productor_id)}::uuid
  AND pl.tipo = ${sqlString(payload.tipo_documento)}
LIMIT 1;`;
return [{ json: { ...payload, datos_adicionales: payload.datos_adicionales || {}, select_query: query } }];
"""
    validate_fields_js = r"""
const request = $items('Validate Request')[0].json;
const row = $input.first().json;
if (!row.productor || !row.plantilla) {
  return [{ json: { estado: 'error', error: 'productor_o_plantilla_no_encontrado', mensaje: 'No encontre el productor o la plantilla solicitada.', request } }];
}
const productor = row.productor;
const plantilla = row.plantilla;
const datosProductor = {
  nombre: productor.nombre || '',
  nombre_empresa: productor.nombre || '',
  nombre_representante: productor.nombre || '',
  dui: productor.dui || '',
  dui_representante: productor.dui || '',
  nit: productor.nit || '',
  direccion: productor.ubicacion || '',
  telefono: productor.telefono || '',
  rubro: productor.rubro || ''
};
const datosCompletos = { ...datosProductor, ...request.datos_adicionales };
const camposRequeridos = Array.isArray(plantilla.campos_requeridos) ? plantilla.campos_requeridos : JSON.parse(plantilla.campos_requeridos || '[]');
const camposFaltantes = camposRequeridos.filter((campo) => !datosCompletos[campo]);
if (camposFaltantes.length > 0) {
  return [{ json: { estado: 'incompleto', campos_faltantes: camposFaltantes, mensaje: `Necesito estos datos para completar el borrador: ${camposFaltantes.join(', ')}.`, productor_id: request.productor_id, plantilla_id: plantilla.id, tipo_documento: plantilla.tipo } }];
}
const archivoNombre = `${plantilla.tipo}_${Date.now()}.docx`;
const archivoUrl = `simulado://documentos-dinac/${archivoNombre}`;
return [{
  json: {
    estado: 'borrador',
    productor_id: request.productor_id,
    plantilla_id: plantilla.id,
    tipo_documento: plantilla.tipo,
    path_template: plantilla.path_template,
    datos_usados: datosCompletos,
    archivo_nombre: archivoNombre,
    archivo_url: archivoUrl,
    mensaje: 'Borrador preparado en modo demo. Debe revisarse, completarse con la plantilla oficial y firmarse por el productor.'
  }
}];
"""
    insert_js = r"""
const data = $input.first().json;
if (data.estado !== 'borrador') {
  return [{ json: { ...data, insert_query: 'SELECT NULL::text AS documento_id;' } }];
}
function sqlString(value) {
  return `'${String(value ?? '').replace(/'/g, "''")}'`;
}
const query = `INSERT INTO documentos_generados (productor_id, plantilla_id, datos_usados, archivo_url, estado)
VALUES (
  ${sqlString(data.productor_id)}::uuid,
  ${sqlString(data.plantilla_id)}::uuid,
  ${sqlString(JSON.stringify(data.datos_usados))}::jsonb,
  ${sqlString(data.archivo_url)},
  'borrador'
)
RETURNING id::text AS documento_id, archivo_url, estado;`;
return [{ json: { ...data, insert_query: query } }];
"""

    return {
        'name': 'COMPA - Fase 4 - generar_documento',
        'nodes': [
            {
                'parameters': {'httpMethod': 'POST', 'path': 'generar-documento-dinac', 'responseMode': 'responseNode', 'options': {'responseData': 'allEntries'}},
                'id': 'webhook-generar-documento',
                'name': 'Webhook generar-documento-dinac',
                'type': 'n8n-nodes-base.webhook',
                'typeVersion': 2,
                'position': [0, 0],
                'webhookId': 'compa-generar-documento-dinac',
            },
            code_node('Validate Request', validate_js, 260, 0),
            {
                'parameters': {'operation': 'executeQuery', 'query': '={{ $json.select_query }}', 'options': {}},
                'id': 'query-productor-plantilla',
                'name': 'Query Productor and Template',
                'type': 'n8n-nodes-base.postgres',
                'typeVersion': 2.4,
                'position': [520, 0],
                'credentials': {'postgres': {'id': 'REPLACE_SUPABASE_POSTGRES_CREDENTIAL_ID', 'name': 'Supabase Postgres'}},
            },
            code_node('Validate Fields and Simulate Draft', validate_fields_js, 780, 0),
            code_node('Build Audit Insert', insert_js, 1040, 0),
            {
                'parameters': {'operation': 'executeQuery', 'query': '={{ $json.insert_query }}', 'options': {}},
                'id': 'insert-documento-generado',
                'name': 'Insert Documento Generado',
                'type': 'n8n-nodes-base.postgres',
                'typeVersion': 2.4,
                'position': [1300, 0],
                'credentials': {'postgres': {'id': 'REPLACE_SUPABASE_POSTGRES_CREDENTIAL_ID', 'name': 'Supabase Postgres'}},
                'continueOnFail': True,
            },
            {
                'parameters': {
                    'respondWith': 'json',
                    'responseBody': "={{ $items('Validate Fields and Simulate Draft')[0].json }}",
                    'options': {'responseCode': 200},
                },
                'id': 'respond-documento',
                'name': 'Respond Documento',
                'type': 'n8n-nodes-base.respondToWebhook',
                'typeVersion': 1.1,
                'position': [1560, 0],
            },
        ],
        'connections': {
            'Webhook generar-documento-dinac': {'main': [[{'node': 'Validate Request', 'type': 'main', 'index': 0}]]},
            'Validate Request': {'main': [[{'node': 'Query Productor and Template', 'type': 'main', 'index': 0}]]},
            'Query Productor and Template': {'main': [[{'node': 'Validate Fields and Simulate Draft', 'type': 'main', 'index': 0}]]},
            'Validate Fields and Simulate Draft': {'main': [[{'node': 'Build Audit Insert', 'type': 'main', 'index': 0}]]},
            'Build Audit Insert': {'main': [[{'node': 'Insert Documento Generado', 'type': 'main', 'index': 0}]]},
            'Insert Documento Generado': {'main': [[{'node': 'Respond Documento', 'type': 'main', 'index': 0}]]},
        },
        'settings': {'executionOrder': 'v1', 'timezone': 'America/El_Salvador'},
        'staticData': None,
        'pinData': {},
        'versionId': 'compa-fase-4-generar-documento',
        'triggerCount': 1,
        'tags': [{'name': 'compa'}, {'name': 'fase-4'}, {'name': 'legal'}],
    }


def update_agent_config(kb_files: list[dict[str, Any]]) -> None:
    path = DOCS / 'elevenlabs-agent-config-v3-legal.md'
    text = path.read_text(encoding='utf-8-sig')
    selected_names = {
        'Ley-de-compras-publicas-III-15.julio_.2024_con-portada.pdf',
        'LEY-DE-CREACION-DE-LA-DIRECCION-NACIONAL-DE-COMPRAS-PUBLICAS-DL-653-ANIO-2023-LT.pdf',
        'nov23-Codigo-Etica-Socios-Negocios-DINAC.pdf',
        'Lineamiento-para-la-Participacion-en-los-Procesos-de-Compras-Publicas-de-las-MIPYMES.pdf',
        'Lineamiento-para-el-Metodo-de-Contratacion-de-Licitacion-Competitiva.pdf',
        'Lineamiento-para-el-Metodo-de-Contratacion-Directa.pdf',
        'LINEAMIENTO-PARA-EL-PROCEDIMIENTO-ESPECIAL-DE-SUBASTA-INVERSA.pdf',
        'Politica-Anual-de-Compras-2026-.pdf',
    }
    selected = [item for item in kb_files if item['archivo'] in selected_names]
    rows = ['| Documento | Archivo | Origen | Tamaño |', '|---|---|---|---|']
    for item in selected:
        rows.append(f"| {item['archivo']} | `{item['path']}` | {item['area']} | {item['bytes']} bytes |")
    kb_section = (
        '## 2. Knowledge Base (RAG)\n\n'
        'Subir al Knowledge Base del agente solo documentos del repositorio legal: leyes, reglamentos, lineamientos, políticas e información DINAC.\n\n'
        '**No subir `DocumentacionLegal/Documentación-usuario/` al RAG.** Esa carpeta contiene plantillas/formularios para documentos que la plataforma genera para usuarios; no es material de consulta legal.\n\n'
        + '\n'.join(rows) + '\n\n'
        '**Regla de separación**:\n'
        '- `Documentación-usuario`: plantillas generables por `generar_documento`.\n'
        '- `Leyes y reglamentos`, `Lineamientos`, `Políticas`, `Información DINAC.txt`: repositorio legal para RAG.\n\n'
        '**Configuración RAG**:\n'
        '- Use RAG: ON\n'
        '- Source attribution: ON\n'
        '- Include source citations in responses\n'
    )
    text = re.sub(r'## 2\. Knowledge Base \(RAG\).*?## 3\. Tools', kb_section + '\n## 3. Tools', text, flags=re.DOTALL)
    text = text.replace('Si el productor necesita un documento oficial (declaración jurada, formulario\nde garantía, carta compromiso, desglose de precios), usá la herramienta', 'Si el productor necesita generar o preparar un documento oficial usando una plantilla de Documentación-usuario (declaración jurada, documento estándar, carta compromiso, desglose de precios), usá la herramienta')
    text = text.replace('Reglas para preguntas legales:\n1. Respondé SOLO con base en los documentos de tu Knowledge Base.', 'Reglas para preguntas legales:\n1. Respondé SOLO con base en los documentos del repositorio legal cargados en tu Knowledge Base. No uses las plantillas de Documentación-usuario como fuente RAG.')
    path.write_text(text, encoding='utf-8')


def write_docs(template_files: list[dict[str, Any]], kb_files: list[dict[str, Any]]) -> None:
    total_templates = sum(item['bytes'] for item in template_files)
    total_kb = sum(item['bytes'] for item in kb_files)
    curated = [item for item in kb_files if item['archivo'] in {
        'Ley-de-compras-publicas-III-15.julio_.2024_con-portada.pdf',
        'LEY-DE-CREACION-DE-LA-DIRECCION-NACIONAL-DE-COMPRAS-PUBLICAS-DL-653-ANIO-2023-LT.pdf',
        'nov23-Codigo-Etica-Socios-Negocios-DINAC.pdf',
        'Lineamiento-para-la-Participacion-en-los-Procesos-de-Compras-Publicas-de-las-MIPYMES.pdf',
        'Lineamiento-para-el-Metodo-de-Contratacion-de-Licitacion-Competitiva.pdf',
        'Lineamiento-para-el-Metodo-de-Contratacion-Directa.pdf',
        'LINEAMIENTO-PARA-EL-PROCEDIMIENTO-ESPECIAL-DE-SUBASTA-INVERSA.pdf',
        'Politica-Anual-de-Compras-2026-.pdf',
    }]
    curated_size = sum(item['bytes'] for item in curated)
    doc = f'''# Fase 4 - Legal como módulo secundario

## Separación corregida

La confusión venía de mezclar dos usos distintos de la carpeta legal:

- `DocumentacionLegal/Documentación-usuario/`: plantillas y formularios para documentos que COMPA puede preparar para el usuario.
- `DocumentacionLegal/Leyes y reglamentos/`, `DocumentacionLegal/Lineamientos/`, `DocumentacionLegal/Políticas/` e `Información DINAC.txt`: repositorio de información legal para Knowledge Base/RAG.

## Entregables

- `data/legal-template-manifest.json`: inventario de plantillas generables.
- `data/legal-kb-repository-manifest.json`: inventario del repositorio legal.
- `data/legal-kb-curated-elevenlabs.json`: subconjunto recomendado para subir al Knowledge Base.
- `n8n-exports/workflow-generar-documento-dinac.json`: workflow importable para generar un borrador simulado y auditarlo en Supabase.
- `demo/payload-generar-documento-vilma.mock.json`: payload de prueba.
- `scripts/test_phase4_contract.py`: validación estática del contrato.

## Tamaños locales

- Plantillas de usuario: {len(template_files)} archivos, {total_templates} bytes.
- Repositorio legal completo: {len(kb_files)} archivos, {total_kb} bytes.
- Subconjunto RAG recomendado: {len(curated)} archivos, {curated_size} bytes.

## Regla de demo

El módulo legal no es la ruta principal de demo. Si se muestra, debe declararse como módulo secundario en modo borrador:

1. Pregunta legal: responder con RAG del repositorio legal, citando fuente.
2. Documento: usar `generar_documento` sobre plantillas de `Documentación-usuario`.
3. Resultado: siempre `estado = borrador`; nunca decir firmado, presentado o aprobado.

## Variables requeridas

- `COMPA_WEBHOOK_SECRET` opcional, default `whsec_compa_buildathon_2026`.
- Credential n8n `Supabase Postgres` para los nodos Postgres.

## Prueba local

```powershell
C:\\Users\\isabe\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe Compa\\scripts\\test_phase4_contract.py
```

Salida esperada:

```text
phase4 contract ok
```
'''
    (DOCS / 'FASE-4-LEGAL.md').write_text(doc, encoding='utf-8')


def write_tests() -> None:
    payload = {
        'tipo_documento': 'declaracion_jurada_persona_natural',
        'productor_id': '11111111-1111-4111-8111-111111111111',
        'datos_adicionales': {'fecha': '2026-07-04'},
        '_skip_auth': True,
    }
    write_json(DEMO / 'payload-generar-documento-vilma.mock.json', payload)
    test = r'''from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
UUID_RE = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.I)


def load_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    templates = load_json(ROOT / 'data' / 'legal-template-manifest.json')
    kb = load_json(ROOT / 'data' / 'legal-kb-repository-manifest.json')
    curated = load_json(ROOT / 'data' / 'legal-kb-curated-elevenlabs.json')
    workflow = load_json(ROOT / 'n8n-exports' / 'workflow-generar-documento-dinac.json')
    payload = load_json(ROOT / 'demo' / 'payload-generar-documento-vilma.mock.json')

    assert_true(len(templates['templates']) > 0, 'missing user templates')
    assert_true(len(kb['repository']) > 0, 'missing legal repository')
    assert_true(all(not item['subir_a_rag'] for item in templates['templates']), 'templates must not be marked for RAG')
    assert_true(all('Documentación-usuario' not in item['path'] for item in kb['repository']), 'KB repository includes user templates')
    assert_true(len(curated['elevenlabs_kb_recommended']) > 0, 'missing curated KB list')
    text = json.dumps(workflow, ensure_ascii=False)
    assert_true('generar-documento-dinac' in text, 'missing document webhook path')
    assert_true('estado' in text and 'borrador' in text, 'workflow must return borrador state')
    assert_true('INSERT INTO documentos_generados' in text, 'workflow must audit generated document')
    assert_true(UUID_RE.match(payload['productor_id']) is not None, 'mock productor_id is not UUID')
    assert_true(payload['tipo_documento'] == 'declaracion_jurada_persona_natural', 'unexpected mock document type')
    print('phase4 contract ok')


if __name__ == '__main__':
    main()
'''
    (SCRIPTS / 'test_phase4_contract.py').write_text(test, encoding='utf-8')


def main() -> None:
    template_files, kb_files = build_manifests()
    curated_names = {
        'Ley-de-compras-publicas-III-15.julio_.2024_con-portada.pdf',
        'LEY-DE-CREACION-DE-LA-DIRECCION-NACIONAL-DE-COMPRAS-PUBLICAS-DL-653-ANIO-2023-LT.pdf',
        'nov23-Codigo-Etica-Socios-Negocios-DINAC.pdf',
        'Lineamiento-para-la-Participacion-en-los-Procesos-de-Compras-Publicas-de-las-MIPYMES.pdf',
        'Lineamiento-para-el-Metodo-de-Contratacion-de-Licitacion-Competitiva.pdf',
        'Lineamiento-para-el-Metodo-de-Contratacion-Directa.pdf',
        'LINEAMIENTO-PARA-EL-PROCEDIMIENTO-ESPECIAL-DE-SUBASTA-INVERSA.pdf',
        'Politica-Anual-de-Compras-2026-.pdf',
    }
    curated = [item for item in kb_files if item['archivo'] in curated_names]
    write_json(DATA / 'legal-template-manifest.json', {'source': 'DocumentacionLegal/Documentación-usuario', 'templates': template_files})
    write_json(DATA / 'legal-kb-repository-manifest.json', {'source': 'DocumentacionLegal except Documentación-usuario', 'repository': kb_files})
    write_json(DATA / 'legal-kb-curated-elevenlabs.json', {'source': 'legal-kb-repository-manifest.json', 'elevenlabs_kb_recommended': curated})
    update_schema(template_files)
    write_json(N8N / 'workflow-generar-documento-dinac.json', build_legal_workflow())
    update_agent_config(kb_files)
    write_docs(template_files, kb_files)
    write_tests()
    print(f'phase4 files written: {len(template_files)} templates, {len(kb_files)} repository docs, {len(curated)} curated')


if __name__ == '__main__':
    main()