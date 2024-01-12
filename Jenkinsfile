pipeline {
    agent any

    environment {
        FLASK_APP_URL = 'http://darioserver.duckdns.org:5001'
        LOGICAL_EXIT_CODE = -100
        LOGICAL_MESSAGE = 'UNEXECUTED'
        DEVELOPER_EXIT_CODE = -100
        DEVELOPER_MESSAGE = 'UNEXECUTED'
        WEBHOOK_URL = "https://abb.webhook.office.com/webhookb2/0bb87d12-694d-42e4-b1ac-8789abc7e2f9@372ee9e0-9ce0-4033-a64a-c07073a91ecd/IncomingWebhook/8c4d2fbdbad540c392bc80efafa429e4/c6c993a4-8ced-4242-9ad0-814f68c1bef7"

    stages {
        stage('Logical Coupling') {
            steps {
                script {
                    def result
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                        result = executeCouplingStage('logical-coupling')

                        LOGICAL_EXIT_CODE = result ? result.exitCode : -500
                        LOGICAL_MESSAGE = result ? result.message : 'Service not available'

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
                    def result
                    catchError(buildResult: 'FAILURE', stageResult: 'FAILURE') {
                        result = executeCouplingStage('developer-coupling')
                        DEVELOPER_EXIT_CODE = result ? result.exitCode : -500
                        DEVELOPER_MESSAGE = result ? result.message : 'Service not available'

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

                if WEBHOOK_URL != "" {

                    def logicalFacts = [
                        [name: "LogicalCouplingExitCode", template: "${LOGICAL_EXIT_CODE}"],
                        [name: "LogicalCouplingNessage", template: "${LOGICAL_MESSAGE}"]
                    ]
                    def developerFacts = [
                        [name: "DeveloperNewCommiExitCode", template: "${DEVELOPER_EXIT_CODE}"],
                        [name: "DeveloperNewCommitMessage", template: "${DEVELOPER_MESSAGE}"]
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
                    office365ConnectorSend webhookUrl: "",
                        factDefinitions: facts
                }
            }
        }
    }
}

def executeCouplingStage(couplingType) {
    def repoUrl = env.GIT_URL
    def commitHash = env.GIT_COMMIT
    def branchName = 'main'  // You can customize this if needed

    echo "Repository URL: ${repoUrl}"
    echo "Commit Hash: ${commitHash}"
    echo "Branch Name: ${branchName}"

    def response
    try {
        response = sh(script: """
            curl -G -d 'git_url=${repoUrl}' -d 'commit_hash=${commitHash}' -d 'branch=${branchName}' ${FLASK_APP_URL}/${couplingType}
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

    echo "Exit Code: ${exitCode}"
    echo "Message: ${message}"



    return [exitCode: exitCode, message: message]
}
