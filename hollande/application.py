import argparse

import github3

from .commands.registry import CommandRegistry
from .config import Configuration


_APPLICATION = None


class Application(object):
    def __init__(self):
        self._github = None
        self._config = Configuration()

    @property
    def config(self):
        return self._config

    @property
    def github(self):
        if self._github is None:
            self._github = github3.login(
                token=self.config.get('github', 'token'),
            )

        return self._github

    def main(self):
        parser = argparse.ArgumentParser(
            description='A linting bot for github',
        )

        sub_parsers = parser.add_subparsers()
        CommandRegistry.configure_parser(sub_parsers)

        parsed_arguments = parser.parse_args()
        parsed_arguments.func(parsed_arguments)


def app():
    return _APPLICATION


def main():
    global _APPLICATION
    _APPLICATION = Application()
    _APPLICATION.main()
