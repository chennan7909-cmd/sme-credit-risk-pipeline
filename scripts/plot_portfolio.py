"""Optional chart regeneration: requires matplotlib; reads saved aggregates only."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1] / 'analytics/reports/historical'
with (root / 'purposes.csv').open() as handle:
    rows = list(csv.DictReader(handle))
fig, axes = plt.subplots(1, 2, figsize=(12, 5), layout='constrained')
fig.patch.set_facecolor('#f8fafc')
for ax, key, title, label in zip(
    axes, ['default_rate_pct', 'total_loans'],
    ['Highest rates: review frequency', 'Largest segments: review scale'],
    ['Resolved default rate (%)', 'Resolved loans (thousands)']
):
    selected = sorted(rows, key=lambda r: float(r[key]), reverse=True)[:6][::-1]
    values = [float(r[key]) / (1000 if key == 'total_loans' else 1) for r in selected]
    bars = ax.barh([r['loan_purpose'].replace('_', ' ') for r in selected], values,
                   color=['#ea7b42' if r['loan_purpose'] == 'small_business' else '#237a8c' for r in selected])
    ax.bar_label(bars, fmt='%.1f', padding=4, fontsize=9)
    ax.set_xlim(0, max(values) * 1.2)
    ax.set_title(title, loc='left', fontweight='bold', pad=16)
    ax.set_xlabel(label)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.tick_params(axis='y', length=0)
fig.suptitle('Loan-purpose review: balance rate with volume', fontsize=17, fontweight='bold')
fig.text(.01, -.055,
         'Source: saved Lending Club notebook output, cell 11. Resolved loans only; not a new raw-data run.\n'
         'Descriptive comparison; differences may reflect grade, term, vintage and outcome selection.',
         fontsize=9, color='#475569')
fig.savefig(root / 'portfolio_review.png', dpi=150, bbox_inches='tight')
