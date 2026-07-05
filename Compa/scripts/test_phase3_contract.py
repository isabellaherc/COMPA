from __future__ import annotations

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
