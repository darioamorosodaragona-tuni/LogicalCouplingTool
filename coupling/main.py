import os
from flask import Flask, request, jsonify
from .logical_coupling import run as logical_coupling_run
from .developer_coupling import run as developer_coupling_run
from . import util
from .my_celery import make_celery
from flask_caching import Cache

app = Flask(__name__)

# Redis configuration using environment variables
app.config.update(
    CELERY_BROKER_URL=os.getenv('REDIS_URL', 'redis://redis:6379/0'),
    CELERY_RESULT_BACKEND=os.getenv('REDIS_URL', 'redis://redis:6379/0')
)

celery = make_celery(app)

# Flask-Caching configuration
app.config['CACHE_TYPE'] = 'redis'
app.config['CACHE_REDIS_URL'] = os.getenv('REDIS_URL', 'redis://redis:6379/0')
cache = Cache(app)

logical_coupling_logger = util.setup_logging("logical_coupling")
developer_coupling_logger = util.setup_logging("developer_coupling")

def load_args():
    git_url = request.args.get('git_url')
    branch = request.args.get('branch')
    commits = request.args.get('commits')
    commits_list = commits.split(',')
    return git_url, branch, commits_list

def run(function, git_url, branch, commits_list):
    if function is logical_coupling_run:
        logger = logical_coupling_logger
    else:
        logger = developer_coupling_logger

    if git_url is None or branch is None or commits_list is None:
        logger.error("Missing parameters")
        return jsonify({"error": "Missing parameters"}), 400

    exit_code, messages, commits = function(git_url, branch, commits_list)

    if exit_code >= 0:
        result = {
            "exit_code": exit_code,
            "message": messages,
            "commits": ",".join(commits)
        }
        logger.debug(result)
        logger.info("Tool finished successfully")
        return jsonify(result), 200
    else:
        return jsonify({"error": messages}), 500

@app.route('/logical-coupling', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def logical_coupling():
    logical_coupling_logger.info("Logical coupling tool started")
    logical_coupling_logger.debug(f"Request:{request}")
    logical_coupling_logger.debug(f"{request.args}")
    git_url, branch, commits_list = load_args()

    # Run Celery task synchronously
    result = run_logical_coupling.apply(args=[git_url, branch, commits_list]).get()
    return jsonify(result), 200

@celery.task
def run_logical_coupling(git_url, branch, commits_list):
    exit_code, messages, commits = logical_coupling_run(git_url, branch, commits_list)
    return {
        "exit_code": exit_code,
        "message": messages,
        "commits": commits
    }

@app.route('/developer-coupling', methods=['GET'])
def developer_coupling():
    git_url, branch, commit_hash = load_args()
    return run(developer_coupling_run, git_url, branch, commit_hash)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
