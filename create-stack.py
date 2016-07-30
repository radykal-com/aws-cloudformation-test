import boto3, os, sys
import aws.stack as stack
import aws.parameters as parameters
from cli.argumentsmanager import ArgumentsManager


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = "templates"
TEMPLATE_EXT = ".json"
AWS_REGION = "eu-west-1"

argumentsManager = ArgumentsManager(parameters.autoParams)
arguments = argumentsManager.parse_args()
applicationName = arguments.Application
environment = arguments.Environment

templateFileName = applicationName + TEMPLATE_EXT
templateFilePath = os.path.sep.join([ROOT_PATH, TEMPLATE_DIR,templateFileName])

try:
    with open(templateFilePath, 'r') as templateFile:
        templateContent = templateFile.read()
except:
    print("Unknown application (template file not found): " + applicationName)
    sys.exit(1)

session = boto3.session.Session(
    region_name=AWS_REGION
)

cfClient = session.client('cloudformation')
response = cfClient.validate_template(TemplateBody=templateContent)
argumentsManager.add_parameters_as_arguments(response.get('Parameters', None))
args = vars(argumentsManager.get_arguments())
autoParams = parameters.set_auto_params_values(
    applicationName,
    environment,
    argumentsManager.get_auto_params(),
    session
)
argParams = parameters.parse_arguments_as_parameters(args)
parameters = autoParams+argParams

cfClient.create_stack(
    StackName=stack.create_stack_name(application=applicationName, environment=environment),
    TemplateBody=templateContent,
    Parameters=parameters
)
