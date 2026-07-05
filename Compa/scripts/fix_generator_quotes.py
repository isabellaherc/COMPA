from pathlib import Path
path = Path('Compa/scripts/generate_phase3_assets.py')
text = path.read_text(encoding='utf-8')
text = text.replace("{'name': 'Authorization', 'value': '={{ 'Bearer ' + $env.OPENAI_API_KEY }}'},", '{\'name\': \'Authorization\', \'value\': "={{ \'Bearer \' + $env.OPENAI_API_KEY }}"},')
path.write_text(text, encoding='utf-8')
print('fixed generator quotes')