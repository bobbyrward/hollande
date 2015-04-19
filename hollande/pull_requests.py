from __future__ import print_function

import os.path
import pep8
from collections import defaultdict

from .commands.registry import CommandRegistry
from .repository import Repository
from .application import app


@CommandRegistry.register
class ListPullRequestsCommand(object):
    name = 'list-pull-requests'

    def run(self, args):
        repo = app().github.repository('inmar', 'dpn_web_services')

        for pr in repo.iter_pulls(state='open'):
            print(pr.title)

    def add_arguments(self, parser):
        # parser.add_argument('token', help='The github token')
        pass


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

    def increment_logical_line(self):
        # self.counters['logical lines'] += 1
        pass

    def init_file(self, filename, lines, expected, line_offset):
        pass

    def get_file_results(self):
        return 0


def remove_preexisting_violations(base_file, base_file_violations, pr_file, pr_file_violations):
    # Remove all violations of the same type at the same location
    for line_number, base_offset_violations in base_file_violations.iteritems():
        for offset, violation in base_offset_violations.iteritems():
            # First check that the violation exists at the same place
            if line_number in pr_file_violations:
                if offset in pr_file_violations[line_number]:
                    if violation == pr_file_violations[line_number][offset]:
                        del pr_file_violations[line_number][offset]
                        pr_report.violation_count -= 1



@CommandRegistry.register
class LintPullRequestCommand(object):
    name = 'lint-pull-request'

    def run(self, args):
        repo = Repository(args.repo)
        pr = repo.gh3_repo.pull_request(args.id)

        base_tree = repo.gh3_repo.tree(
            repo.gh3_repo.git_commit(pr.base.sha).tree.sha,
        )

        for pr_file in pr.iter_files():
            # added, modified, (deleted or removed?)
            _, extension = os.path.splitext(pr_file.filename)

            if extension != '.py':
                continue

            pr_file_blob = repo.blob(pr_file.sha)
            pr_lines = [
                x + '\n' for x in repo.blob(pr_file.sha).decoded.split('\n')
            ]

            pr_report = PullRequestReport()
            pr_checker = pep8.Checker(
                filename=pr_file.filename,
                lines=pr_lines,
                report=pr_report,
            )
            pr_checker.check_all()

            if pr_file.status == 'added':
                if pr_report.violation_count:
                    self.print_file_violations(pr_file.filename, pr_report.file_violations)
            else:
                base_lines = [
                    x + '\n' for x in repo.blob(repo.get_file_hash_from_tree(base_tree, pr_file.filename).sha).decoded.split('\n')
                ]

                base_report = PullRequestReport()
                base_checker = pep8.Checker(
                    filename=pr_file.filename,
                    lines=base_lines,
                    report=base_report,
                )
                base_checker.check_all()

                remove_preexisting_violations(
                    base_lines,
                    base_report.file_violations,
                    pr_lines,
                    pr_report.file_violations,
                )

                if pr_report.violation_count:
                    self.print_file_violations(pr_file.filename, pr_report.file_violations)

    def print_file_violations(self, filename, file_violations):
        for line_number, offset_violations in file_violations.iteritems():
            for offset, violation in offset_violations.iteritems():
                self.print_violation(filename, line_number, offset, violation)

    def print_violation(self, filename, line_number, offset, violation):
        print('{}:{}:{}: {}'.format(filename, line_number, offset, violation))

    def add_arguments(self, parser):
        parser.add_argument('repo', help='Repo name')
        parser.add_argument('id', help='ID of the pull request')
