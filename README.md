# Python script to launch AWS Cloudformation templates
This script allows to create cloudformation stacks easily, just providing the template file and passing required arguments when calling the script.

Note: Running this script may incur in AWS costs not included in free-tier.

## Configuration

### Software dependencies
In order to run the script the following requirements must be met:
- Python 3.x (and python binaries path added to system PATH)
- Python libraries dependencies can be installed with the following command (run from the app root directory): _pip install -r requirements.txt_

### Credentials configuration
- The script can authenticate with AWS with the methods described in the Boto3 documentation: http://boto3.readthedocs.io/en/latest/guide/configuration.html, the recomended one is with the ~/.aws/credentials file.

## Limitations

### AWS Region
- Region is hard-coded in the script, actually set as _eu-west-1_ so the methods to define it through config files as shown in the Boto3 documentation will not work.

## Quick start
There is a cloudformation template included within the script called _hello-world.json_. 

It creates a stack composed of:
 - Auto-scaling group of t2.micro instances (free-tier eligible) from 2 to 6 instances running Windows Server 2012 R2
 - Elastic Load Balancer (public access on port 80)
 - CloudWatch alarms and scaling policies
 
The stack has some parameters like:
 - IP CIDR to allow RDP connections
 - IP CIDR to access port 8080
 - Email address to notify auto-scaling actions

The script will show you the required parameters if you provide at least the application and environment such as:

_python create-stack.py_ --Application hello-world --Environment development

To add more stacks just put the cloudformation template files inside templates directory with json extension. To call the template just pass the file name of the template as application (without extension).

## Useful information

### Stack Name
The stack name for each template is automatically set with the following pattern: _application-environment_ so running the hello-world application for development environment will create the stack called _hello-world-development_

### Special parameters
There are some special parameters that act different if present in a template:
- _S3LogsBucketName_ and _S3LogsBucketCreate_: These 2 parameters wont be prompt as inputs for the script. The script will automatically pass the name _logs-application-environment_ (logs-hello-world-development for the previous example) to the template and check if the bucket already exists to pass the flag accordly.
- _DefaultVPCId_: Automatically filled with the default VPC Id.
- _DefaultRouteTableId_: Automatically filled with the Main route-table Id assigned to the Default VPC.
- _DefaultVPCSecurityGroupId_: Automaticalled filled with the default security-group Id of the default VPC.

### Troubleshooting
Run the script with _--Debug true_ to disable stack rollback on failure.

### Predefined tags
The following tags will be created automatically with each stack:
- application: the application name (template file name)
- environment: environment (environment called when creating the stack)

## Usage example (hello-world)
python create-stack.py --Application hello-world --Environment development --Debug False --InstanceType t2.micro --KeyName aKeyPairName --ScalingNotificationEmail notify-me@example.com --RDPAllowCidrIp 8.8.8.8/24 --PrivateAdminCidrIp 8.8.4.4/32
