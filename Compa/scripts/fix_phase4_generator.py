from pathlib import Path
path = Path('Compa/scripts/generate_phase4_assets.py')
text = path.read_text(encoding='utf-8')
text = text.replace('    }}]\n    curated_size', '    }]\n    curated_size')
path.write_text(text, encoding='utf-8')
print('fixed phase4 generator')