def create_stack_name(application, environment):
    separator = '-'
    name = separator.join([application, environment])
    return name
