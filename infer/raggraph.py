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
# OPENAI_API_KEY = os.environ.get("OPEN_API_SECRET")

AQ_VECTOR_INDEX_NAME = 'assessment_quest_chunks'
AQ_VECTOR_NODE_LABEL = NodeType.ASESSMENTQ.label
AQ_VECTOR_SOURCE_PROPERTY = 'rationale'
AQ_VECTOR_EMBEDDING_PROPERTY = 'aqtext_embedding'

SOURCE_UPDATE_QUERY = """
    MATCH (n:""" + NodeType.ASESSMENTQ.label + """)
    SET n.source = 'https://www.nist.gov/cyberframework'
    """

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
        self.OPENAI_API_KEY = os.environ.get("OPEN_API_SECRET")
        # Below should be handled in rag prep
        # self.neo4jgraph.query(SOURCE_UPDATE_QUERY)
        # self.neo4jgraph.refresh_schema()
        # print(self.neo4jgraph.schema)

        

    def graph_rag_prep(self):
        '''Initialize the graph for rag flows'''
        self.neo4jgraph.query(VECTOR_INDEXING_QUERY)
        self.neo4jgraph.query(AQ_VECTOR_EMBEDDING_QUERY, params={"openAiApiKey":self.OPENAI_API_KEY} )
        self.neo4jgraph.query(SOURCE_UPDATE_QUERY)
        self.neo4jgraph.refresh_schema()
        print(self.neo4jgraph.schema)
    
    def infer_plain(self, question):
        '''Infer with question no augmentation for LLM'''
        vector_store = Neo4jVector.from_existing_graph(
            embedding=OpenAIEmbeddings(api_key=self.OPENAI_API_KEY),
            url=self.neo4jconnector.getUri(),
            username=self.neo4jconnector.getAuthUser(),
            password=self.neo4jconnector.getAuthPassword(),
            index_name=AQ_VECTOR_INDEX_NAME,
            node_label=AQ_VECTOR_NODE_LABEL,
            text_node_properties=[AQ_VECTOR_SOURCE_PROPERTY],
            embedding_node_property=AQ_VECTOR_EMBEDDING_PROPERTY,
        )
        # Create a retriever from the store
        # Using a k of default for the retriever
        retriever = vector_store.as_retriever(search_kwargs={'k': 9})

        # Create a chatbot Question & Answer chain from the retriever
        plain_chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0,api_key=self.OPENAI_API_KEY), 
            chain_type="stuff", 
            retriever=retriever
        )
    
        
        results = plain_chain(
            {"question": question},
            return_only_outputs=True,
        )

        return results
    

    def infer_rag(self, question):
        '''Infer with question with augmentation for LLM'''

        rationale_retrieval_query = """
        MATCH (node)-[:ASSESSES]->(c:CONTROL),
            (c)-[:CAPTURES]->(keyc:KEYCONCEPT)
        WITH node, c, keyc
        WITH collect (
            "CSF Control " + c.name + 
            " is primarily concerned with the core concept of " + keyc.name + " hence the question: '" + node.name + "' is part of the compliance assessment checks. " + node.rationale 
        ) AS control_context_statements, keyc, node
        RETURN apoc.text.join(control_context_statements, "\n") + 
            "\n" + node.name AS text, node, 0.9 as score,
            { 
            source: node.source
            } as metadata
        """




        vector_store_with_question_rationale = Neo4jVector.from_existing_index(
            embedding=OpenAIEmbeddings(api_key=self.OPENAI_API_KEY),
            url=self.neo4jconnector.getUri(),
            username=self.neo4jconnector.getAuthUser(),
            password=self.neo4jconnector.getAuthPassword(),
            database="neo4j",
            index_name=AQ_VECTOR_INDEX_NAME,
            node_label=AQ_VECTOR_NODE_LABEL,
            retrieval_query=rationale_retrieval_query,
        )

        # Create a retriever from the vector store
        retriever_with_rationale = vector_store_with_question_rationale.as_retriever(search_kwargs={'k': 9})

        # Create a chatbot Question & Answer chain from the retriever
        rag_chain = RetrievalQAWithSourcesChain.from_chain_type(
            ChatOpenAI(temperature=0, api_key=self.OPENAI_API_KEY), 
            chain_type="stuff", 
            retriever=retriever_with_rationale
        )

        results = rag_chain(
            {"question": question},
            return_only_outputs=True,
        )
        return results
    
    
