from .fullerrorargumentparser import FullErrorArgumentParser


class ArgumentsManager(object):
    def __init__(self, not_required_params):
        self.Parser = FullErrorArgumentParser(description='Creates an AWS Cloudformation Stack')
        self.NotRequiredParams = not_required_params
        self.add_default_arguments()

    def parse_args(self):
        args, unknown = self.Parser.parse_known_args()
        return args

    def add_default_arguments(self):
        self.Parser.add_argument('--Application',
                                 metavar='hello-world',
                                 type=str,
                                 required=True,
                                 help='Application Name (must match template filename)')
        self.Parser.add_argument('--Environment',
                                 metavar='development',
                                 choices=['development', 'staging', 'production'],
                                 required=True,
                                 help='AWS Environment, allowed values: development, staging, production')

    def add_parameters_as_arguments(self, parameters):
        for parameter in parameters:
            self.add_parameter_as_argument(parameter)
        return self.Parser.parse_args()

    def add_parameter_as_argument(self, parameter):
        param_name = parameter.get('ParameterKey', None)
        if param_name is not None and param_name not in self.NotRequiredParams:
            arg_name = '--' + param_name
            arg_desc = parameter.get('Description', None)
            arg_default_value = parameter.get('DefaultValue', None)

            self.Parser.add_argument(
                arg_name,
                metavar=arg_default_value,
                required=True,
                help=arg_desc
            )
