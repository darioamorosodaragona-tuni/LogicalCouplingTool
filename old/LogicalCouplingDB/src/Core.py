from DBManager import connect_to_db
from GitExtractor import GitExtractor
from LogicalCouplingCalculator import LogicalCouplingCalculator
from Neo4jModel import addCouples, getComponentsCoupled
from util import File, Component


def run(branch_name, project_name, repo_url, commit, db_url, db_port, db_username, db_password):
    connect_to_db(project_name, branch_name, db_url, db_port, db_username, db_password)
    extractor = GitExtractor(repo_url, branch_name, commit)
    files = extractor.extract()
    files_modified, components, couples = LogicalCouplingCalculator().calculate(files_modified=files)

    for item in couples:
        files = []
        for file_modified, component in zip(files_modified, components):
            if component == item[0] or component == item[1]:
                files.append(File(path=file_modified, component=component))
        comp_1 = Component(name=item[0])
        comp_2 = Component(name=item[1])

        addCouples(comp_1, comp_2, files)

    for component in getComponentsCoupled():
        print(component)

