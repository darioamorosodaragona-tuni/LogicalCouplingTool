from flask import Flask, request, jsonify

from logical_coupling import run as logical_coupling_run
from developer_coupling import run as developer_coupling_run

app = Flask(__name__)


def load_args():
    git_url = request.args.get('git_url')
    branch = request.args.get('branch')
    commit_hash = request.args.get('commit_hash')
    return git_url, branch, commit_hash


def run(function, git_url, branch, commit_hash):
    if git_url is None or branch is None or commit_hash is None:
        # Return an error response if any parameter is missing
        return jsonify({"error": "Missing parameters"}), 400  # 400 is the HTTP status code for Bad Request

    exit_code, messages = function(git_url, branch, commit_hash)

    if exit_code >= 0:

        # You can use these values in your processing logic
        result = {
            "exit_code": exit_code,
            "message": messages
        }
        return jsonify(result), 200  # 200 is the HTTP status code for OK
    else:
        return jsonify({"error": messages}), 500


@app.route('/logical-coupling', methods=['GET'])
def logical_coupling():
    # Access the three arguments from the endpoint
    # You can use these values in your processing logic
    git_url, branch, commit_hash = load_args()

    return run(logical_coupling_run, git_url, branch, commit_hash)


@app.route('/developer-coupling', methods=['GET'])
def developer_coupling():
    # Access the three arguments from the endpoint
    # You can use these values in your processing logic
    git_url, branch, commit_hash = load_args()

    return run(developer_coupling_run, git_url, branch, commit_hash)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
