"""Generate the purpose rate/volume chart from historical or full aggregates."""
import argparse
import csv
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def historical_rows(path):
    with path.open() as handle:
        return [{
            'purpose': row['loan_purpose'],
            'resolved_loans': float(row['total_loans']),
            'default_rate_pct': float(row['default_rate_pct']),
        } for row in csv.DictReader(handle)]


def full_rows(path):
    with path.open() as handle:
        return [{
            'purpose': row['segment'],
            'resolved_loans': float(row['resolved_loans']),
            'default_rate_pct': 100 * float(row['resolved_default_rate']),
        } for row in csv.DictReader(handle) if row['dimension'] == 'purpose']


def plot(rows, output, source_note):
    if output.suffix.lower() != '.svg':
        raise ValueError('Output must use the .svg extension')
    specs = [
        ('default_rate_pct', 'Highest rates: review frequency', 'Resolved default rate (%)', 1),
        ('resolved_loans', 'Largest segments: review scale', 'Resolved loans (thousands)', 1000),
    ]
    svg = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="560" viewBox="0 0 1200 560">',
        '<rect width="1200" height="560" fill="#f8fafc"/>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;fill:#0f172a}'
        '.title{font-size:26px;font-weight:700}.panel{font-size:18px;font-weight:700}'
        '.label{font-size:13px}.axis{font-size:12px;fill:#475569}.value{font-size:12px;font-weight:600}</style>',
        '<text x="40" y="45" class="title">Loan-purpose review: balance rate with volume</text>',
    ]
    for panel, (key, title, label, divisor) in enumerate(specs):
        selected = sorted(rows, key=lambda row: row[key], reverse=True)[:6][::-1]
        values = [row[key] / divisor for row in selected]
        left = 40 + panel * 590
        label_width, chart_width = 150, 370
        svg.append(f'<text x="{left}" y="88" class="panel">{escape(title)}</text>')
        maximum = max(values)
        for index, (row, value) in enumerate(zip(selected, values)):
            y = 118 + index * 52
            width = chart_width * value / maximum
            color = '#ea7b42' if row['purpose'] == 'small_business' else '#237a8c'
            purpose = escape(row['purpose'].replace('_', ' '))
            svg.extend([
                f'<text x="{left}" y="{y + 18}" class="label">{purpose}</text>',
                f'<rect x="{left + label_width}" y="{y}" width="{width:.1f}" height="25" rx="3" fill="{color}"/>',
                f'<text x="{left + label_width + width + 7:.1f}" y="{y + 18}" class="value">{value:.1f}</text>',
            ])
        svg.append(f'<text x="{left + label_width}" y="448" class="axis">{escape(label)}</text>')
    svg.extend([
        f'<text x="40" y="505" class="axis">{escape(source_note)}</text>',
        '<text x="40" y="528" class="axis">Resolved loans only; descriptive comparison, not a causal or fixed-horizon estimate.</text>',
        '</svg>',
    ])
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(svg) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--segments', type=Path,
                        help='Full-run 02_segments.csv; omit to use historical purposes.csv')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    if args.segments:
        rows = full_rows(args.segments)
        output = args.output or ROOT / 'analytics/reports/full/portfolio_review.svg'
        source_note = 'Source: full Lending Club accepted-loan CSV run; aggregate outputs only.'
    else:
        source = ROOT / 'analytics/reports/historical/purposes.csv'
        rows = historical_rows(source)
        output = args.output or ROOT / 'analytics/reports/historical/portfolio_review.svg'
        source_note = 'Source: saved Lending Club notebook output, cell 11; not a new raw-data run.'
    plot(rows, output, source_note)
