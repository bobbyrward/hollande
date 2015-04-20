import unittest

from ..linting import remove_preexisting_violations
from ..linting import PullRequestReport


class TestRemovePreExistingViolations(unittest.TestCase):
    def setUp(self):
        self.base_report = PullRequestReport()
        self.pr_report = PullRequestReport()

        self.base_lines = [str(x) for x in range(250)]
        self.base_report.init_file('filename.ext', self.base_lines, None, None)

        self.pr_lines = self.base_lines[:]
        self.pr_lines[10:10] = ['A', 'B', 'C', 'D', 'E', 'F']
        self.pr_report.init_file('filename.ext', self.pr_lines, None, None)

    def _add_exact_match(self):
        self.base_report.error(4, 0, 'EXACT MATCH', None)
        self.pr_report.error(4, 0, 'EXACT MATCH', None)

    def _add_no_match_different_line(self):
        self.base_report.error(1, 0, 'SAME VIOLATION', None)
        self.pr_report.error(2, 0, 'SAME VIOLATION', None)

    def _add_no_match_same_line(self):
        self.base_report.error(3, 0, 'ORIGINAL VIOLATION', None)
        self.pr_report.error(3, 0, 'NEW VIOLATION', None)

    def _add_no_match_same_line_diff_col(self):
        self.base_report.error(3, 0, 'DIFFERENT COL', None)
        self.pr_report.error(3, 1, 'DIFFERENT COL', None)

    def _add_pushed_violation(self):
        self.base_report.error(20, 0, 'PUSHED', None)
        self.pr_report.error(26, 0, 'PUSHED', None)

    def _add_pushed_violation_diff_col(self):
        self.base_report.error(30, 0, 'PUSHED DIFF COL', None)
        self.pr_report.error(36, 1, 'PUSHED DIFF COL', None)

    def _add_pushed_violation_diff_violation(self):
        self.base_report.error(40, 0, 'PUSHED DIFF ORIGINAL', None)
        self.pr_report.error(46, 0, 'PUSHED DIFF NEW', None)

    def _assert_violation_count(self, base_count, pr_count):
        self.assertEqual(self.base_report.violation_count, base_count)
        self.assertEqual(self.pr_report.violation_count, pr_count)

    def _do_remove(self):
        remove_preexisting_violations(
            self.base_lines,
            self.base_report,
            self.pr_lines,
            self.pr_report,
        )

    def test_exact_matches(self):
        self._add_exact_match()
        self._assert_violation_count(1, 1)
        self._do_remove()
        self._assert_violation_count(1, 0)

    def test_no_match_same_line(self):
        self._add_no_match_same_line()
        self._assert_violation_count(1, 1)
        self._do_remove()
        self._assert_violation_count(1, 1)

    def test_no_match_same_line_diff_col(self):
        self._add_no_match_same_line_diff_col()
        self._assert_violation_count(1, 1)
        self._do_remove()
        self._assert_violation_count(1, 1)

    def test_no_match_different_line(self):
        self._add_no_match_different_line()
        self._assert_violation_count(1, 1)
        self._do_remove()
        self._assert_violation_count(1, 1)

    def test_pushed(self):
        self._add_pushed_violation()
        self._assert_violation_count(1, 1)
        self._do_remove()
        self._assert_violation_count(1, 0)

    def test_pushed_diff_col(self):
        self._add_pushed_violation_diff_col()
        self._assert_violation_count(1, 1)
        self._do_remove()
        self._assert_violation_count(1, 1)

    def test_pushed_diff_violation(self):
        self._add_pushed_violation_diff_violation()
        self._assert_violation_count(1, 1)
        self._do_remove()
        self._assert_violation_count(1, 1)

    def test_all(self):
        self._add_exact_match()
        self._add_no_match_same_line()
        self._add_no_match_same_line_diff_col()
        self._add_no_match_different_line()
        self._add_pushed_violation()
        self._add_pushed_violation_diff_col()
        self._add_pushed_violation_diff_violation()

        self._assert_violation_count(7, 7)
        self._do_remove()
        self._assert_violation_count(7, 5)
