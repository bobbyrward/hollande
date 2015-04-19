from functools import wraps


class CommandRegistry(object):
    registry = {}

    @classmethod
    def register(cls, command_class):
        cls.registry[command_class.name] = command_class()
        return command_class

    @classmethod
    def configure_parser(cls, main_parser):
        for command in cls.registry.values():
            sub_parser = main_parser.add_parser(command.name)
            command.add_arguments(sub_parser)
            sub_parser.set_defaults(func=command.run)
