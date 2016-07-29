import boto3, os, sys
from cli.argumentsmanager import ArgumentsManager


ROOT_PATH = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = "templates"
TEMPLATE_EXT = ".json"
AWS_REGION = "eu-west-1"

# Params found in template not required as arguments (script will populate them)
notRequiredParams = [
        'DefaultVPCSecurityGroupId',
        'S3LogsBucketName',
        'S3LogsBucketCreate'
]
argumentsManager = ArgumentsManager(notRequiredParams)
arguments = argumentsManager.parse_args()
applicationName = arguments.Application
environment = arguments.Environment

templateFilename = applicationName + TEMPLATE_EXT
templateFilepath = os.path.sep.join([ROOT_PATH, TEMPLATE_DIR,templateFilename])

try:
    with open(templateFilepath, 'r') as templateFile:
        templateContent = templateFile.read()
except:
    print("Unknown application: " + applicationName)
    sys.exit(1)

session = boto3.session.Session(
    region_name=AWS_REGION
)
cfClient = session.client('cloudformation')
response = cfClient.validate_template(TemplateBody=templateContent)
arg = argumentsManager.add_parameters_as_arguments(response.get('Parameters', None))


# cf = boto3.client('cloudformation')
# cf.create_stack(
#     '-'.join([appName, appEnv]),  # Stack name as appName-appEnv
#     cfTemplateContent,  # Template body
#     None,               # Template URL (s3)
#     [
#
#     ],                 # Parameters
#     False,               # Disable Rollback
#     30,                 # TimeoutInMinutes
#     [],                 # NotificationARNs
#     [],                 # Capabilities
#     [],                 # Resource Types
#     None,                 # On Failure action
#     '',                 # Stack Policy Body
#     '',                 # Stack Policy URL
#     [{
#         'app': '',
#         'env': ''
#     }]                  # Tags
# )
#
# appName = 'hello-world'
