import os.path
import collections

import pep8


class PullRequestReport(object):
    def __init__(self):
        self.file_violations = collections.defaultdict(dict)
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


def lint_python_file(repository, base_tree, pr_file):
    # TODO: Need to add logic for deleted files but need to see what the status for that is
    pr_lines = repository.get_blob_as_lines(pr_file.sha)

    pr_report = PullRequestReport()
    pr_checker = pep8.Checker(
        filename=pr_file.filename,
        lines=pr_lines,
        report=pr_report,
    )
    pr_checker.check_all()

    if pr_file.status == 'modified':
        base_lines = repository.get_blob_as_lines(
            repository.get_file_hash_from_tree(base_tree, pr_file.filename).sha
        )

        base_report = PullRequestReport()
        base_checker = pep8.Checker(
            filename=pr_file.filename,
            lines=base_lines,
            report=base_report,
        )
        base_checker.check_all()

        remove_preexisting_violations(
            base_lines,
            base_report,
            pr_lines,
            pr_report,
        )

    return pr_report


def lint_pull_request(repository, pull_request_number):
    pr = repository.get_pull_request(pull_request_number)
    base_tree = repository.get_tree_from_commit(pr.base.sha)

    reports = {}

    lint_dict = {
        '.py': lint_python_file,
    }

    for pr_file in pr.iter_files():
        _, extension = os.path.splitext(pr_file.filename)

        if extension not in lint_dict:
            continue

        reports[pr_file.filename] = lint_dict[extension](repository, base_tree, pr_file)

    return reports
