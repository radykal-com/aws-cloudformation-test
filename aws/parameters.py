import botocore
import sys

DefaultVPCId = None


def parse_arguments_as_parameters(arguments):
    parameters = []
    for name, value in arguments.items():
        if name not in excludeParams:
            parameter = create_parameter(name, value)
            parameters.append(parameter)
    return parameters


def create_parameter(name, value):
    return {
            'ParameterKey': name,
            'ParameterValue': value,
            'UsePreviousValue': False
        }


def set_auto_params_values(application, environment, parameters_names, aws_session):
    parameters = []
    for parameter_name in parameters_names:
        if parameter_name in autoParams:
            value = autoParams[parameter_name](application, environment, aws_session)
            parameter = create_parameter(parameter_name, value)
            parameters.append(parameter)
    return parameters


def get_default_vpc_security_group(application, environment, aws_session):
    ec2_resource = aws_session.resource('ec2')
    ec2_client = ec2_resource.meta.client
    default_vpc_id = get_default_vpc_id(application, environment, aws_session)
    return get_default_security_group(ec2_client, default_vpc_id)


def get_default_vpc_id(application, environment, aws_session):
    global DefaultVPCId
    if DefaultVPCId is None:
        ec2_resource = aws_session.resource('ec2')
        ec2_client = ec2_resource.meta.client
        res = ec2_client.describe_vpcs()
        vpcs = res.get('Vpcs')
        for vpc in vpcs:
            if vpc.get('IsDefault'):
                DefaultVPCId = vpc.get('VpcId')
    return DefaultVPCId


def get_default_security_group(ec2_client, default_vpc_id):
    res = ec2_client.describe_security_groups()
    security_groups = res.get('SecurityGroups')
    for security_group in security_groups:
        if security_group.get('VpcId') == default_vpc_id:
            return security_group.get('GroupId')


def get_default_route_table_id(application, environment, aws_session):
    vpcId = get_default_vpc_id(application, environment, aws_session)
    ec2_resource = aws_session.resource('ec2')
    ec2_client = ec2_resource.meta.client
    res = ec2_client.describe_route_tables()
    route_tables = res.get('RouteTables')
    for rt in route_tables:
        if rt.get('VpcId') == vpcId:
            associations = rt.get('Associations')
            for assoc in associations:
                if assoc.get('Main') == True:
                    return rt.get('RouteTableId')


def get_s3_logs_bucket_name(application, environment, aws_session):
    return '-'.join(['logs', application, environment])


def create_s3_logs_bucket(application, environment, aws_session):
    s3 = aws_session.resource('s3')
    bucket_name = get_s3_logs_bucket_name(application, environment, aws_session)
    if check_s3_bucket_exists(s3, bucket_name):
        print("[WARNING]: Found S3 bucket [%s] under your account." % bucket_name)
        print("[WARNING]: Please verify the access policies manually or stack resources may not have access to it.")
        return 'No'
    else:
        print("S3 bucket [%s] will be created if resource is present in the stack template" % bucket_name)
        return 'Yes'


def check_s3_bucket_exists(s3, bucket_name):
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        if check_s3_bucket_ownership(s3, bucket_name):
            return True
        else:
            sys.stderr.write("Could not detect %s bucket ownership." % bucket_name)
            exit(50)
    except botocore.exceptions.ClientError as e:
        if e.response['ResponseMetadata']['HTTPStatusCode'] == 404:
            return False
        elif e.response['ResponseMetadata']['HTTPStatusCode'] == 403:
            sys.stderr.write("S3 Bucket [%s] already exists and your account has no access to it." % bucket_name)
            exit(51)


def check_s3_bucket_ownership(s3, bucket_name):
    if s3.Bucket(bucket_name) in s3.buckets.all():
        return True


# Dictionary must be declared after the functions declarations in order to work
autoParams = {
    'DefaultVPCId': get_default_vpc_id,
    'DefaultRouteTableId': get_default_route_table_id,
    'DefaultVPCSecurityGroupId': get_default_vpc_security_group,
    'S3LogsBucketName': get_s3_logs_bucket_name,
    'S3LogsBucketCreate': create_s3_logs_bucket
}

# This parameters wont be passed to the cloudformation stack creation
excludeParams = [
    'Application',
    'Environment',
    'Debug'
]