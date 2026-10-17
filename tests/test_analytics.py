import csv
import tempfile
import unittest
from pathlib import Path
from analytics.run import ROOT, build


class AnalyticsTests(unittest.TestCase):
    def run_data(self, text=None):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        data = root / 'input.csv'
        data.write_text(text if text is not None else (ROOT / 'data/demo_loans.csv').read_text())
        manifest = build(data, root / 'out', 'synthetic-demo')
        def rows(name):
            with (root / 'out' / name).open() as f:
                return list(csv.DictReader(f))
        return manifest, rows

    def test_unresolved_not_in_default_denominator(self):
        manifest, rows = self.run_data()
        total = rows('01_portfolio.csv')[0]
        self.assertEqual(int(total['accepted_loans']), 10)
        self.assertEqual(int(total['resolved_loans']), 7)
        self.assertAlmostEqual(float(total['resolved_default_rate']), 3 / 7)
        self.assertEqual(manifest['quality']['missing_fico'], 1)

    def test_segments_reconcile_and_shares_sum_to_one(self):
        _, rows = self.run_data()
        for dimension in ['purpose', 'state', 'grade']:
            segment = [r for r in rows('02_segments.csv') if r['dimension'] == dimension]
            self.assertEqual(sum(int(r['accepted_loans']) for r in segment), 10)
            self.assertEqual(sum(int(r['defaulted_loans']) for r in segment), 3)
            self.assertAlmostEqual(sum(float(r['default_count_share']) for r in segment), 1)

    def test_cohort_change_uses_percentage_points_and_calendar_gap(self):
        _, rows = self.run_data()
        cohorts = {(r['grade'], r['issue_year']): r for r in rows('03_cohorts.csv')}
        self.assertAlmostEqual(float(cohorts['A', '2018']['resolved_default_rate']), 0)
        self.assertEqual(cohorts['A', '2018']['yoy_change_pp'], '')
        self.assertAlmostEqual(float(cohorts['B', '2016']['yoy_change_pp']), 0)

    def test_pricing_outlier_is_actual_high_fico_high_rate_loan(self):
        _, rows = self.run_data()
        self.assertEqual([r['id'] for r in rows('04_pricing_review.csv')], ['DEMO-005'])

    def test_duplicates_invalid_rows_and_coverage(self):
        original = (ROOT / 'data/demo_loans.csv').read_text()
        extra = '\n'.join([original.splitlines()[1],
            'BAD,NaN,Fully Paid,Jan-2015,36 months,A,car,CA,10,700',
            'BAD2,1000,Fully Paid,wrong,36 months,A,car,CA,10,700'])
        manifest, _ = self.run_data(original + extra + '\n')
        self.assertEqual(manifest['quality']['source_rows'], 13)
        self.assertEqual(manifest['quality']['rejected_rows'], 3)
        self.assertEqual(manifest['quality']['duplicate_ids'], 1)

    def test_no_resolved_loans_yields_null_rate(self):
        original = (ROOT / 'data/demo_loans.csv').read_text().splitlines()
        _, rows = self.run_data(original[0] + '\n' + original[3] + '\n')
        self.assertEqual(rows('01_portfolio.csv')[0]['resolved_default_rate'], '')

    def test_missing_columns_fail(self):
        with self.assertRaisesRegex(ValueError, 'Missing columns'):
            self.run_data('id,loan_amnt\na,100\n')


if __name__ == '__main__':
    unittest.main()
