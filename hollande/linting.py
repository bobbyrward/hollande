from collections import defaultdict


class PullRequestReport(object):
    def __init__(self):
        self.file_violations = defaultdict(dict)
        self.violation_count = 0
        self.skip_violations = ['E501', 'W391']

    def error(self, line_number, offset, text, check):
        for skip in self.skip_violations:
            if text.startswith(skip):
                return

        self.file_violations[line_number][offset] = text
        self.violation_count += 1

    @property
    def violations(self):
        return self.file_violations

    def increment_logical_line(self):
        # self.counters['logical lines'] += 1
        pass

    def init_file(self, filename, lines, expected, line_offset):
        pass

    def get_file_results(self):
        return 0


def remove_preexisting_violations(base_file, base_report, pr_file, pr_report):
    # Remove all violations of the same type at the same location
    for line_number, base_offset_violations in base_report.violations.iteritems():
        for offset, violation in base_offset_violations.iteritems():
            # First check that the violation exists at the same place
            if line_number in pr_report.violations:
                if offset in pr_report.violations[line_number]:
                    if violation == pr_report.violations[line_number][offset]:
                        del pr_report.violations[line_number][offset]
                        pr_report.violation_count -= 1

            matching_offset_lines = []

            # It's gone or moved.  Try to find a matching line with a violation
            for pr_line_number, pr_offset_violations in pr_report.violations.iteritems():
                for pr_offset, pr_violation in pr_offset_violations.iteritems():
                    # The offset has to match or the line has been changed
                    # Even if just indentation, mark it as a violation

                    if pr_offset == offset and pr_violation == violation:
                        matching_offset_lines.append(pr_line_number)

            # Remove lines that haven't changed but have been moved
            for offset_match in matching_offset_lines:
                if base_file[line_number] == pr_file[offset_match]:
                    del pr_report.violations[offset_match][offset]
                    pr_report.violation_count -= 1
