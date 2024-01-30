from datetime import datetime

from logical_coupling import run as logical_coupling_run
from developer_coupling import run as developer_coupling_run

# Specify the repository URL, branch, and commits to analyze
repo_url = "/Users/ncdaam/Desktop/UNICOS_Standard_ACX580"
branch = "develop"
commits = ["29cc3e6248b59203e4144089550851fc39f92e4c"]
last_commit = "d0ec6cb450bf6f18493fe33581dd94ff1a2a260d"

start = datetime.now()
# Run logical coupling analysis
exit_code, messages, _ = logical_coupling_run(repo_url, branch, commits, last_commit)
end = datetime.now()
print(end - start)

# Alternatively, run developer coupling analysis
# exit_code, messages = developer_coupling_run(repo_url, branch, commits)

# Process the results based on the exit code and messages
if exit_code == 0:
    print("No logical couplings detected.")
elif exit_code == 1:
    print("Logical couplings detected:")
    # print(messages)
else:
    print("An error occurred:")
    print(messages)
