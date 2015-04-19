from .application import app
from .commands.registry import CommandRegistry


@CommandRegistry.register
class GithubTokenCommand(object):
    name = 'github-token'

    def run(self, args):
        app().config.set('github', 'token', args.token)

    def add_arguments(self, parser):
        parser.add_argument('token', help='The github token')
