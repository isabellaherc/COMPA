from pathlib import Path
import json
import re

workflow_path = Path('Compa/n8n-exports/workflow-generar-documento-dinac.json')
workflow = json.loads(workflow_path.read_text(encoding='utf-8'))
for node in workflow['nodes']:
    if node['name'] == 'Build Audit Insert':
        js = node['parameters']['jsCode']
        js = js.replace("return [{ json: { ...data, insert_query: null } }];", "return [{ json: { ...data, insert_query: 'SELECT NULL::text AS documento_id;' } }];")
        node['parameters']['jsCode'] = js
workflow_path.write_text(json.dumps(workflow, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

generator_path = Path('Compa/scripts/generate_phase4_assets.py')
text = generator_path.read_text(encoding='utf-8')
text = text.replace("return [{ json: { ...data, insert_query: null } }];", "return [{ json: { ...data, insert_query: 'SELECT NULL::text AS documento_id;' } }];")
generator_path.write_text(text, encoding='utf-8')

tool = {
    'type': 'webhook',
    'name': 'generar_documento',
    'description': 'Prepara un BORRADOR de documento oficial usando plantillas de Documentación-usuario. No firma, no presenta y no sustituye revisión humana.',
    'parameters': {
        'type': 'object',
        'properties': {
            'tipo_documento': {
                'type': 'string',
                'description': 'Tipo de plantilla generable.',
                'enum': [
                    'declaracion_jurada_persona_natural',
                    'declaracion_jurada_apoderado_persona_natural',
                    'declaracion_jurada_persona_juridica',
                    'declaracion_jurada_apoderado_persona_juridica',
                    'documento_estandar_contratacion_directa',
                    'documento_estandar_comparacion_precios_bienes_servicios',
                    'carta_compromiso',
                    'desglose_precios',
                ],
            },
            'productor_id': {'type': 'string', 'description': 'UUID real del productor en Supabase.'},
            'datos_adicionales': {'type': 'object', 'description': 'Datos faltantes conversados con el usuario, por ejemplo fecha, monto, items o precios_unitarios.'},
        },
        'required': ['tipo_documento', 'productor_id'],
    },
    'api': {
        'url': 'https://{WORKSPACE}.app.n8n.cloud/webhook/generar-documento-dinac',
        'method': 'POST',
        'headers': {'Content-Type': 'application/json', 'X-Compa-Webhook-Secret': 'whsec_compa_buildathon_2026'},
    },
}
Path('Compa/n8n-exports/elevenlabs-tool-generar-documento.json').write_text(json.dumps(tool, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

agent_path = Path('Compa/docs/elevenlabs-agent-config-v3-legal.md')
agent = agent_path.read_text(encoding='utf-8-sig')
start = agent.index('### Tool 2: generar_documento')
json_start = agent.index('```json', start)
json_end = agent.index('```', json_start + len('```json'))
replacement = '```json\n' + json.dumps(tool, ensure_ascii=False, indent=2) + '\n```'
agent = agent[:json_start] + replacement + agent[json_end + 3:]
agent_path.write_text(agent, encoding='utf-8')

# Strengthen phase 4 docs with the tool artifact.
doc_path = Path('Compa/docs/FASE-4-LEGAL.md')
doc = doc_path.read_text(encoding='utf-8')
if 'elevenlabs-tool-generar-documento.json' not in doc:
    doc = doc.replace('- `n8n-exports/workflow-generar-documento-dinac.json`: workflow importable para generar un borrador simulado y auditarlo en Supabase.\n', '- `n8n-exports/workflow-generar-documento-dinac.json`: workflow importable para generar un borrador simulado y auditarlo en Supabase.\n- `n8n-exports/elevenlabs-tool-generar-documento.json`: definición del tool para copiar al dashboard de ElevenLabs.\n')
doc_path.write_text(doc, encoding='utf-8')

# Extend test expectations.
test_path = Path('Compa/scripts/test_phase4_contract.py')
test = test_path.read_text(encoding='utf-8')
if "elevenlabs-tool-generar-documento.json" not in test:
    test = test.replace("payload = load_json(ROOT / 'demo' / 'payload-generar-documento-vilma.mock.json')", "payload = load_json(ROOT / 'demo' / 'payload-generar-documento-vilma.mock.json')\n    tool = load_json(ROOT / 'n8n-exports' / 'elevenlabs-tool-generar-documento.json')")
    test = test.replace("assert_true('INSERT INTO documentos_generados' in text, 'workflow must audit generated document')", "assert_true('INSERT INTO documentos_generados' in text, 'workflow must audit generated document')\n    assert_true('SELECT NULL::text AS documento_id' in text, 'workflow must safely respond when draft is incomplete')\n    assert_true({'tipo_documento', 'productor_id'}.issubset(set(tool['parameters']['required'])), 'document tool missing required params')")
test_path.write_text(test, encoding='utf-8')

print('phase4 workflow/tool adjusted')