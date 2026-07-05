from pathlib import Path

paths = [
    Path('Compa/supabase-schema.sql'),
    Path('Compa/n8n-exports/n8n-workflow-especificaciones.md'),
    Path('Compa/docs/FASE-1-DEMO-ESTABLE.md'),
    Path('Compa/demo/guion-demo-fase-1.md'),
]

for path in paths:
    raw = path.read_bytes()
    try:
        text = raw.decode('utf-8')
    except UnicodeDecodeError:
        text = raw.decode('utf-8', errors='replace')
    if '\ufffd' in text:
        text = raw.decode('cp1252')
    path.write_text(text, encoding='utf-8')
    print(f'normalized {path}')