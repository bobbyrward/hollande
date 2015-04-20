import unittest

from ..linting import PullRequestReport


class TestPullRequestReport(unittest.TestCase):
    def test_normal_usage(self):
        pr_report = PullRequestReport()
        pr_report.init_file('filename.ext', ['1', '2', '3'], None, None)
        pr_report.error(1, 25, 'A ERROR! ERROR! ERROR!', None)
        pr_report.error(2, 24, 'B ERROR! ERROR! ERROR!', None)
        pr_report.error(3, 23, 'C ERROR! ERROR! ERROR!', None)

        # these should be ignored
        pr_report.error(3, 7, 'E501 ERROR! ERROR! ERROR!', None)
        pr_report.error(3, 9, 'W391 ERROR! ERROR! ERROR!', None)

        self.assertEqual(pr_report.violation_count, 3)
        self.assertIn(1, pr_report.violations)
        self.assertIn(25, pr_report.violations[1])
        self.assertEqual(pr_report.violations[1][25], 'A ERROR! ERROR! ERROR!')

        self.assertIn(2, pr_report.violations)
        self.assertIn(24, pr_report.violations[2])
        self.assertEqual(pr_report.violations[2][24], 'B ERROR! ERROR! ERROR!')

        self.assertIn(3, pr_report.violations)
        self.assertIn(23, pr_report.violations[3])
        self.assertEqual(pr_report.violations[3][23], 'C ERROR! ERROR! ERROR!')
