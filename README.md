Certainly! Here's the updated README.md file with added instructions for using the Logical Coupling Tool locally:

---

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

## Configuration

The tool can be configured using a `.lcignore` file to specify components to ignore during analysis. Each component to ignore should be listed on a separate line in the file.

## Contributing

Contributions to the Logical Coupling Tool are welcome! To contribute:

1. Fork the repository.
2. Create a new branch.
3. Make your changes.
4. Submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

This README now includes instructions for using the Logical Coupling Tool both as a Flask app and locally, providing flexibility in how users can utilize the tool based on their requirements.