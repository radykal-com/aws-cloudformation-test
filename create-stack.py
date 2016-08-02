import boto3, os, sys
import aws.stack as stack
import aws.parameters as parameters
from cli.argumentsmanager import ArgumentsManager


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = "templates"
TEMPLATE_EXT = ".json"
AWS_REGION = "eu-west-1"

session = boto3.session.Session(
    region_name=AWS_REGION
)

argumentsManager = ArgumentsManager(parameters.autoParams)
arguments = argumentsManager.parse_args()
application = arguments.Application
environment = arguments.Environment

templateFileName = application + TEMPLATE_EXT
templateFilePath = os.path.sep.join([ROOT_PATH, TEMPLATE_DIR,templateFileName])
try:
    with open(templateFilePath, 'r') as templateFile:
        templateContent = templateFile.read()
        print("Found template file for application: " + application)
except:
    sys.stderr.write("Error: Unknown application (template file not found): " + application)
    sys.exit(1)

stackName = stack.create_stack_name(application, environment)
if stack.stack_exists(stackName, session):
    sys.stderr.write("Error: Stack with name " + stackName + " already exists")
    sys.exit(1)

cfClient = session.client('cloudformation')
response = cfClient.validate_template(TemplateBody=templateContent)
print("Stack template validated")

print("Passing cli-arguments as stack parameters")
argumentsManager.add_parameters_as_arguments(response.get('Parameters', None))
args = vars(argumentsManager.get_arguments())
autoParams = parameters.set_auto_params_values(
    application,
    environment,
    argumentsManager.get_auto_params(),
    session
)
argParams = parameters.parse_arguments_as_parameters(args)
parameters = autoParams+argParams

debug = True if args.get('Debug') == 'true' else False
print("Creating stack with name: " + stackName)
cfClient.create_stack(
    StackName=stackName,
    TemplateBody=templateContent,
    Parameters=parameters,
    DisableRollback=debug,
    Tags=[
        {
            'Key': 'application',
            'Value': application
        },
        {
            'Key': 'environment',
            'Value': environment
        }
    ]
)
print("Stack creation running...waiting for completion")
waiter = cfClient.get_waiter('stack_create_complete')
waiter.wait(StackName=stackName)
print("Stack created")
