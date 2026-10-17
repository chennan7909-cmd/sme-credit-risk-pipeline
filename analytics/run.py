"""CSV -> validated SQLite -> SQL reports. Python standard library only."""
import argparse
import csv
import hashlib
import json
import math
import sqlite3
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REQUIRED = {'id', 'loan_amnt', 'loan_status', 'issue_d', 'term', 'grade', 'purpose', 'addr_state', 'int_rate', 'fico_range_low'}
RESOLVED = {'Fully Paid', 'Charged Off', 'Default'}
DEFAULTED = {'Charged Off', 'Default'}


def number(value):
    if value is None or not value.strip():
        return None
    result = float(value.strip().removesuffix('%'))
    if not math.isfinite(result):
        raise ValueError('non-finite numeric value')
    return result


def build(csv_path, output, source):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(':memory:')
    db.execute('''CREATE TABLE loans (
        id TEXT PRIMARY KEY, loan_amnt REAL NOT NULL, loan_status TEXT NOT NULL,
        issue_month TEXT NOT NULL, term_months INTEGER NOT NULL, grade TEXT NOT NULL,
        purpose TEXT NOT NULL, addr_state TEXT NOT NULL, int_rate REAL,
        fico_range_low REAL, is_resolved INTEGER NOT NULL, is_default INTEGER NOT NULL)''')
    quality = {'source_rows': 0, 'loaded_rows': 0, 'rejected_rows': 0, 'duplicate_ids': 0,
               'missing_interest_rate': 0, 'missing_fico': 0, 'unknown_dimensions': 0}
    with open(csv_path, newline='', encoding='utf-8-sig') as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED.issubset(reader.fieldnames or []):
            raise ValueError(f'Missing columns: {sorted(REQUIRED - set(reader.fieldnames or []))}')
        for row in reader:
            quality['source_rows'] += 1
            try:
                identity = row['id'].strip()
                amount = number(row['loan_amnt'])
                status = row['loan_status'].strip()
                month = datetime.strptime(row['issue_d'].strip(), '%b-%Y').strftime('%Y-%m')
                term = int(row['term'].strip().split()[0])
                rate, fico = number(row['int_rate']), number(row['fico_range_low'])
                if not identity or amount is None or amount <= 0 or not status or term not in (36, 60):
                    raise ValueError('invalid required value')
                if (rate is not None and not 0 <= rate <= 100) or (fico is not None and not 300 <= fico <= 850):
                    raise ValueError('numeric value outside contract')
                dimensions = [row[k].strip() or 'Unknown' for k in ('grade', 'purpose', 'addr_state')]
                db.execute('INSERT INTO loans VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',
                           (identity, amount, status, month, term, *dimensions, rate, fico,
                            int(status in RESOLVED), int(status in DEFAULTED)))
                quality['loaded_rows'] += 1
                quality['missing_interest_rate'] += rate is None
                quality['missing_fico'] += fico is None
                quality['unknown_dimensions'] += 'Unknown' in dimensions
            except sqlite3.IntegrityError:
                quality['duplicate_ids'] += 1
                quality['rejected_rows'] += 1
            except (ValueError, TypeError, AttributeError, IndexError):
                quality['rejected_rows'] += 1
    if not quality['loaded_rows']:
        raise ValueError('No valid loans loaded')
    for query in sorted((ROOT / 'sql').glob('*.sql')):
        cursor = db.execute(query.read_text())
        with (output / f'{query.stem}.csv').open('w', newline='') as handle:
            writer = csv.writer(handle)
            writer.writerow([col[0] for col in cursor.description])
            writer.writerows(cursor)
    with (output / 'status_coverage.csv').open('w', newline='') as handle:
        writer = csv.writer(handle)
        writer.writerow(['loan_status', 'loans'])
        writer.writerows(db.execute('SELECT loan_status, COUNT(*) FROM loans GROUP BY loan_status ORDER BY loan_status'))
    digest = hashlib.sha256()
    with open(csv_path, 'rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    manifest = {'source': source, 'input_sha256': digest.hexdigest(),
                'quality': quality, 'sqlite_version': sqlite3.sqlite_version,
                'outcome_definition': 'Charged Off or Default / Fully Paid, Charged Off or Default',
                'warning': 'Resolved-only descriptive rates; no fixed observation horizon or causal claims.'}
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    db.close()
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--source', choices=['synthetic-demo', 'lending-club'], required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.csv, args.out, args.source), indent=2))
