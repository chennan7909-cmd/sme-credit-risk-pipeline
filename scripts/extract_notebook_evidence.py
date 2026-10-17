"""Extract saved text tables; this does NOT re-execute the historical notebook."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / 'Individual_Project_Chen.ipynb'
notebook = json.loads(path.read_text())
text = ''.join(''.join(o.get('text', [])) for o in notebook['cells'][11].get('outputs', []))
sections = {
    'states': ('Province Risk Ranking (Top 15):', 'Window Function 2:'),
    'cohorts': ('Year-over-Year Default Rate Change by Loan Grade:', 'Window Function 3:'),
    'purposes': ('Default Rate by Loan Purpose:', 'Feature data saved'),
}
output = ROOT / 'analytics/reports/historical'
output.mkdir(parents=True, exist_ok=True)
for name, (start, stop) in sections.items():
    block = text.split(start, 1)[1].split(stop, 1)[0]
    rows = [[item.strip() for item in line.strip().strip('|').split('|')]
            for line in block.splitlines() if line.startswith('|')]
    rows[0] = ['state' if h == 'province' else h for h in rows[0]]
    with (output / f'{name}.csv').open('w', newline='') as handle:
        csv.writer(handle).writerows(rows)
manifest = {
    'source': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
    'cell_index_zero_based': 11, 'evidence_type': 'saved notebook text outputs; not rerun',
    'coverage': {'states': 'top 15 only', 'cohorts': 'first 30 only', 'purposes': 'all 14 displayed'},
    'semantics': 'state replaces misleading original province label; rates unchanged',
}
(output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Extracted saved historical tables to', output.relative_to(ROOT))
