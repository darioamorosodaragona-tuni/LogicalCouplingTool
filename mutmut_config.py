

def pre_mutation(context):
    line = context.current_source_line.strip()
    if line.startswith('logger.'):
        context.skip = True
    if "logger" in line:
        context.skip = True
    if "to.csv(file commits)" in line:
        context.skip = True
    if "repo_name = repo_url.split(" in line:
        context.skip = True