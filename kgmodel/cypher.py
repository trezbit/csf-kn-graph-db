'''Cypher Queries for the KG Graph'''
from config.includes import PUBLIC_GRAPH_DATA_ROOT
CLEANUP_GRAPH = """
	MATCH (n)
	OPTIONAL MATCH (n)-[r]-()
	DELETE n,r
"""

CREATE_CONSTRAINT ="""CREATE CONSTRAINT id___LABEL___uniq IF NOT EXISTS FOR (n: __LABEL__) REQUIRE (n.`id`) IS UNIQUE;"""

'''Node Load CYBHER Queries'''
LOAD_STANDARD="""
    LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/standard.csv'
    AS row WITH row
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
LOAD_CONTROL="""
LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/control.csv'
AS row WITH row
WHERE NOT toInteger(trim(row.`id`)) IS NULL
CALL {
  WITH row
  MERGE (n: `CONTROL` { `id`: toInteger(trim(row.`id`)) })
  SET n.`id` = toInteger(trim(row.`id`))
  SET n.`functional_category` = row.`functional_category`
  SET n.`name` = row.`name`
} IN TRANSACTIONS OF 10000 ROWS;
"""

'''Relation Load CYBHER Queries'''

LOAD_HAS_CONTROL="""
LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/has_control.csv'
AS row WITH row 
CALL {
  WITH row
  MATCH (source: `STANDARD` { `id`: toInteger(trim(row.`from_id`)) })
  MATCH (target: `CONTROL` { `id`: toInteger(trim(row.`to_id`)) })
  MERGE (source)-[r: `HAS_CONTROL`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;
"""

LOAD_MAPS_TO="""
LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/maps_to.csv'
AS row WITH row 
CALL {
  WITH row
  MATCH (source: `CONTROL` { `id`: toInteger(trim(row.`from_id`)) })
  MATCH (target: `CONTROL` { `id`: toInteger(trim(row.`to_id`)) })
  MERGE (source)-[r: `MAPS_TO`]->(target)
} IN TRANSACTIONS OF 10000 ROWS;
"""


LOAD_KEYCONCEPT= """
LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/keyconcept.csv' 
AS row WITH row
WHERE NOT toInteger(trim(row.`id`)) IS NULL
CALL {
  WITH row
  MERGE (n: `KEYCONCEPT` { `id`: toInteger(trim(row.`id`)) })
  SET n.`id` = toInteger(trim(row.`id`))
  SET n.`name` = row.`name`
  SET n.`accronym` = row.`accronym`
} IN TRANSACTIONS OF 10000 ROWS;
"""

LOAD_ASSESSMENTQ="""
LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/asessmentq.csv' 
AS row WITH row
WHERE NOT toInteger(trim(row.`id`)) IS NULL
CALL {
  WITH row
  MERGE (n: `QUESTION` { `id`: toInteger(trim(row.`id`)) })
  SET n.`id` = toInteger(trim(row.`id`))
  SET n.`name` = row.`name`
  SET n.`scope` = row.`scope`
  SET n.`rationale` = row.`rationale`
} IN TRANSACTIONS OF 10000 ROWS;
"""


LOAD_CONTROL_CAPTURES="""
LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/control_captures.csv'
AS row WITH row 
CALL {
  WITH row
  MATCH (source: `CONTROL` { `id`: toInteger(trim(row.`from_id`)) })
  MATCH (target: `KEYCONCEPT` { `id`: toInteger(trim(row.`to_id`)) })
  MERGE (source)-[r: `CAPTURES`]->(target)
  SET r.`from_id` = toInteger(trim(row.`from_id`))
  SET r.`to_id` = toInteger(trim(row.`to_id`))
  SET r.`confidence` = toFloat(trim(row.`confidence`))
} IN TRANSACTIONS OF 10000 ROWS;
"""

LOAD_ASSESSES_CONTROL=""" 
LOAD CSV WITH HEADERS FROM '""" +  PUBLIC_GRAPH_DATA_ROOT + """/assesses.csv'
AS row WITH row 
CALL {
  WITH row
  MATCH (source: `QUESTION` { `id`: toInteger(trim(row.`from_id`)) })
  MATCH (target: `CONTROL` { `id`: toInteger(trim(row.`to_id`)) })
  MERGE (source)-[r: `ASSESSES`]->(target)
  SET r.`from_id` = toInteger(trim(row.`from_id`))
  SET r.`to_id` = toInteger(trim(row.`to_id`))
  SET r.`strength` = toLower(trim(row.`strength`)) IN ['1','true','yes']
} IN TRANSACTIONS OF 10000 ROWS;
"""

