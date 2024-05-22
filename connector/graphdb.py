'''Graph database connector for Neo4j'''
import os
from neo4j import GraphDatabase
from neo4j.exceptions import Neo4jError
from kgmodel.cypher import CLEANUP_GRAPH


class NEO4JConnector(object):
    '''Neo4j connector class'''
    def __init__(self):
        self.uri = os.environ.get("NEO4J_URI")
        self.auth = (os.environ.get("NEO4J_USER", "neo4j")
                     , os.environ.get("NEO4J_PASSWORD", "password"))
        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)

    def close(self):
        '''Close the driver'''
        self.driver.close()

    def verify_connectivity(self):
        '''Verify connectivity to the driver'''
        with self.driver.session() as session:
            session.run("MATCH (n) RETURN n LIMIT 1")
            print("Connectivity verified")

    def run_query(self, query):
        '''Run a query on the driver'''
        with self.driver.session() as session:
            result = session.run(query)
            return result

    def run_query_params(self, query, params):
        '''Run a query on the driver with parameters'''
        with self.driver.session() as session:
            result = session.run(query, params)
            return result
    def cleanup_full(self):
        '''Cleanup the database'''
        with self.driver.session() as session:
            try:
                session.run(CLEANUP_GRAPH)
            except Neo4jError as e:
                print("Error in cleanup: " + str(e))

            
