from pathlib import Path
root = Path('Compa/DocumentacionLegal')
for p in sorted(root.rglob('*')):
    if p.is_file():
        print(f'{p.relative_to(root)}\t{p.stat().st_size}')