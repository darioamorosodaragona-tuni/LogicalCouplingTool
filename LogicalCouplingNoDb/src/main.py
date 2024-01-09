from flask import Flask, request, jsonify

from logical_coupling import main

app = Flask(__name__)

@app.route('/logical-coupling', methods=['GET'])
def process_data():
    # Access the three arguments from the endpoint
    # You can use these values in your processing logic
    git_url = request.args.get('git_url')
    branch = request.args.get('branch')
    commit_hash = request.args.get('commit_hash')

    if git_url is None or branch is None or commit_hash is None:
        # Return an error response if any parameter is missing
        return jsonify({"error": "Missing parameters"}), 400  # 400 is the HTTP status code for Bad Request

    exit_code, messages = main(git_url, branch, commit_hash)


    # You can use these values in your processing logic
    result = {
        "exit_code": exit_code,
        "message": messages
    }
    return jsonify(result), 200  # 200 is the HTTP status code for OK


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
