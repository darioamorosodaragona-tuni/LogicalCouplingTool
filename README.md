# Logical Coupling Tool

The Logical Coupling Tool is designed to analyze commits in a software repository and identify logical couplings between different components. It helps in understanding the relationships between different parts of the codebase and can be used for various software maintenance tasks such as refactoring, code reviews, and bug analysis.

## Features

- **Commit Analysis**: Analyze commits in a repository for logical couplings.
- **Visualization**: Visualize logical couplings between components.
- **Alerting**: Generate alerts for changes in logical couplings.
- **Integration**: Integrates with Git repositories for seamless analysis.

## Installation

To install the Logical Coupling Tool, follow these steps:

1. Clone the repository:

   ```bash
   git clone https://github.com/your_username/logical-coupling-tool.git
   ```

2. Navigate to the project directory:

   ```bash
   cd logical-coupling-tool
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Using the Flask App

The Logical Coupling Tool can be deployed as a Flask web application. To use the Flask app, follow these steps:

1. Ensure you have Flask installed:

   ```bash
   pip install flask
   ```

2. Run the Flask app:

   ```bash
   python app.py
   ```

3. Access the following endpoints:

   - **Logical Coupling Analysis**: `http://localhost:5001/logical-coupling`
   - **Developer Coupling Analysis**: `http://localhost:5001/developer-coupling`

#### Endpoint Parameters

The endpoints accept the following parameters:

- `git_url`: URL of the Git repository.
- `branch`: Branch name to analyze.
- `commits`: List of commit hashes to analyze (comma-separated).

#### Jenkins Pipeline Integration

The Logical Coupling Tool can be seamlessly integrated into a Jenkins pipeline to automate the analysis of logical and developer coupling in your software projects. The provided Jenkinsfile demonstrates how to incorporate the tool into your CI/CD workflow. Here's how it works:

1. **Pipeline Configuration**: The Jenkins pipeline is configured to execute the logical coupling analysis in two stages: `Logical Coupling` and `Developer Coupling`. These stages are defined within the `stages` section of the pipeline script.

2. **Environment Variables**: Several environment variables are defined at the beginning of the pipeline script to store important parameters such as the Flask app URL, exit codes, messages, and the webhook URL for sending notifications.

3. **Stage Execution**: Each stage in the pipeline script executes the corresponding analysis (logical or developer coupling) using the `executeCouplingStage` function. This function sends a GET request to the Flask app endpoint (`/logical-coupling` or `/developer-coupling`) with the necessary parameters such as the Git URL, branch name, and commit hash.

4. **Error Handling**: The pipeline script includes error handling mechanisms to catch and handle any exceptions that occur during the execution of each stage. If an error occurs, it sets the exit code to 500 and the message to indicate the type of error encountered.

5. **Post-Build Actions**: After executing the stages, the pipeline script checks the exit codes of both stages. If any stage fails (exit code != 0), the pipeline marks the build as failed. Otherwise, it marks the build as successful.

6. **Notifications**: If a webhook URL is provided, the pipeline script sends notifications to a Teams channel using the Office 365 Connector plugin. These notifications include information about the exit codes and messages from each stage, allowing team members to stay informed about the analysis results.

This Jenkins pipeline provides a robust and automated way to integrate the Logical Coupling Tool into your CI/CD process, enabling you to continuously monitor and improve the quality of your software projects.


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

## Contributing

Contributions to the Logical Coupling Tool are welcome! To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

