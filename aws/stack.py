def create_stack_name(application, environment):
    separator = '-'
    name = separator.join([application, environment])
    return name


def stack_exists(stack_name, aws_session):
    cf = aws_session.client('cloudformation')
    stacks = cf.describe_stacks().get('Stacks')
    for stack in stacks:
        if stack.get('StackName') == stack_name:
            return True
    return False