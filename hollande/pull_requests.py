from __future__ import print_function

import os.path
import pep8

from .commands.registry import CommandRegistry
from .repository import Repository
from .linting import PullRequestReport
from .linting import remove_preexisting_violations


@CommandRegistry.register
class ListPullRequestsCommand(object):
    name = 'list-pull-requests'

    def run(self, args):
        repo = Repository(args.repo)

        for pr in repo.gh3_repo.iter_pulls(state='open'):
            print('{}: {}'.format(pr.number, pr.title))

    def add_arguments(self, parser):
        parser.add_argument('repo', help='Repo name')


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
                    base_report,
                    pr_lines,
                    pr_report,
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
