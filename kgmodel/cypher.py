'''Cypher Queries for the KG Graph'''

CLEANUP_GRAPH = """
	MATCH (n)
	OPTIONAL MATCH (n)-[r]-()
	DELETE n,r
"""

'''Node Load'''
LOAD_STANDARD="""LOAD CSV WITH HEADERS FROM ($uri) AS row
WITH row
WHERE NOT toInteger(trim(row.`id`)) IS NULL
CALL {
  WITH row
  MERGE (n: `STANDARD` { `id`: toInteger(trim(row.`id`)) })
  SET n.`id` = toInteger(trim(row.`id`))
  SET n.`name` = row.`name`
  SET n.`display_name` = row.`display_name`
  SET n.`role` = row.`role`
} IN TRANSACTIONS OF 10000 ROWS;
"""