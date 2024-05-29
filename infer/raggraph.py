''' This module contains a demo class for graph inference & RAG functionalities leveraging LanguageChain'''

import os
from connector.graphdb import NEO4JConnector
from kgmodel.kgtypes import NodeType

from langchain_community.graphs import Neo4jGraph
from langchain_community.vectorstores import Neo4jVector
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import RetrievalQAWithSourcesChain
from langchain_openai import ChatOpenAI

# LLM/Embedding constants
OPENAI_API_KEY = os.environ.get("OPEN_API_SECRET")

AQ_VECTOR_INDEX_NAME = 'assessment_quest_chunks'
AQ_VECTOR_NODE_LABEL = NodeType.ASESSMENTQ.label
AQ_VECTOR_SOURCE_PROPERTY = 'rationale'
AQ_VECTOR_EMBEDDING_PROPERTY = 'aqtext_embedding'

VECTOR_INDEXING_QUERY ="""
    CREATE VECTOR INDEX `""" + AQ_VECTOR_INDEX_NAME + """` IF NOT EXISTS
    FOR (c:""" + AQ_VECTOR_NODE_LABEL + """) ON (c.""" + AQ_VECTOR_EMBEDDING_PROPERTY + """) 
    OPTIONS { indexConfig: {
    `vector.dimensions`: 1536,
    `vector.similarity_function`: 'cosine'    
    }}
"""
AQ_VECTOR_EMBEDDING_QUERY ="""
    MATCH (aq:""" + AQ_VECTOR_NODE_LABEL + """) WHERE aq.""" + AQ_VECTOR_EMBEDDING_PROPERTY + """ IS NULL
    WITH aq, genai.vector.encode(
      aq.""" + AQ_VECTOR_SOURCE_PROPERTY + """,     
      "OpenAI", 
      {
        token: $openAiApiKey
      }) AS vector
    CALL db.create.setNodeVectorProperty(aq, '""" + AQ_VECTOR_EMBEDDING_PROPERTY + """', vector)
"""

class GraphInference:
    '''Graph Inference class'''
    def __init__(self):
        '''Initialize RAG inference class'''
        self.neo4jconnector = NEO4JConnector()
        '''Initialize the Neo4j graph via LangChain'''
        self.neo4jgraph = Neo4jGraph(url=self.neo4jconnector.getUri()
                                     , username=self.neo4jconnector.getAuthUser()
                                     , password=self.neo4jconnector.getAuthPassword())

    def graph_rag_prep(self):
        '''Initialize the graph for rag flows'''
        self.neo4jgraph.query(VECTOR_INDEXING_QUERY)
        self.neo4jgraph.query(AQ_VECTOR_EMBEDDING_QUERY, params={"openAiApiKey":OPENAI_API_KEY} )
        self.neo4jgraph.refresh_schema()
        print(self.neo4jgraph.schema)

    def infer(self, question, context):
        '''Infer RAG question and context'''
        return self.retrievalqa.infer(question, context)
    