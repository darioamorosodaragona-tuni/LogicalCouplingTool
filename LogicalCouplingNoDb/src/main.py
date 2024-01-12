from flask import Flask, request, jsonify

from logical_coupling import run as logical_coupling_run
from developer_coupling import run as developer_coupling_run
import util

app = Flask(__name__)
logical_coupling_logger = util.setup_logging("logical_coupling")
developer_coupling_logger = util.setup_logging("developer_coupling")




def load_args():
    git_url = request.args.get('git_url')
    branch = request.args.get('branch')
    commits = request.args.get('commits')
    commits_list = commits.split(',')

    return git_url, branch, commits_list


def run(function, git_url, branch, commits_list):

    if function is logical_coupling:
        logger = logical_coupling_logger
    else:
        logger = developer_coupling_logger

    if git_url is None or branch is None or commits_list is None:
        # Return an error response if any parameter is missing
        logger.error("Missing parameters")
        return jsonify({"error": "Missing parameters"}), 400  # 400 is the HTTP status code for Bad Request

    exit_code, messages, commits = function(git_url, branch, commits_list)

    if exit_code >= 0:

        # You can use these values in your processing logic
        result = {
            "exit_code": exit_code,
            "message": messages,
            "commits": commits
        }
        logger.debug(result)
        logger.info("Tool finished successfully")
        return jsonify(result), 200  # 200 is the HTTP status code for OK
    else:
        return jsonify({"error": messages}), 500


@app.route('/logical-coupling', methods=['GET'])
def logical_coupling():

    # Access the three arguments from the endpoint
    # You can use these values in your processing logic
    logical_coupling_logger.info("Logical coupling tool started")
    logical_coupling_logger.debug(f"Request:{request}")
    logical_coupling_logger.debug(f"{request.args}")

    git_url, branch, commits_list = load_args()
    logical_coupling_logger.info("Analyzing project " + git_url + " on branch " + branch + " with commits " + commits_list.__str__())

    return run(logical_coupling_run, git_url, branch, commits_list)


@app.route('/developer-coupling', methods=['GET'])
def developer_coupling():
    # Access the three arguments from the endpoint
    # You can use these values in your processing logic
    git_url, branch, commit_hash = load_args()

    return run(developer_coupling_run, git_url, branch, commit_hash)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
