pipeline {
    agent any
    environment {
        branchName = "${env.GIT_BRANCH.split('/').size() == 1 ? env.GIT_BRANCH.split('/')[-1] : env.GIT_BRANCH.split('/')[1..-1].join('/')}"
        commitHash = sh (script: "git log -n 1 --pretty=format:'%H'", returnStdout: true)
        scmUrl = scm.getUserRemoteConfigs()[0].getUrl()
    }
    stages {
//         stage('Logical Coupling') {
//             steps {
//               sh 'apt-get install python'
//               sh 'python pip install -r requirements.txt'
//               sh 'python main.py  --branch ${branchName} --commit_hash ${commitHash} --repo_url ${scmUrl}'
//             }
//         }

        stage('Load Docker Image') {
            steps {
                script {
                    sh 'docker load -i logical_coupling.tar'
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    sh 'docker run logical_coupling_1 --branch ${branchName} --commit_hash ${commitHash} --repo_url ${scmUrl}'
                }
            }
        }

        stage('Compile') {
            steps {
                echo 'Compile the source code'
            }
        }
        stage('Security Check') {
            steps {
                echo 'Run the security check against the application'
            }
        }
        stage('Run Unit Tests') {
            steps {
                echo 'Run unit tests from the source code'
            }
        }
        stage('Run Integration Tests') {
            steps {
                echo 'Run only crucial integration tests from the source code'
            }
        }
        stage('Publish Artifacts') {
            steps {
                echo 'Sve the assemblies generated from the compilation'
            }
        }
    }
}