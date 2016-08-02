from .fullerrorargumentparser import FullErrorArgumentParser


class ArgumentsManager(object):
    def __init__(self, not_required_params):
        self.NotRequiredParams = not_required_params
        self.AutoParams = []
        self.Parser = FullErrorArgumentParser(description='Creates an AWS Cloudformation Stack')
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

        self.Parser.add_argument('--Debug',
                                 metavar='false',
                                 default='false',
                                 choices=['true', 'false'],
                                 required=False,
                                 help='Disable stack rollback on failure')

    def add_parameters_as_arguments(self, parameters):
        for parameter in parameters:
            param_name = parameter.get('ParameterKey', None)
            if param_name is not None:
                if param_name not in self.NotRequiredParams:
                    name = '--' + param_name
                    help_message = parameter.get('Description', None)
                    default_value = parameter.get('DefaultValue', None)
                    self.add_parameter_as_argument(name, default_value, help_message)
                else:
                    self.AutoParams.append(param_name)

    def add_parameter_as_argument(self, name, default_value, help_message):
        self.Parser.add_argument(
            name,
            metavar=default_value,
            required=True,
            help=help_message
        )

    def get_arguments(self):
        return self.Parser.parse_args()

    def get_auto_params(self):
        return self.AutoParams