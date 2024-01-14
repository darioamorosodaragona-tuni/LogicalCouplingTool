pipeline {
    agent any

    environment {
        FLASK_APP_URL = 'http://darioserver.duckdns.org:5001'
        LOGICAL_EXIT_CODE = -100
        LOGICAL_MESSAGE = 'UNEXECUTED'
        LOGICAL_COMMITS = ''

        DEVELOPER_EXIT_CODE = -100
        DEVELOPER_MESSAGE = 'UNEXECUTED'
        DEVELOPER_COMMITS = ''
        WEBHOOK_URL = "https://abb.webhook.office.com/webhookb2/0bb87d12-694d-42e4-b1ac-8789abc7e2f9@372ee9e0-9ce0-4033-a64a-c07073a91ecd/IncomingWebhook/8c4d2fbdbad540c392bc80efafa429e4/c6c993a4-8ced-4242-9ad0-814f68c1bef7"
    }

    stages {
        stage('Logical Coupling') {
            steps {
                script {
                    def commits = sh(script: "git log --pretty=format:'%H' origin/main..main", returnStdout: true).trim().split('\n')
                    def result
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                        result = executeCouplingStage('logical-coupling', commits)

                        LOGICAL_EXIT_CODE = result ? result.exitCode : -500
                        LOGICAL_MESSAGE = result ? result.message : 'Service not available'
                        LOGICAL_COMMITS = result ? result.commits : ''

                        if (result.exitCode != 0) {
                                error "Stage failed. Exit Code: ${exitCode}, Message: ${message}"
                        }
                    }
                }
            }
        }

        stage('Developer Coupling') {
            steps {
                script {
                    def commits = sh(script: "git log --pretty=format:'%H' origin/${BRANCH_NAME}..${BRANCH_NAME}", returnStdout: true).trim().split('\n')
                    def result
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                        result = executeCouplingStage('developer-coupling', commits)
                        DEVELOPER_EXIT_CODE = result ? result.exitCode : -500
                        DEVELOPER_MESSAGE = result ? result.message : 'Service not available'
                        DEVELOPER_COMMITS = result ? result.commits : ''

                        if (result.exitCode != 0) {
                                error "Stage failed. Exit Code: ${exitCode}, Message: ${message}"
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                echo "LOGICAL_EXIT_CODE: ${LOGICAL_EXIT_CODE}"
                echo "DEVELOPER_EXIT_CODE: ${DEVELOPER_EXIT_CODE}"

                 if (LOGICAL_EXIT_CODE != 0 || DEVELOPER_EXIT_CODE != 0 ) {
                    currentBuild.result = 'FAILURE'
                } else {
                    currentBuild.result = 'SUCCESS'
                }

                if(WEBHOOK_URL != ""){
                    def logicalFacts = [
                        [name: "LogicalCouplingExitCode", template: "${LOGICAL_EXIT_CODE}"],
                        [name: "LogicalCouplingMessage", template: "${LOGICAL_MESSAGE}"],
                        [name: "LogicalCouplingCommits", template: "${LOGICAL_COMMITS}"]
                    ]
                    def developerFacts = [
                        [name: "DeveloperNewCommiExitCode", template: "${DEVELOPER_EXIT_CODE}"],
                        [name: "DeveloperNewCommitMessage", template: "${DEVELOPER_MESSAGE}"],
                        [name: "DeveloperNewCommitCommits", template: "${DEVELOPER_COMMITS}"]
                    ]

                    def facts

                    // If both stages are executed, format fact definitions with the values of each stage
                    if (LOGICAL_EXIT_CODE != -100 && DEVELOPER_EXIT_CODE != -100) {
                        facts = logicalFacts + developerFacts
                    }
                    else if (LOGICAL_EXIT_CODE != -100){
                        facts = logicalFacts
                    }
                    else if (DEVELOPER_EXIT_CODE != -100){
                        facts = developerFacts
                    }

                    // Send notifications with exitCode and message from each stage
                    office365ConnectorSend webhookUrl: WEBHOOK_URL,
                        factDefinitions: facts
                }
            }
        }
    }
}

def executeCouplingStage(couplingType, commits) {
    def repoUrl = env.GIT_URL
    def branchName = 'main'  // You can customize this if needed

    echo "Repository URL: ${repoUrl}"
    echo "Commits: ${commits.join(',')}"
    echo "Branch Name: ${branchName}"

    def response
    try {
        response = sh(script: """
            curl -G -d 'git_url=${repoUrl}' -d 'commits=${commits.join(',')}' -d 'branch=${branchName}' ${FLASK_APP_URL}/${couplingType}
        """, returnStdout: true).trim()
    } catch (Exception e) {
        return [exitCode: 500, message: 'Server did not respond']
    }

    if (response == null) {
        return [exitCode: 500, message: 'Server response is null']
    }

    echo "Raw Response from Flask App: ${response}"

    def jsonResponse = readJSON text: response
    def exitCode = jsonResponse.exit_code
    def message = jsonResponse.message
    def commits_to_notify = jsonResponse.commits

    echo "Exit Code: ${exitCode}"
    echo "Message: ${message}"
    echo "Commits: ${commits_to_notify}"

    return [exitCode: exitCode, message: message, commits: commits_to_notify]
}
