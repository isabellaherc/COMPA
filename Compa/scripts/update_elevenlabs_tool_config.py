from pathlib import Path
import json

path = Path('Compa/docs/elevenlabs-agent-config-v3-legal.md')
tool = json.loads(Path('Compa/n8n-exports/elevenlabs-tool-retar-decision.json').read_text(encoding='utf-8'))
text = path.read_text(encoding='utf-8-sig')
start = text.index('### Tool 1: retar_decision')
json_start = text.index('```json', start)
json_end = text.index('```', json_start + len('```json'))
replacement = '```json\n' + json.dumps(tool, ensure_ascii=False, indent=2) + '\n```'
text = text[:json_start] + replacement + text[json_end + 3:]
path.write_text(text, encoding='utf-8')
print('updated elevenlabs retar_decision config')