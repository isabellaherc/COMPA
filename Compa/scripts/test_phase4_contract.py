from __future__ import annotations

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
    tool = load_json(ROOT / 'n8n-exports' / 'elevenlabs-tool-generar-documento.json')

    assert_true(len(templates['templates']) > 0, 'missing user templates')
    assert_true(len(kb['repository']) > 0, 'missing legal repository')
    assert_true(all(not item['subir_a_rag'] for item in templates['templates']), 'templates must not be marked for RAG')
    assert_true(all('Documentación-usuario' not in item['path'] for item in kb['repository']), 'KB repository includes user templates')
    assert_true(len(curated['elevenlabs_kb_recommended']) > 0, 'missing curated KB list')
    text = json.dumps(workflow, ensure_ascii=False)
    assert_true('generar-documento-dinac' in text, 'missing document webhook path')
    assert_true('estado' in text and 'borrador' in text, 'workflow must return borrador state')
    assert_true('INSERT INTO documentos_generados' in text, 'workflow must audit generated document')
    assert_true('SELECT NULL::text AS documento_id' in text, 'workflow must safely respond when draft is incomplete')
    assert_true({'tipo_documento', 'productor_id'}.issubset(set(tool['parameters']['required'])), 'document tool missing required params')
    assert_true(UUID_RE.match(payload['productor_id']) is not None, 'mock productor_id is not UUID')
    assert_true(payload['tipo_documento'] == 'declaracion_jurada_persona_natural', 'unexpected mock document type')
    print('phase4 contract ok')


if __name__ == '__main__':
    main()
