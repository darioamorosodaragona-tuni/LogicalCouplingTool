

def pre_mutation(context):
    line = context.current_source_line.strip()
    if line.startswith('logger.'):
        context.skip = True
    if "logger" in line:
        context.skip = True
