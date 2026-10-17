"""Reconcile dbt marts to aggregate evidence from analytics/run.py."""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path

import duckdb


ROOT = Path(__file__).resolve().parents[1]


def csv_rows(path):
    with path.open(newline='') as handle:
        return list(csv.DictReader(handle))


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def close(left, right, tolerance=1e-10):
    if left is None or right in (None, ''):
        return left is None and right in (None, '')
    return abs(float(left) - float(right)) <= tolerance


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database', type=Path,
                        default=ROOT / 'dbt/target/sme_credit_risk.duckdb')
    parser.add_argument('--evidence', type=Path,
                        default=ROOT / 'analytics/reports/full')
    args = parser.parse_args()

    raw_path = os.environ.get('LENDING_CLUB_CSV')
    if not raw_path:
        raise SystemExit('LENDING_CLUB_CSV is required to verify source identity')
    manifest = json.loads((args.evidence / 'manifest.json').read_text())
    actual_digest = sha256(Path(raw_path))
    if actual_digest != manifest['input_sha256']:
        raise SystemExit('Raw CSV digest differs from the legacy full-run evidence')

    db = duckdb.connect(str(args.database), read_only=True)
    portfolio_columns = [item[0] for item in db.execute(
        'DESCRIBE analytics_marts.mart_portfolio').fetchall()]
    actual_portfolio = dict(zip(portfolio_columns, db.execute(
        'SELECT * FROM analytics_marts.mart_portfolio').fetchone()))
    legacy_portfolio = csv_rows(args.evidence / '01_portfolio.csv')[0]
    for field in ('accepted_loans', 'resolved_loans', 'defaulted_loans'):
        assert int(actual_portfolio[field]) == int(legacy_portfolio[field]), field
    for field in ('original_principal_usd', 'resolved_share', 'resolved_default_rate'):
        assert close(actual_portfolio[field], legacy_portfolio[field], 1e-12), field

    quality_columns = [item[0] for item in db.execute(
        'DESCRIBE analytics_marts.mart_data_quality').fetchall()]
    quality = dict(zip(quality_columns, db.execute(
        'SELECT * FROM analytics_marts.mart_data_quality').fetchone()))
    expected = manifest['quality']
    assert quality['source_records'] == expected['source_rows']
    assert quality['accepted_loans'] == expected['loaded_rows']
    assert quality['non_loan_summary_records'] == expected['rejected_rows']
    assert quality['invalid_loan_records'] == 0
    assert quality['duplicate_loan_records'] == expected['duplicate_ids']

    segment_rows = db.execute('''
        SELECT dimension, segment, accepted_loans, resolved_loans, defaulted_loans
        FROM analytics_marts.mart_segments
    ''').fetchall()
    actual_segments = {(row[0], row[1]): row[2:] for row in segment_rows}
    for row in csv_rows(args.evidence / '02_segments.csv'):
        key = (row['dimension'], row['segment'])
        assert key in actual_segments, key
        assert actual_segments[key] == (
            int(row['accepted_loans']), int(row['resolved_loans']), int(row['defaulted_loans']))

    print('Source SHA-256:', actual_digest)
    print('Source records:', quality['source_records'])
    print('Valid loans:', quality['accepted_loans'])
    print('Non-loan summary records:', quality['non_loan_summary_records'])
    print('Resolved loans:', actual_portfolio['resolved_loans'])
    print('Defaulted loans:', actual_portfolio['defaulted_loans'])
    for key in [('purpose', 'debt_consolidation'), ('purpose', 'small_business'), ('state', 'CA')]:
        accepted, resolved, defaulted = actual_segments[key]
        print(f'{key[0]}={key[1]}: accepted={accepted}, resolved={resolved}, defaulted={defaulted}')
    print('Reconciliation: PASS')
    db.close()


if __name__ == '__main__':
    main()
