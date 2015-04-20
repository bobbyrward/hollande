from __future__ import print_function

from .commands.registry import CommandRegistry
from .repository import Repository
from . import linting


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
        reports = linting.lint_pull_request(repo, args.id)

        # Needs to pull filename from violations
        self.print_reports(reports)

    def print_reports(self, reports):
        for filename, report in reports.iteritems():
            self.print_file_violations(filename, report.file_violations)

    def print_file_violations(self, filename, file_violations):
        for line_number, offset_violations in file_violations.iteritems():
            for offset, violation in offset_violations.iteritems():
                self.print_violation(filename, line_number, offset, violation)

    def print_violation(self, filename, line_number, offset, violation):
        print('{}:{}:{}: {}'.format(filename, line_number, offset, violation))

    def add_arguments(self, parser):
        parser.add_argument('repo', help='Repo name')
        parser.add_argument('id', help='ID of the pull request')
