from pathlib import Path

paths = [
    Path('Compa/n8n-exports/workflow-retar-decision.json'),
    Path('Compa/n8n-exports/workflow-oportunidades-elevenlabs.json'),
    Path('Compa/n8n-exports/elevenlabs-tool-retar-decision.json'),
    Path('Compa/scripts/generate_phase3_assets.py'),
]
for path in paths:
    text = path.read_text(encoding='utf-8-sig')
    text = text.replace("={{ 'Bearer ' + .OPENAI_API_KEY }}", "={{ 'Bearer ' + $env.OPENAI_API_KEY }}")
    text = text.replace("=Bearer {{ $env.OPENAI_API_KEY }}", "={{ 'Bearer ' + $env.OPENAI_API_KEY }}")
    path.write_text(text, encoding='utf-8')
    print(f'fixed {path}')