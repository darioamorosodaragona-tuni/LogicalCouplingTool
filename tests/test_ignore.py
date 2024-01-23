import fnmatch
import unittest


class TestCalculator(unittest.TestCase):
    # Replace these values with your Neo4j database credentials and URI
    path = ".ProjectToTestLogicalCouplingTool"

    def test_ignore_single_file(self):
        to_ignore = ["Jenkinsfile"]  # Add file names and patterns you want to ignore to this list
        modified_files = ["Jenkinsfile", "src/main/java/com/example/demo/DemoApplication.java"]
        result = []

        for files in modified_files:
            if not any(fnmatch.fnmatch(files, pattern) for pattern in to_ignore):
                result.append(files)

        self.assertEqual(result, ["src/main/java/com/example/demo/DemoApplication.java"])

    if __name__ == '__main__':
        unittest.main()
