# Logical Coupling Tool

The Logical Coupling Tool is designed to analyze commits in a software repository and identify logical couplings between different components. It helps in understanding the relationships between different parts of the codebase and can be used for various software maintenance tasks such as refactoring, code reviews, and bug analysis.

## Features

- **Commit Analysis**: Analyze commits in a repository for logical couplings.
- **Visualization**: Visualize logical couplings between components.
- **Alerting**: Generate alerts for changes in logical couplings.
- **Integration**: Integrates with Git repositories for seamless analysis.


#### Project Structure

```
project_root
|_ coupling
   |_ __init__.py
   |_ main.py
   |_ my_celery.py
   |_ logical_coupling.py
   |_ developer_coupling.py
   |_ util.py
|_ docker-compose.yml
|_ Dockerfile
|_ nginx.conf
|_ requirements.txt
|_ Jenkinsfile
```

### Building and Running the Project

#### Prerequisites

- Docker
- Docker Compose

#### Steps

1. **Clone the repository:**

   ```sh
   git clone <repository_url>
   cd project_root
   ```

2. **Build and run the Docker containers:**

   ```sh
   docker-compose up --build
   ```

   This command will build the Docker images and start the containers for the Flask application, Redis, and Nginx.


### Jenkins Pipeline Integration

The Logical Coupling Tool can be seamlessly integrated into a Jenkins pipeline to automate the analysis of logical and developer coupling in your software projects. The provided Jenkinsfile demonstrates how to incorporate the tool into your CI/CD workflow. Here's how it works:

1. **Pipeline Configuration**: The Jenkins pipeline is configured to execute the logical coupling analysis in two stages: `Logical Coupling` and `Developer Coupling`. These stages are defined within the `stages` section of the pipeline script.

2. **Environment Variables**: Several environment variables are defined at the beginning of the pipeline script to store important parameters such as the Flask app URL, exit codes, messages, and the webhook URL for sending notifications.

3. **Stage Execution**: Each stage in the pipeline script executes the corresponding analysis (logical or developer coupling) using the `executeCouplingStage` function. This function sends a GET request to the Flask app endpoint (`/logical-coupling` or `/developer-coupling`) with the necessary parameters such as the Git URL, branch name, and commit hash.

4. **Error Handling**: The pipeline script includes error handling mechanisms to catch and handle any exceptions that occur during the execution of each stage. If an error occurs, it sets the exit code to 500 and the message to indicate the type of error encountered.

5. **Post-Build Actions**: After executing the stages, the pipeline script checks the exit codes of both stages. If any stage fails (exit code != 0), the pipeline marks the build as failed. Otherwise, it marks the build as successful.

6. **Notifications**: If a webhook URL is provided, the pipeline script sends notifications to a Teams channel using the Office 365 Connector plugin. These notifications include information about the exit codes and messages from each stage, allowing team members to stay informed about the analysis results.

This Jenkins pipeline provides a robust and automated way to integrate the Logical Coupling Tool into your CI/CD process, enabling you to continuously monitor and improve the quality of your software projects.

#### Teams Notification: Webhook URL

To send notifications to a Teams channel, you need to obtain a webhook URL for the channel. Here's how you can get the webhook URL: https://learn.microsoft.com/en-us/microsoftteams/platform/webhooks-and-connectors/how-to/add-incoming-webhook?tabs=newteams%2Cdotnet.
Save the webhook URL, you will need it in the next step.

#### Configuring the Jenkins File

To configure the Jenkins file, follow these steps:

1. **Update the Jenkinsfile with the following variables:**

   ```groovy
   environment {
       # Update the following variables with appropriate values
       FLASK_APP_URL = 'http://localhost:8000'
       WEBHOOK_URL = "WEBHOOK_URL_OF_THE_TEAMS_CHANNEL_TO_SEND_NOTIFICATIONS"
   }
   ```
   
Use the webhook URL obtained in the previous step to replace `WEBHOOK_URL_OF_THE_TEAMS_CHANNEL_TO_SEND_NOTIFICATIONS`.
Set the `FLASK_APP_URL` to the URL of the logical_coupling tool. Remember that the tool is running on port 8000.

2**Configure Jenkins Pipeline:**

   - Go to Jenkins Dashboard
   - Create a new Pipeline job
   - In the Pipeline configuration, point to your repository and specify the Jenkinsfile path

3**Configure the Jenkinsfile stages:**

   Ensure the `executeCouplingStage` function correctly sends requests to your Flask application and handles the responses. The function should look like this:

   ```groovy
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
               curl -G -d 'git_url=${repoUrl}' -d 'commits=${commitHash}' -d 'branch=${branchName}' ${FLASK_APP_URL}/${couplingType}
           """, returnStdout: true).trim()
       } catch (Exception e) {
           return [exitCode: 500, message: 'Server did not respond']
       }

       if (response == null) {
           return [exitCode: 500, message:'Server response is null']
       }

       echo "Raw Response from Flask App: ${response}"

       def jsonResponse = readJSON text: response
       def exitCode = jsonResponse.exit_code
       def message = jsonResponse.message

       echo "Exit Code: ${exitCode}"
       echo "Message: ${message}"

       return [exitCode: exitCode, message: message]
   }
   ```

4. **Set up the Jenkins job:**

   - Create a new job in Jenkins.
   - Choose "Pipeline" and configure it to use your repository and Jenkinsfile.

5**Run the Jenkins job:**

   Trigger the Jenkins job to build and deploy the application.



### Using the Logical Coupling Tool   

Access the following endpoints:

   - **Logical Coupling Analysis**: `http://localhost:8000/logical-coupling`
   - **Developer Coupling Analysis**: `http://localhost:8000/developer-coupling`

#### Endpoint Parameters

The endpoints accept the following parameters:

- `git_url`: URL of the Git repository.
- `branch`: Branch name to analyze.
- `commits`: List of commit hashes to analyze (comma-separated).



### Using the Tool Locally

You can also use the Logical Coupling Tool locally by importing and calling the appropriate functions in your Python script. Here's an example of how to use it:

```python
from logical_coupling import run as logical_coupling_run
from developer_coupling import run as developer_coupling_run

# Specify the repository URL, branch, and commits to analyze
repo_url = "https://github.com/example/repo.git"
branch = "main"
commits = ["abc", "def"]

# Run logical coupling analysis
exit_code, messages = logical_coupling_run(repo_url, branch, commits)

# Alternatively, run developer coupling analysis
# exit_code, messages = developer_coupling_run(repo_url, branch, commits)

# Process the results based on the exit code and messages
if exit_code == 0:
    print("No logical couplings detected.")
else:
    print("Logical couplings detected:")
    print(messages)
```
## Return Values

Upon completion of analysis, the app either in Flask mode or used locally returns the following values:

- **Exit Code**: Indicates the outcome of the analysis.
  - **Exit Code 0**: No logical couplings detected.
  - **Exit Code 1**: Logical couplings detected.

- **Message**: Additional information or messages related to the analysis outcome.
  - For example, if logical couplings are detected, the message might provide details about the detected couplings. If no couplings are detected, the message could indicate that no couplings were found.

## Configuration

The Logical Coupling Tool can be configured using a `.lcignore` file to specify components to ignore during analysis. Each component to ignore should be listed on a separate line in the file.
The `.lcignore` file should be placed in the root directory of the repository.

### Example .lcignore File

Here's an example of how to structure a `.lcignore` file:

```plaintext
tests/*
docs/*
config.yaml
*.py
```

In this example:

- `tests/*`: Ignores all components under the "tests" directory.
- `docs/*`: Ignores all components under the "docs" directory.
- `config.yaml`: Ignores the specific file named "config.yaml".
- `*.py`: Ignores all Python files.

### Notes

- Ensure that the `FLASK_APP_URL` and `WEBHOOK_URL` environment variables are correctly set to point to your Flask application and Teams webhook URL, respectively.
- The `docker-compose.yml` is set to expose the application on port `8000` through Nginx. Adjust the port as needed.
- The log files and data directories are mapped to Docker volumes to persist data.

This should provide you with a working setup for building, running, and managing your project using Docker and Jenkins.

## Contributing

Contributions to the Logical Coupling Tool are welcome! To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

