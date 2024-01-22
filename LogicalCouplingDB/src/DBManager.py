from neomodel import config
from neo4j import GraphDatabase


def connect_to_db(database_name="neo4j", url='localhost', port='7687', username='neo4j', password='neo4j'):
    # uri = 'bolt://' + url + ':' + port
    # driver = GraphDatabase.driver(uri, auth=(username, password))

    # with driver.session(database="system") as session:
    #     with session.begin_transaction() as tx:
    #         tx.run(f"CREATE DATABASE {project_name}_{branch_name} IF NOT EXISTS")
    #     session.last_bookmark()


    config.DATABASE_URL = 'bolt://' + username + ':' + password + '@' + url + ':' + port + '/' +  database_name

