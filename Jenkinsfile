pipeline {
    agent any

    stages {
        stage('Logical Coupling') {
            steps {
                script {

                    // Replace the URL with the actual URL of your Flask app
                    def flaskAppUrl = 'http://darioserver.duckdns.org:5001/logical-coupling'

                    // Example parameters to pass to the Flask app
                            // Get the repository URL
                    def repoUrl = env.GIT_URL

                    // Get the commit hash
                    def commitHash = env.GIT_COMMIT

                    // Get the branch name
                    // def branchName = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()


                    echo "Repository URL: ${repoUrl}"
                    echo "Commit Hash: ${commitHash}"
                    echo "Branch Name: main"


                    // Use curl to make an HTTP request to the Flask app
                    def response = sh(script: "curl -G -d 'git_url=${repoUrl}' -d 'commit_hash=${commitHash}' -d 'branch=main' http://darioserver.duckdns.org:5001/logical-coupling", returnStdout: true).trim()


                    echo "Raw Response from Flask App: ${response}"

                    // Parse the JSON response
                    def jsonResponse = readJSON text: response

                    // Access exit code and message from the JSON response
                    def exitCode = jsonResponse.exit_code
                    def message = jsonResponse.message

                    echo "Exit Code: ${exitCode}"
                    echo "Message: ${message}"

                    // Determine whether the stage should pass or fail
                    if (exitCode == 0) {
                        echo "Stage passed."
                    } else {
                        error "Stage failed. Exit Code: ${exitCode}, Message: ${message}"
                    }
                }
            }
        }

        stage('Developer Coupling') {
            steps {
                script {

                    // Replace the URL with the actual URL of your Flask app
                    def flaskAppUrl = 'http://darioserver.duckdns.org:5001/developer-coupling'

                    // Example parameters to pass to the Flask app
                            // Get the repository URL
                    def repoUrl = env.GIT_URL

                    // Get the commit hash
                    def commitHash = env.GIT_COMMIT

                    // Get the branch name
                    // def branchName = sh(script: 'git rev-parse --abbrev-ref HEAD', returnStdout: true).trim()


                    echo "Repository URL: ${repoUrl}"
                    echo "Commit Hash: ${commitHash}"
                    echo "Branch Name: main"


                    // Use curl to make an HTTP request to the Flask app
                    def response = sh(script: "curl -G -d 'git_url=${repoUrl}' -d 'commit_hash=${commitHash}' -d 'branch=main' http://darioserver.duckdns.org:5001/logical-coupling", returnStdout: true).trim()


                    echo "Raw Response from Flask App: ${response}"

                    // Parse the JSON response
                    def jsonResponse = readJSON text: response

                    // Access exit code and message from the JSON response
                    def exitCode = jsonResponse.exit_code
                    def message = jsonResponse.message

                    echo "Exit Code: ${exitCode}"
                    echo "Message: ${message}"

                    // Determine whether the stage should pass or fail
                    if (exitCode == 0) {
                        echo "Stage passed."
                    } else {
                        error "Stage failed. Exit Code: ${exitCode}, Message: ${message}"
                    }
                }
            }
        }


    }

}
