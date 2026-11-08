"""Write docs/CHIFFRES.md from the published catalogue."""
from collections import Counter
import json
from pathlib import Path

root = Path(__file__).resolve().parents[1]
data = json.loads((root / 'site/catalog/catalog.json').read_text(encoding='utf-8'))
manifest = json.loads((root / 'site/export-manifest.json').read_text(encoding='utf-8'))
items, guides = data['items'], data['guides']
SUBJECTS = {'mechanics': 'Mécanique', 'simracing': 'Sim racing', 'engineering': 'Ingénierie', 'driving': 'Pilotage', 'career': 'Métiers',
            'media': 'Photo & vidéo', 'business': 'Business', 'fitness': 'Préparation', 'other': 'Autres'}
number = lambda value: f'{value:,}'.replace(',', ' ')

def table(title, heads, rows):
    lines = [f'## {title}', '', '| ' + ' | '.join(heads) + ' |', '|' + '---|' * len(heads)]
    lines += ['| ' + ' | '.join(row) + ' |' for row in rows]
    return lines + ['']

french = [item for item in items if item.get('language') == 'fr']
subjects, french_subjects = Counter(i['category'] for i in items), Counter(i['category'] for i in french)
models = Counter()
for item in items:
    named = {(v.get('make', ''), v.get('model', '')) for v in (item.get('automotive') or {}).get('vehicles', []) if v.get('model')}
    models.update(named)
with_vehicle = sum(1 for i in items if any(v.get('model') for v in (i.get('automotive') or {}).get('vehicles', [])))

out = ['# Chiffres du catalogue', '', f"Généré par `scripts/report_stats.py` depuis le catalogue exporté le {manifest['generated_at'][:10]}.", '']
out += table('Vue d’ensemble', ['Indicateur', 'Valeur'], [
    ['Vidéos référencées', number(len(items))], ['En français', number(len(french))], ['Guides RaceLink', number(len(guides))],
    ['Langues repérées', str(len({i.get('language') for i in items if i.get('language') not in (None, 'und')}))],
    ['Transcriptions', number(sum(bool(i.get('has_transcript')) for i in items))], ['Vidéos reliées à un modèle de voiture', number(with_vehicle)],
    ['Catalogue JSON', f"{manifest['catalog_bytes'] // 1048576} Mo"], ['Catalogue compressé', f"{manifest['catalog_gzip_bytes'] / 1048576:.1f} Mo"]])
out += table('Par plateforme', ['Plateforme', 'Vidéos'], [[k, number(v)] for k, v in Counter(i['platform'] for i in items).most_common()])
out += table('Par langue', ['Langue', 'Vidéos'], [[str(k), number(v)] for k, v in Counter(i.get('language') for i in items).most_common()])
out += table('Par sujet', ['Sujet', 'Vidéos', 'En français'], [[SUBJECTS.get(k, k), number(v), number(french_subjects[k])] for k, v in subjects.most_common()])
out += table('Modèles les mieux couverts', ['Voiture', 'Vidéos'], [[f'{make} {model}'.strip(), number(v)] for (make, model), v in models.most_common(20)])
out += ['La langue et la voiture proviennent des métadonnées publiques : elles peuvent être estimées.', '']
target = root / 'docs/CHIFFRES.md'
target.parent.mkdir(exist_ok=True)
target.write_text('\n'.join(out), encoding='utf-8')
print(f'{target.name}: {number(len(items))} videos')
